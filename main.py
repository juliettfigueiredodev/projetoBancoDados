"""
main.py
Ponto de entrada do projeto.
Demonstra todas as operações CRUD e consultas com relacionamento.
"""

from database import get_session
from crud.crud import (
    criar_hospede, criar_quarto, criar_reserva, criar_pagamento,
    listar_hospedes, listar_quartos_disponiveis, listar_reservas,
    atualizar_status_quarto, atualizar_email_hospede,
    deletar_pagamento, deletar_hospede
)
from queries.queries import (
    reservas_ativas_com_detalhes,
    total_pago_por_reserva,
    hospedes_brasileiros_com_reservas_ativas,
    quartos_com_manutencao,
    quartos_disponiveis_baratos
)
from datetime import date

LINHA = "=" * 60


def secao(titulo: str):
    print(f"\n{LINHA}")
    print(f"  {titulo}")
    print(LINHA)


# ============================================================
# BLOCO 1 — CREATE (Inserções)
# ============================================================
def demo_create(session):
    secao("CREATE — Inserindo novos registros")

    # 3 hóspedes novos
    print("\n[1] Inserindo 3 hóspedes:")
    h1 = criar_hospede(session,
        nome="Lucas Ferreira", tipo_documento="CPF",
        valor_documento="111.222.333-44",
        email="lucas.ferreira@email.com", telefone="(85) 91111-2222")

    h2 = criar_hospede(session,
        nome="Fernanda Lima", tipo_documento="CPF",
        valor_documento="555.666.777-88",
        email="fernanda.lima@email.com", telefone="(85) 93333-4444")

    h3 = criar_hospede(session,
        nome="James Cooper", tipo_documento="PASSAPORTE",
        valor_documento="GB1122334",
        email="james.cooper@email.com", telefone="+44 7911 112233")

    # 1 quarto novo disponível
    print("\n[2] Inserindo 1 quarto disponível:")
    q = criar_quarto(session,
        numero=401, tipo="LUXO",
        capacidade=4, tarifa=600.00, status="DISPONIVEL")

    # 1 reserva no quarto 401
    print("\n[3] Inserindo 1 reserva:")
    r = criar_reserva(session,
        data_entrada=date(2026, 4, 1),
        data_saida=date(2026, 4, 7),
        nro_hospedes=2,
        origem="site",
        id_hospede=h1.id,
        numero_quarto=401)

    # 1 pagamento para a reserva criada
    print("\n[4] Inserindo 1 pagamento:")
    criar_pagamento(session,
        data=date(2026, 3, 15),
        forma="pix",
        valor=1200.00,
        id_reserva=r.id)

    return h1, h2, h3, q, r


# ============================================================
# BLOCO 2 — READ (Listagens com paginação e ordenação)
# ============================================================
def demo_read(session):
    secao("READ — Listando registros")

    print("\n[1] Hóspedes (página 1, 15 por página):")
    for h in listar_hospedes(session, pagina=1, por_pagina=15):
        print(f"   - {h.nome} | {h.tipo_documento}: {h.valor_documento}")

    print("\n[2] Quartos disponíveis (ordenados por tarifa):")
    for q in listar_quartos_disponiveis(session):
        print(f"   - Quarto {q.numero} | {q.tipo} | R$ {q.tarifa_base_diaria}")

    print("\n[3] Reservas (página 1, 15 por página):")
    for r in listar_reservas(session, pagina=1, por_pagina=15):
        print(f"   - Reserva #{r.id} | Entrada: {r.data_entrada} | Saída: {r.data_saida}")


# ============================================================
# BLOCO 3 — UPDATE (Atualizações)
# ============================================================
def demo_update(session):
    secao("UPDATE — Atualizando registros")

    print("\n[1] Atualizando status do quarto 401 para OCUPADO:")
    atualizar_status_quarto(session, numero_quarto=401, novo_status="OCUPADO")

    print("\n[2] Atualizando e-mail do hóspede ID 1:")
    atualizar_email_hospede(session, id_hospede=1, novo_email="joao.silva.novo@email.com")


