"""
crud_demo.py — Demonstração completa de CRUD + Consultas com SQLAlchemy ORM
═══════════════════════════════════════════════════════════════════════════════

COBERTURA DO SCRIPT
───────────────────
CRUD
  [CREATE] Inserção de 3+ registros em entidade principal (Hospede + Quarto + Reserva)
  [READ]   Listagem com paginação simples e ordenação
  [UPDATE] Atualização de registros (status, tarifa, email)
  [DELETE] Remoção com respeito à integridade referencial

CONSULTAS ORM (3 obrigatórias)
  [Q1] JOIN — Reservas ativas com dados do hóspede e do quarto
  [Q2] JOIN + AGREGAÇÃO — Total pago e número de pagamentos por reserva
  [Q3] FILTRO + ORDENAÇÃO — Quartos disponíveis ordenados por tarifa (top 5)

EXECUÇÃO
  python crud_demo.py
"""

import sys
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# ── Importações internas do projeto ───────────────────────────────────────────
from config import DB_CONFIG
from database import Database
from models import Hospede, Quarto, QuartoManutencao, Reserva, Pagamento

# ── Helpers de saída ──────────────────────────────────────────────────────────

SEP = "─" * 68
SEP2 = "═" * 68

def titulo(texto: str):
    print(f"\n{SEP2}")
    print(f"  {texto}")
    print(SEP2)

def secao(texto: str):
    print(f"\n{SEP}")
    print(f"  {texto}")
    print(SEP)

def ok(msg: str):
    print(f"  ✓  {msg}")

def info(msg: str):
    print(f"  ·  {msg}")

def erro(msg: str):
    print(f"  ✗  {msg}")

def linha():
    print(f"  {'-' * 60}")


# ══════════════════════════════════════════════════════════════════════════════
#  CREATE — Inserção de registros usando ORM
# ══════════════════════════════════════════════════════════════════════════════

def demo_create(db: Database):
    titulo("CREATE — Inserção de registros")

    # ── 1. Inserção de 3 hóspedes ──────────────────────────────────────────
    secao("1.1 · Inserindo 3 novos hóspedes")

    novos_hospedes = [
        Hospede(
            nome="Lúcia Ferreira Braga",
            tipo_documento="CPF",
            valor_documento="741.852.963-11",
            email="lucia.braga@email.com",
            telefone="(85) 99100-2233",
        ),
        Hospede(
            nome="James Mitchell",
            tipo_documento="PASSAPORTE",
            valor_documento="US8765432",
            email="james.mitchell@email.com",
            telefone="+1 202-555-0198",
        ),
        Hospede(
            nome="Fernanda Castelo Melo",
            tipo_documento="CPF",
            valor_documento="159.357.486-22",
            email="fernanda.melo@email.com",
            telefone="(88) 98877-6655",
        ),
    ]

    ids_hospedes = []
    with db.get_session() as s:
        for h in novos_hospedes:
            s.add(h)
        s.flush()  # envia ao BD sem commitar — obtemos os IDs gerados
        for h in novos_hospedes:
            ids_hospedes.append(h.id)
            ok(f"Hóspede inserido → id={h.id}  nome='{h.nome}'  doc={h.tipo_documento}")

    # ── 2. Inserção de 2 quartos ───────────────────────────────────────────
    secao("1.2 · Inserindo 2 novos quartos")

    novos_quartos = [
        Quarto(numero=401, tipo="LUXO",   capacidade=3, tarifa_base_diaria=450.00, status="DISPONIVEL"),
        Quarto(numero=105, tipo="SIMPLES", capacidade=1, tarifa_base_diaria=120.00, status="DISPONIVEL"),
    ]

    with db.get_session() as s:
        for q in novos_quartos:
            s.add(q)
        ok(f"Quarto inserido → numero=401  tipo=LUXO     tarifa=R$ 450,00")
        ok(f"Quarto inserido → numero=105  tipo=SIMPLES  tarifa=R$ 120,00")

    # ── 3. Inserção de 2 reservas para os novos hóspedes ──────────────────
    secao("1.3 · Inserindo 2 reservas usando os hóspedes criados acima")

    id_lucia, id_james, _ = ids_hospedes
    hoje = date.today()

    novas_reservas = [
        Reserva(
            data_entrada=hoje + timedelta(days=5),
            data_saida=hoje + timedelta(days=10),
            nro_hospedes=1,
            origem="site",
            id_hospede=id_lucia,
            numero_quarto=105,   # quarto recém inserido
        ),
        Reserva(
            data_entrada=hoje + timedelta(days=3),
            data_saida=hoje + timedelta(days=8),
            nro_hospedes=2,
            origem="telefone",
            id_hospede=id_james,
            numero_quarto=401,   # quarto recém inserido
        ),
    ]

    ids_reservas = []
    with db.get_session() as s:
        for r in novas_reservas:
            s.add(r)
        s.flush()
        for r in novas_reservas:
            ids_reservas.append(r.id)
            ok(f"Reserva inserida  → id={r.id}  "
               f"hóspede_id={r.id_hospede}  quarto={r.numero_quarto}  "
               f"entrada={r.data_entrada}  saída={r.data_saida}")

    # ── 4. Inserção de pagamento para a primeira reserva ──────────────────
    secao("1.4 · Inserindo 1 pagamento para a reserva recém criada")

    id_reserva_lucia = ids_reservas[0]
    with db.get_session() as s:
        pag = Pagamento(
            data=date.today(),
            forma="pix",
            valor=300.00,
            id_reserva=id_reserva_lucia,
        )
        s.add(pag)
        s.flush()
        ok(f"Pagamento inserido → id={pag.id}  forma=pix  "
           f"valor=R$ 300,00  reserva_id={pag.id_reserva}")

    # ── 5. Tentativa de inserção duplicada (e-mail já existente) ──────────
    secao("1.5 · Tentativa de duplicata (deve ser rejeitada)")
    try:
        with db.get_session() as s:
            duplicado = Hospede(
                nome="Qualquer Nome",
                tipo_documento="CPF",
                valor_documento="000.000.000-00",
                email="lucia.braga@email.com",   # e-mail já cadastrado
                telefone="(00) 00000-0000",
            )
            s.add(duplicado)
    except IntegrityError:
        ok("IntegrityError capturado corretamente — e-mail duplicado rejeitado.")

    return ids_hospedes, ids_reservas


