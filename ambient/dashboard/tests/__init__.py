from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase

PASSWORD = "SenhaForte!2026"


class FinanceE2ETests(APITestCase):
    """Fluxo completo: cadastro -> login -> uso autenticado -> isolamento -> logout."""

    def setUp(self):
        # O throttle usa o cache; limpar evita 429 entre testes
        cache.clear()

    # ---------- helpers ----------
    def register(self, email, first_name="Maria", last_name="Silva"):
        return self.client.post(
            "/api/auth/register/",
            {"email": email, "first_name": first_name, "last_name": last_name, "password": PASSWORD},
            format="json",
        )

    def login(self, email):
        response = self.client.post(
            "/api/token/", {"email": email, "password": PASSWORD}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data  # {"access": ..., "refresh": ...}

    def authenticate(self, access_token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def create_user_session(self, email):
        """Cadastra, faz login, autentica o client e devolve (tokens, person_id)."""
        self.assertEqual(self.register(email).status_code, status.HTTP_201_CREATED)
        tokens = self.login(email)
        self.authenticate(tokens["access"])
        people = self.client.get("/api/dashboard/people/")
        return tokens, people.data["results"][0]["id"]

    # ---------- testes ----------
    def test_rotas_protegidas_exigem_token(self):
        for url in ("/api/auth/me/", "/api/dashboard/transactions/", "/api/dashboard/goals/"):
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, url)

    def test_fluxo_completo_do_usuario(self):
        # 1. Cadastro cria usuário + Person
        _, person_id = self.create_user_session("maria@exemplo.com")

        # 2. /me devolve o usuário do token
        me = self.client.get("/api/auth/me/")
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data["email"], "maria@exemplo.com")

        # 3. Cria um lançamento
        created = self.client.post(
            "/api/dashboard/transactions/",
            {
                "person": person_id,
                "transaction_title": "Salário",
                "transaction_date": "2026-10-05",
                "transaction_type": "INCOME",
                "transaction_amount": "5000.00",
            },
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED, created.data)
        transaction_id = created.data["id"]

        # 4. Lista e detalha
        listing = self.client.get("/api/dashboard/transactions/")
        self.assertEqual(listing.data["count"], 1)
        detail = self.client.get(f"/api/dashboard/transactions/{transaction_id}/")
        self.assertEqual(detail.data["transaction_title"], "Salário")

        # 5. Atualiza parcialmente
        patched = self.client.patch(
            f"/api/dashboard/transactions/{transaction_id}/",
            {"transaction_title": "Salário outubro"},
            format="json",
        )
        self.assertEqual(patched.status_code, status.HTTP_200_OK)

        # 6. Exclui (soft delete) e confirma que some da API
        deleted = self.client.delete(f"/api/dashboard/transactions/{transaction_id}/")
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.get("/api/dashboard/transactions/").data["count"], 0)
        self.assertEqual(
            self.client.get(f"/api/dashboard/transactions/{transaction_id}/").status_code,
            status.HTTP_404_NOT_FOUND,
        )

        # 7. O registro continua no banco, com deleted_at preenchido
        from dashboard.models import FinancialTransaction
        row = FinancialTransaction.all_objects.get(pk=transaction_id)
        self.assertIsNotNone(row.deleted_at)

    def test_validacoes_de_negocio(self):
        _, person_id = self.create_user_session("maria@exemplo.com")

        invalid_amount = self.client.post(
            "/api/dashboard/transactions/",
            {"person": person_id, "transaction_title": "X", "transaction_date": "2026-10-05",
             "transaction_type": "EXPENSE", "transaction_amount": "-10"},
            format="json",
        )
        self.assertEqual(invalid_amount.status_code, status.HTTP_400_BAD_REQUEST)

        invalid_percentage = self.client.post(
            "/api/dashboard/budgets/",
            {"person": person_id, "budget_title": "Lazer", "granted_amount": "1000",
             "allocated_percentage": "150"},
            format="json",
        )
        self.assertEqual(invalid_percentage.status_code, status.HTTP_400_BAD_REQUEST)

    def test_isolamento_entre_usuarios(self):
        # Usuário A cria um lançamento
        _, person_a = self.create_user_session("a@exemplo.com")
        transaction_a = self.client.post(
            "/api/dashboard/transactions/",
            {"person": person_a, "transaction_title": "Do A", "transaction_date": "2026-10-05",
             "transaction_type": "INCOME", "transaction_amount": "100.00"},
            format="json",
        ).data["id"]

        # Usuário B entra no sistema
        self.client.credentials()  # remove o token do A
        _, person_b = self.create_user_session("b@exemplo.com")

        # B não vê, não lê e não altera o que é do A
        self.assertEqual(self.client.get("/api/dashboard/transactions/").data["count"], 0)
        self.assertEqual(
            self.client.get(f"/api/dashboard/transactions/{transaction_a}/").status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            self.client.delete(f"/api/dashboard/transactions/{transaction_a}/").status_code,
            status.HTTP_404_NOT_FOUND,
        )

        # B também não consegue criar dados na Person do A
        forged = self.client.post(
            "/api/dashboard/transactions/",
            {"person": person_a, "transaction_title": "Invasão", "transaction_date": "2026-10-05",
             "transaction_type": "EXPENSE", "transaction_amount": "1.00"},
            format="json",
        )
        self.assertEqual(forged.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refresh_e_logout(self):
        self.register("maria@exemplo.com")
        tokens = self.login("maria@exemplo.com")
        self.authenticate(tokens["access"])

        # Renova o access token
        refreshed = self.client.post("/api/token/refresh/", {"refresh": tokens["refresh"]}, format="json")
        self.assertEqual(refreshed.status_code, status.HTTP_200_OK)
        new_refresh = refreshed.data["refresh"]  # rotação ativa: vem um novo refresh

        # Logout coloca o refresh na blacklist
        logout = self.client.post("/api/auth/logout/", {"refresh": new_refresh}, format="json")
        self.assertEqual(logout.status_code, status.HTTP_201_CREATED)

        # O refresh invalidado não renova mais
        reused = self.client.post("/api/token/refresh/", {"refresh": new_refresh}, format="json")
        self.assertEqual(reused.status_code, status.HTTP_401_UNAUTHORIZED)