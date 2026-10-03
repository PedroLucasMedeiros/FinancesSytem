# Documentação do projeto Financas System

## Resumo
O propósito do projeto é um sistema Web feito com uma API RESTful para gestão de ganhos mensais.
O intuito é facilitar o controle financeiro dos usuários de forma que registre:

- **Fontes de Renda:** Entrada
- **Planos:** Saída
- **Saldo do Mês:** Dado
- **Orçamentos para o Mês X:**

    - **Cabeçalho:** Pessoa que vai destinar a verba | Valor destinado para o orçamento daquele mês

        - **Reserva:** Porcentagem da entrada dedicada à ação | Valor da porcentagem
        - **Contas:** Porcentagem da entrada dedicada à ação | Valor da porcentagem
        - **Pessoal:** Porcentagem da entrada dedicada à ação | Valor da porcentagem
        - **Mercado:** Porcentagem da entrada dedicada à ação | Valor da porcentagem

    - **Soma das Pessoas Ativas:**

        - **Reserva:** Valor
        - **Pessoal:** Valor
        - **Mercado:** Valor

- **Lançamentos do Mês X** (Normalmente operações cadastradas no cartão):
    - **Card de Lançamento:** Nome dado ao Lançamento | Data | Categoria do tipo de lançamento | Pessoa que recebe | Despesa ou Receita | Valor

- **Dashboard:**
    - **Gráfico Pizza:** Gastos por Categoria
    - **Gráfico em Barra:** Entradas e Gastos - Mês X

- **Formulário / Card de Metas:**
    - **Qual é a Meta:** Valor da Meta | Valor que temos na Reserva