# ══════════════════════════════════════════════════════════════════════════════
#  READ — Listagem com paginação e ordenação
# ══════════════════════════════════════════════════════════════════════════════

def demo_read(db: Database):
    titulo("READ — Listagem com paginação e ordenação")

    # ── 1. Todos os hóspedes, ordenados pelo nome, com paginação ──────────
    secao("2.1 · Hóspedes ordenados por nome — página 1 (3 por página)")

    PAGE_SIZE = 3
    PAGE      = 1  # página 1 (base 1)

    with db.get_session() as s:
        query = (
            s.query(Hospede)
             .order_by(Hospede.nome)          # ORDER BY nome ASC
             .offset((PAGE - 1) * PAGE_SIZE)  # OFFSET
             .limit(PAGE_SIZE)                # LIMIT
        )
        hospedes_pg1 = query.all()
        total        = s.query(func.count(Hospede.id)).scalar()

        info(f"Total de hóspedes: {total}  |  Página {PAGE}  |  Itens por página: {PAGE_SIZE}")
        linha()
        print(f"  {'ID':<5} {'Nome':<28} {'Tipo Doc':<12} {'E-mail'}")
        linha()
        for h in hospedes_pg1:
            print(f"  {h.id:<5} {h.nome:<28} {h.tipo_documento:<12} {h.email}")

    secao("2.2 · Hóspedes — página 2")
    PAGE = 2
    with db.get_session() as s:
        hospedes_pg2 = (
            s.query(Hospede)
             .order_by(Hospede.nome)
             .offset((PAGE - 1) * PAGE_SIZE)
             .limit(PAGE_SIZE)
             .all()
        )
        info(f"Página {PAGE}  |  {len(hospedes_pg2)} registro(s) retornado(s)")
        linha()
        print(f"  {'ID':<5} {'Nome':<28} {'Tipo Doc':<12} {'E-mail'}")
        linha()
        for h in hospedes_pg2:
            print(f"  {h.id:<5} {h.nome:<28} {h.tipo_documento:<12} {h.email}")

    # ── 2. Quartos ordenados por tarifa decrescente ────────────────────────
    secao("2.3 · Todos os quartos ordenados por tarifa (maior → menor)")
    with db.get_session() as s:
        quartos = (
            s.query(Quarto)
             .order_by(Quarto.tarifa_base_diaria.desc())
             .all()
        )
        linha()
        print(f"  {'Nº':<6} {'Tipo':<10} {'Capac.':<8} {'Tarifa/dia':<14} {'Status'}")
        linha()
        for q in quartos:
            print(f"  {q.numero:<6} {q.tipo:<10} {q.capacidade:<8} "
                  f"R$ {float(q.tarifa_base_diaria):<11.2f} {q.status}")

    # ── 3. Reservas — listagem básica com datas ────────────────────────────
    secao("2.4 · Todas as reservas ordenadas por data de entrada")
    with db.get_session() as s:
        reservas = (
            s.query(Reserva)
             .order_by(Reserva.data_entrada)
             .all()
        )
        linha()
        print(f"  {'ID':<5} {'Hóspede':<25} {'Quarto':<8} {'Entrada':<13} {'Saída':<13} {'Origem'}")
        linha()
        for r in reservas:
            print(f"  {r.id:<5} {r.hospede.nome:<25} {r.numero_quarto:<8} "
                  f"{str(r.data_entrada):<13} {str(r.data_saida):<13} {r.origem}")


