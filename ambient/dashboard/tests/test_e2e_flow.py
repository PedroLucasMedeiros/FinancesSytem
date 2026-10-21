from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase

PASSWORD = "SenhaForte!2026"


class FinanceE2ETests(APITestCase):
    """Fluxo completo: cadastro -> login -> uso autenticado -> isolamento -> logout."""

    def setUp(self):
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
        return response.data

    def authenticate(self, access_token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def create_user_session(self, email):
        """Cadastra, faz login, autentica o client e devolve (tokens, person_id)."""
        print(f"\n   [Setup] Criando sessão e autenticando para: {email}...")
        self.assertEqual(self.register(email).status_code, status.HTTP_201_CREATED)
        tokens = self.login(email)
        self.authenticate(tokens["access"])
        people = self.client.get("/api/dashboard/people/")
        return tokens, people.data["results"][0]["id"]

    # ---------- testes ----------
    def test_rotas_protegidas_exigem_token(self):
        print("\n>>> Executando: Validação de Proteção de Rotas (401)")
        for url in ("/api/auth/me/", "/api/dashboard/transactions/", "/api/dashboard/goals/"):
            print(f"    -> Testando acesso anônimo em: {url}")
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, url)

    def test_fluxo_completo_do_usuario(self):
        print("\n>>> Executando: Fluxo Completo E2E do Usuário")

        print("  1. Cadastrando e autenticando 'maria@exemplo.com'")
        _, person_id = self.create_user_session("maria@exemplo.com")

        print("  2. Validando endpoint /api/auth/me/")
        me = self.client.get("/api/auth/me/")
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data["email"], "maria@exemplo.com")

        print("  3. Criando nova transação (Salário)")
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

        print(f"  4. Listando e detalhando a transação #{transaction_id}")
        listing = self.client.get("/api/dashboard/transactions/")
        self.assertEqual(listing.data["count"], 1)
        detail = self.client.get(f"/api/dashboard/transactions/{transaction_id}/")
        self.assertEqual(detail.data["transaction_title"], "Salário")

        print(f"  5. Atualizando parcialmente a transação #{transaction_id} via PATCH")
        patched = self.client.patch(
            f"/api/dashboard/transactions/{transaction_id}/",
            {"transaction_title": "Salário outubro"},
            format="json",
        )
        self.assertEqual(patched.status_code, status.HTTP_200_OK)

        print(f"  6. Executando Soft Delete na transação #{transaction_id}")
        deleted = self.client.delete(f"/api/dashboard/transactions/{transaction_id}/")
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.get("/api/dashboard/transactions/").data["count"], 0)
        self.assertEqual(
            self.client.get(f"/api/dashboard/transactions/{transaction_id}/").status_code,
            status.HTTP_404_NOT_FOUND,
        )

        print("  7. Verificando persistence no banco de dados com 'deleted_at'")
        from dashboard.models import FinancialTransaction
        row = FinancialTransaction.all_objects.get(pk=transaction_id)
        self.assertIsNotNone(row.deleted_at)

    def test_validacoes_de_negocio(self):
        print("\n>>> Executando: Teste de Validações de Regra de Negócio")
        _, person_id = self.create_user_session("maria@exemplo.com")

        print("  -> Tentando criar transação com valor negativo (Esperado: 400 Bad Request)")
        invalid_amount = self.client.post(
            "/api/dashboard/transactions/",
            {"person": person_id, "transaction_title": "X", "transaction_date": "2026-10-05",
             "transaction_type": "EXPENSE", "transaction_amount": "-10"},
            format="json",
        )
        self.assertEqual(invalid_amount.status_code, status.HTTP_400_BAD_REQUEST)

        print("  -> Tentando definir porcentagem de orçamento acima de 100% (Esperado: 400 Bad Request)")
        invalid_percentage = self.client.post(
            "/api/dashboard/budgets/",
            {"person": person_id, "budget_title": "Lazer", "granted_amount": "1000",
             "allocated_percentage": "150"},
            format="json",
        )
        self.assertEqual(invalid_percentage.status_code, status.HTTP_400_BAD_REQUEST)

    def test_isolamento_entre_usuarios(self):
        print("\n>>> Executando: Isolamento de Dados (Multi-tenant) entre Usuários")

        print("  1. Usuário A cria um lançamento")
        _, person_a = self.create_user_session("a@exemplo.com")
        transaction_a = self.client.post(
            "/api/dashboard/transactions/",
            {"person": person_a, "transaction_title": "Do A", "transaction_date": "2026-10-05",
             "transaction_type": "INCOME", "transaction_amount": "100.00"},
            format="json",
        ).data["id"]

        print("  2. Trocando para o Usuário B")
        self.client.credentials()  # Limpa o token do Usuário A
        _, person_b = self.create_user_session("b@exemplo.com")

        print("  3. Garantindo que B não lê nem exclui dados do Usuário A")
        self.assertEqual(self.client.get("/api/dashboard/transactions/").data["count"], 0)
        self.assertEqual(
            self.client.get(f"/api/dashboard/transactions/{transaction_a}/").status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            self.client.delete(f"/api/dashboard/transactions/{transaction_a}/").status_code,
            status.HTTP_404_NOT_FOUND,
        )

        print("  4. Garantindo que B não pode forçar criação associando à Person do A")
        forged = self.client.post(
            "/api/dashboard/transactions/",
            {"person": person_a, "transaction_title": "Invasão", "transaction_date": "2026-10-05",
             "transaction_type": "EXPENSE", "transaction_amount": "1.00"},
            format="json",
        )
        self.assertEqual(forged.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refresh_e_logout(self):
        print("\n>>> Executando: Fluxo de Autenticação JWT (Refresh Token & Logout)")

        print("  1. Registrando, logando e autenticando")
        self.register("maria@exemplo.com")
        tokens = self.login("maria@exemplo.com")
        self.authenticate(tokens["access"])

        print("  2. Renovando access token via refresh token")
        refreshed = self.client.post("/api/token/refresh/", {"refresh": tokens["refresh"]}, format="json")
        self.assertEqual(refreshed.status_code, status.HTTP_200_OK)
        new_refresh = refreshed.data["refresh"]

        print("  3. Realizando logout e adicionando refresh token na blacklist")
        logout = self.client.post("/api/auth/logout/", {"refresh": new_refresh}, format="json")
        self.assertEqual(logout.status_code, status.HTTP_201_CREATED)

        print("  4. Tentando reusar o token invalidado (Esperado: 401 Unauthorized)")
        reused = self.client.post("/api/token/refresh/", {"refresh": new_refresh}, format="json")
        self.assertEqual(reused.status_code, status.HTTP_401_UNAUTHORIZED)