# ============================================================
# BLOCO 4 — DELETE (Remoções)
# ============================================================
def demo_delete(session, hospede_sem_reserva, pagamento_id=None):
    secao("DELETE — Removendo registros")

    # Deleta hóspede que não tem reserva (criado na demo_create)
    print(f"\n[1] Tentando remover hóspede sem reservas (ID {hospede_sem_reserva.id}):")
    deletar_hospede(session, id_hospede=hospede_sem_reserva.id)

    # Tenta remover hóspede com reservas (deve falhar por integridade)
    print("\n[2] Tentando remover hóspede COM reservas (ID 1 — deve falhar):")
    deletar_hospede(session, id_hospede=1)


# ============================================================
# BLOCO 5 — CONSULTAS COM RELACIONAMENTO
# ============================================================
def demo_queries(session):
    secao("CONSULTA 1 — Reservas ativas (JOIN: Reserva + Hóspede + Quarto)")
    resultados = reservas_ativas_com_detalhes(session)
    if resultados:
        for r in resultados:
            print(f"   Reserva #{r.id_reserva} | {r.nome_hospede} | "
                  f"Quarto {r.numero_quarto} ({r.tipo_quarto}) | "
                  f"{r.data_entrada} → {r.data_saida}")
    else:
        print("   Nenhuma reserva ativa encontrada.")

    secao("CONSULTA 2 — Total pago por reserva (JOIN + SUM/COUNT)")
    resultados = total_pago_por_reserva(session)
    if resultados:
        for r in resultados:
            print(f"   Reserva #{r.id_reserva} | {r.nome_hospede} | "
                  f"Pagamentos: {r.qtd_pagamentos} | "
                  f"Total: R$ {r.valor_total_pago}")
    else:
        print("   Nenhum pagamento encontrado.")

    secao("CONSULTA 3 — Hóspedes brasileiros com reservas ativas (FILTRO + ORDENAÇÃO)")
    resultados = hospedes_brasileiros_com_reservas_ativas(session)
    if resultados:
        for r in resultados:
            print(f"   {r.nome_hospede} | CPF: {r.cpf} | "
                  f"Quarto {r.numero_quarto} | {r.data_entrada} → {r.data_saida}")
    else:
        print("   Nenhum resultado encontrado.")

    secao("CONSULTA 4 — Quartos com/sem manutenção (LEFT JOIN)")
    resultados = quartos_com_manutencao(session)
    for r in resultados:
        manut = r.motivo if r.motivo else "Sem manutenção"
        print(f"   Quarto {r.numero_quarto} | {r.tipo} | {r.status} | {manut}")

    secao("CONSULTA 5 — Quartos disponíveis abaixo de R$ 300 (FILTRO + ORDENAÇÃO)")
    resultados = quartos_disponiveis_baratos(session, limite_tarifa=300.0)
    if resultados:
        for q in resultados:
            print(f"   Quarto {q.numero} | {q.tipo} | "
                  f"Capacidade: {q.capacidade} | R$ {q.tarifa_base_diaria}")
    else:
        print("   Nenhum quarto encontrado.")


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================
if __name__ == "__main__":
    print("\n" + LINHA)
    print("  SISTEMA HOTEL — Demonstração ORM com SQLAlchemy")
    print(LINHA)

    session = get_session()

    try:
        h1, h2, h3, q, r = demo_create(session)
        demo_read(session)
        demo_update(session)
        demo_delete(session, hospede_sem_reserva=h3)
        demo_queries(session)

    except Exception as e:
        print(f"\n  ERRO: {e}")
        session.rollback()

    finally:
        session.close()
        print(f"\n{LINHA}")
        print("  Sessão encerrada. Demonstração concluída!")
        print(LINHA)