# ══════════════════════════════════════════════════════════════════════════════
#  UPDATE — Atualização de registros
# ══════════════════════════════════════════════════════════════════════════════

def demo_update(db: Database, ids_hospedes: list, ids_reservas: list):
    titulo("UPDATE — Atualização de registros")

    id_lucia   = ids_hospedes[0]
    id_reserva = ids_reservas[0]

    # ── 1. Atualizar e-mail e telefone de um hóspede ──────────────────────
    secao("3.1 · Atualizar telefone e e-mail da hóspede Lúcia")
    with db.get_session() as s:
        h = s.get(Hospede, id_lucia)
        info(f"ANTES  →  email='{h.email}'  telefone='{h.telefone}'")

        h.email    = "lucia.braga.novo@email.com"
        h.telefone = "(85) 99200-4455"
        # commit é automático ao sair do bloco — sem UPDATE manual necessário

    with db.get_session() as s:
        h = s.get(Hospede, id_lucia)
        ok(f"DEPOIS →  email='{h.email}'  telefone='{h.telefone}'")

    # ── 2. Atualizar status de um quarto ──────────────────────────────────
    secao("3.2 · Atualizar status do quarto 105: DISPONIVEL → BLOQUEADO")
    with db.get_session() as s:
        q = s.get(Quarto, 105)
        info(f"ANTES  →  quarto={q.numero}  status='{q.status}'")
        q.status = "BLOQUEADO"

    with db.get_session() as s:
        q = s.get(Quarto, 105)
        ok(f"DEPOIS →  quarto={q.numero}  status='{q.status}'")

    # ── 3. Atualizar tarifa de um quarto ──────────────────────────────────
    secao("3.3 · Reajustar tarifa do quarto 401: R$ 450,00 → R$ 520,00")
    with db.get_session() as s:
        q = s.get(Quarto, 401)
        info(f"ANTES  →  quarto={q.numero}  tarifa=R$ {float(q.tarifa_base_diaria):.2f}")
        q.tarifa_base_diaria = 520.00

    with db.get_session() as s:
        q = s.get(Quarto, 401)
        ok(f"DEPOIS →  quarto={q.numero}  tarifa=R$ {float(q.tarifa_base_diaria):.2f}")

    # ── 4. Atualizar nro_hospedes e origem de uma reserva ─────────────────
    secao("3.4 · Atualizar número de hóspedes e origem da reserva recém criada")
    with db.get_session() as s:
        r = s.get(Reserva, id_reserva)
        info(f"ANTES  →  reserva_id={r.id}  nro_hospedes={r.nro_hospedes}  origem='{r.origem}'")
        r.nro_hospedes = 2
        r.origem       = "balcao"

    with db.get_session() as s:
        r = s.get(Reserva, id_reserva)
        ok(f"DEPOIS →  reserva_id={r.id}  nro_hospedes={r.nro_hospedes}  origem='{r.origem}'")

    # ── 5. UPDATE em lote via query ORM ───────────────────────────────────
    secao("3.5 · Reajustar em +10% todos os quartos SIMPLES disponíveis (UPDATE em lote)")
    with db.get_session() as s:
        quartos_simples = (
            s.query(Quarto)
             .filter(Quarto.tipo == "SIMPLES", Quarto.status == "DISPONIVEL")
             .all()
        )
        info(f"{len(quartos_simples)} quarto(s) SIMPLES+DISPONIVEL encontrado(s)")
        for q in quartos_simples:
            tarifa_anterior = float(q.tarifa_base_diaria)
            q.tarifa_base_diaria = round(tarifa_anterior * 1.10, 2)
            ok(f"Quarto {q.numero}: R$ {tarifa_anterior:.2f} → R$ {float(q.tarifa_base_diaria):.2f}")


# ══════════════════════════════════════════════════════════════════════════════
#  DELETE — Remoção com respeito à integridade referencial
# ══════════════════════════════════════════════════════════════════════════════

def demo_delete(db: Database, ids_hospedes: list, ids_reservas: list):
    titulo("DELETE — Remoção com respeito à integridade referencial")

    id_fernanda = ids_hospedes[2]  # hóspede sem reservas
    id_james    = ids_hospedes[1]  # hóspede COM reserva

    # ── 1. Remoção permitida (hóspede sem reservas) ───────────────────────
    secao("4.1 · Remover hóspede SEM reservas (deve ser permitido)")
    with db.get_session() as s:
        h = s.get(Hospede, id_fernanda)
        info(f"Removendo: id={h.id}  nome='{h.nome}'")
        s.delete(h)
    ok(f"Hóspede id={id_fernanda} removido com sucesso.")

    # ── 2. Remoção bloqueada por FK (hóspede COM reservas) ────────────────
    secao("4.2 · Tentativa de remover hóspede COM reservas (deve ser bloqueado pela FK)")
    try:
        with db.get_session() as s:
            h = s.get(Hospede, id_james)
            info(f"Tentando remover: id={h.id}  nome='{h.nome}'  reservas={len(h.reservas)}")
            # Força remoção direta sem cascade — a FK RESTRICT deve bloquear
            s.execute(
                __import__("sqlalchemy").text(
                    "DELETE FROM hospede WHERE id = :id"
                ),
                {"id": id_james}
            )
    except (IntegrityError, SQLAlchemyError):
        ok("IntegrityError capturado — FK RESTRICT bloqueou a exclusão corretamente.")

    # ── 3. Remover pagamento de uma reserva ──────────────────────────────
    secao("4.3 · Remover pagamento vinculado a uma reserva")
    id_reserva_lucia = ids_reservas[0]
    with db.get_session() as s:
        r = s.get(Reserva, id_reserva_lucia)
        if r and r.pagamentos:
            pag = r.pagamentos[0]
            info(f"Removendo pagamento: id={pag.id}  valor=R$ {float(pag.valor):.2f}  forma={pag.forma}")
            s.delete(pag)
            ok(f"Pagamento id={pag.id} removido com sucesso.")
        else:
            info("Nenhum pagamento encontrado para remover.")

    # ── 4. Remoção em cascata via ORM (reserva + pagamentos) ─────────────
    secao("4.4 · Remover reserva de James (cascade remove pagamentos relacionados)")
    id_reserva_james = ids_reservas[1]
    with db.get_session() as s:
        r = s.get(Reserva, id_reserva_james)
        if r:
            info(f"Reserva id={r.id}  hóspede='{r.hospede.nome}'  pagamentos={len(r.pagamentos)}")
            s.delete(r)
            # cascade="all, delete-orphan" apaga os pagamentos filhos automaticamente
            ok(f"Reserva id={r.id} e seus pagamentos removidos via cascade ORM.")

    # ── 5. Limpar quartos inseridos nesta demo ────────────────────────────
    secao("4.5 · Limpar quartos criados nesta demonstração (401 e 105)")
    with db.get_session() as s:
        for num in [401, 105]:
            q = s.get(Quarto, num)
            if q:
                # Antes de deletar, garante que não há reservas ativas
                reservas_ativas = [r for r in q.reservas if r.data_saida >= date.today()]
                if reservas_ativas:
                    info(f"Quarto {num} tem reservas ativas — ignorando remoção.")
                else:
                    s.delete(q)
                    ok(f"Quarto {num} removido.")


# ══════════════════════════════════════════════════════════════════════════════
#  CONSULTAS ORM OBRIGATÓRIAS
# ══════════════════════════════════════════════════════════════════════════════

def demo_consultas(db: Database):
    titulo("CONSULTAS ORM")

    # ─────────────────────────────────────────────────────────────────────────
    # CONSULTA 1 — JOIN
    # Reservas ativas com dados completos do hóspede e do quarto
    # Equivalente: SELECT r.*, h.nome, h.email, q.tipo, q.tarifa_base_diaria
    #              FROM reserva r JOIN hospede h ON ... JOIN quarto q ON ...
    #              WHERE r.data_saida >= CURRENT_DATE
    # ─────────────────────────────────────────────────────────────────────────
    secao("Q1 · JOIN — Reservas ativas com dados do hóspede e do quarto")
    info("Técnica ORM: navegação de relacionamentos (r.hospede, r.quarto)")
    info("Equivalente SQL: SELECT … FROM reserva JOIN hospede JOIN quarto WHERE data_saida >= hoje\n")

    with db.get_session() as s:
        reservas_ativas = (
            s.query(Reserva)
             .join(Reserva.hospede)   # JOIN hospede
             .join(Reserva.quarto)    # JOIN quarto
             .filter(Reserva.data_saida >= date.today())
             .order_by(Reserva.data_entrada)
             .all()
        )

        if not reservas_ativas:
            info("Nenhuma reserva ativa encontrada.")
        else:
            linha()
            print(f"  {'Res.':<5} {'Hóspede':<24} {'Doc':<11} {'Quarto':<8} "
                  f"{'Tipo':<8} {'Tarifa':<12} {'Entrada':<12} {'Saída':<12} {'Diárias'}")
            linha()
            for r in reservas_ativas:
                print(f"  {r.id:<5} {r.hospede.nome:<24} "
                      f"{r.hospede.tipo_documento:<11} "
                      f"{r.quarto.numero:<8} {r.quarto.tipo:<8} "
                      f"R$ {float(r.quarto.tarifa_base_diaria):<9.2f} "
                      f"{str(r.data_entrada):<12} {str(r.data_saida):<12} "
                      f"{r.qtd_diarias} dias")
            linha()
            print(f"\n  Total de reservas ativas: {len(reservas_ativas)}")

    # ─────────────────────────────────────────────────────────────────────────
    # CONSULTA 2 — JOIN + AGREGAÇÃO
    # Total pago, número de pagamentos e saldo restante por reserva
    # Equivalente: SELECT r.id, h.nome, COUNT(p.id), SUM(p.valor), …
    #              FROM reserva r JOIN hospede h JOIN pagamento p
    #              GROUP BY r.id ORDER BY SUM(p.valor) DESC
    # ─────────────────────────────────────────────────────────────────────────
    secao("Q2 · JOIN + AGREGAÇÃO — Total pago e contagem de pagamentos por reserva")
    info("Técnica ORM: func.count(), func.sum(), .join(), .group_by(), .label()")
    info("Equivalente SQL: SELECT r.id, h.nome, COUNT(p.id), SUM(p.valor) … GROUP BY r.id\n")

    with db.get_session() as s:
        resultados = (
            s.query(
                Reserva.id.label("reserva_id"),
                Hospede.nome.label("hospede"),
                Quarto.numero.label("quarto"),
                Quarto.tipo.label("tipo_quarto"),
                func.count(Pagamento.id).label("qtd_pagamentos"),
                func.coalesce(func.sum(Pagamento.valor), 0).label("total_pago"),
                Reserva.data_entrada,
                Reserva.data_saida,
            )
            .join(Reserva.hospede)                               # JOIN hospede
            .join(Reserva.quarto)                                # JOIN quarto
            .outerjoin(Reserva.pagamentos)                       # LEFT JOIN pagamento
            .group_by(
                Reserva.id, Hospede.nome,
                Quarto.numero, Quarto.tipo,
                Reserva.data_entrada, Reserva.data_saida
            )
            .order_by(func.sum(Pagamento.valor).desc().nullslast())
            .all()
        )

        if not resultados:
            info("Nenhuma reserva encontrada.")
        else:
            linha()
            print(f"  {'ID':<5} {'Hóspede':<24} {'Qto':<5} {'Tipo':<8} "
                  f"{'Pgtos':<7} {'Total Pago':<14} {'Entrada':<12} {'Saída'}")
            linha()
            for row in resultados:
                print(f"  {row.reserva_id:<5} {row.hospede:<24} "
                      f"{row.quarto:<5} {row.tipo_quarto:<8} "
                      f"{row.qtd_pagamentos:<7} "
                      f"R$ {float(row.total_pago):<11.2f} "
                      f"{str(row.data_entrada):<12} {row.data_saida}")
            linha()

            # Totais agregados
            total_geral       = sum(float(r.total_pago) for r in resultados)
            total_pagamentos  = sum(r.qtd_pagamentos for r in resultados)
            print(f"\n  Reservas analisadas : {len(resultados)}")
            print(f"  Total de pagamentos : {total_pagamentos}")
            print(f"  Receita total       : R$ {total_geral:.2f}")

    # ─────────────────────────────────────────────────────────────────────────
    # CONSULTA 3 — FILTRO + ORDENAÇÃO
    # Top 5 quartos disponíveis com menor tarifa (mais baratos disponíveis)
    # Equivalente: SELECT * FROM quarto
    #              WHERE status = 'DISPONIVEL' AND tarifa_base_diaria < 300
    #              ORDER BY tarifa_base_diaria ASC LIMIT 5
    # ─────────────────────────────────────────────────────────────────────────
    secao("Q3 · FILTRO + ORDENAÇÃO — Top 5 quartos disponíveis com menor tarifa")
    info("Técnica ORM: .filter() composto, .order_by(), .limit()")
    info("Equivalente SQL: SELECT … FROM quarto WHERE status='DISPONIVEL' ORDER BY tarifa ASC LIMIT 5\n")

    with db.get_session() as s:
        top5 = (
            s.query(Quarto)
             .filter(
                 Quarto.status == "DISPONIVEL",       # filtro 1: apenas disponíveis
                 Quarto.tarifa_base_diaria < 300.00   # filtro 2: tarifa < R$ 300
             )
             .order_by(Quarto.tarifa_base_diaria.asc())  # mais barato primeiro
             .limit(5)
             .all()
        )

        if not top5:
            info("Nenhum quarto disponível com tarifa < R$ 300.")
        else:
            linha()
            print(f"  {'#':<4} {'Quarto':<8} {'Tipo':<10} {'Capac.':<8} "
                  f"{'Tarifa/dia':<14} {'Status'}")
            linha()
            for i, q in enumerate(top5, start=1):
                print(f"  {i:<4} {q.numero:<8} {q.tipo:<10} {q.capacidade:<8} "
                      f"R$ {float(q.tarifa_base_diaria):<11.2f} {q.status}")
            linha()
            menor = float(top5[0].tarifa_base_diaria)
            maior = float(top5[-1].tarifa_base_diaria)
            print(f"\n  Faixa de tarifa nesse resultado: R$ {menor:.2f} → R$ {maior:.2f}")


# ══════════════════════════════════════════════════════════════════════════════
#  PONTO DE ENTRADA
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print(f"\n{SEP2}")
    print("  crud_demo.py — SQLAlchemy ORM · CRUD + Consultas")
    print(f"  Banco: {DB_CONFIG['dbname']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(SEP2)

    db = Database()
    print("\n  Conectando ao banco de dados...")
    if not db.conectar():
        print("\n  Falha na conexão. Verifique config.py e tente novamente.\n")
        sys.exit(1)
    print("  Conexão estabelecida.\n")

    try:
        # ── CRUD ──────────────────────────────────────────────────────────
        ids_hospedes, ids_reservas = demo_create(db)
        demo_read(db)
        demo_update(db, ids_hospedes, ids_reservas)
        demo_consultas(db)
        demo_delete(db, ids_hospedes, ids_reservas)

        print(f"\n{SEP2}")
        print("  Demo concluída com sucesso.")
        print(SEP2 + "\n")

    except Exception as e:
        print(f"\n  ERRO inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.desconectar()


if __name__ == "__main__":
    main()