"""
queries/queries.py
Consultas com relacionamento (JOIN), filtros e ordenação via ORM.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, asc, desc
from models.models import Hospede, Quarto, Reserva, Pagamento, QuartoManutencao
from datetime import date


# ============================================================
# CONSULTA 1 — JOIN: Reservas ativas com dados do hóspede e quarto
# Equivalente ao SELECT com INNER JOIN do seu script SQL original
# ============================================================

def reservas_ativas_com_detalhes(session: Session) -> list:
    """
    Lista todas as reservas ativas (data_saida >= hoje),
    trazendo nome do hóspede, e-mail, telefone e tipo do quarto.
    Envolve JOIN entre Reserva, Hospede e Quarto.
    """
    resultados = (
        session.query(
            Reserva.id.label("id_reserva"),
            Hospede.nome.label("nome_hospede"),
            Hospede.email,
            Hospede.telefone,
            Quarto.numero.label("numero_quarto"),
            Quarto.tipo.label("tipo_quarto"),
            Reserva.data_entrada,
            Reserva.data_saida,
            Reserva.nro_hospedes,
            Reserva.origem
        )
        .join(Hospede, Reserva.id_hospede == Hospede.id)
        .join(Quarto, Reserva.numero_quarto == Quarto.numero)
        .filter(Reserva.data_saida >= date.today())
        .order_by(asc(Reserva.data_entrada))
        .all()
    )
    return resultados


# ============================================================
# CONSULTA 2 — JOIN + AGREGAÇÃO: Total pago por reserva
# Equivalente ao SELECT com SUM e GROUP BY do script original
# ============================================================

def total_pago_por_reserva(session: Session) -> list:
    """
    Retorna o valor total pago e quantidade de pagamentos por reserva.
    Envolve JOIN entre Reserva, Hospede, Quarto e Pagamento,
    com agregações SUM e COUNT, ordenado pelo maior valor.
    """
    resultados = (
        session.query(
            Reserva.id.label("id_reserva"),
            Hospede.nome.label("nome_hospede"),
            Quarto.numero.label("numero_quarto"),
            func.count(Pagamento.id).label("qtd_pagamentos"),
            func.sum(Pagamento.valor).label("valor_total_pago"),
            Reserva.data_entrada,
            Reserva.data_saida
        )
        .join(Hospede, Reserva.id_hospede == Hospede.id)
        .join(Quarto, Reserva.numero_quarto == Quarto.numero)
        .join(Pagamento, Pagamento.id_reserva == Reserva.id)
        .group_by(
            Reserva.id, Hospede.nome, Quarto.numero,
            Reserva.data_entrada, Reserva.data_saida
        )
        .order_by(desc("valor_total_pago"))
        .all()
    )
    return resultados


# ============================================================
# CONSULTA 3 — FILTRO + ORDENAÇÃO: Hóspedes brasileiros com reservas ativas
# Filtra por tipo_documento = 'CPF' e data_saida >= hoje
# ============================================================

def hospedes_brasileiros_com_reservas_ativas(session: Session) -> list:
    """
    Lista hóspedes com CPF (brasileiros) que possuem reservas ativas,
    com filtro + ordenação por data de entrada.
    """
    resultados = (
        session.query(
            Hospede.nome.label("nome_hospede"),
            Hospede.valor_documento.label("cpf"),
            Hospede.email,
            Reserva.data_entrada,
            Reserva.data_saida,
            Quarto.numero.label("numero_quarto"),
            Quarto.tipo.label("tipo_quarto")
        )
        .join(Reserva, Hospede.id == Reserva.id_hospede)
        .join(Quarto, Reserva.numero_quarto == Quarto.numero)
        .filter(
            Hospede.tipo_documento == "CPF",
            Reserva.data_saida >= date.today()
        )
        .order_by(asc(Reserva.data_entrada))
        .all()
    )
    return resultados


# ============================================================
# CONSULTA 4 — JOIN: Quartos com ou sem manutenção (LEFT JOIN)
# ============================================================

def quartos_com_manutencao(session: Session) -> list:
    """
    Lista todos os quartos mostrando se têm manutenção agendada.
    Usa LEFT JOIN para incluir quartos sem manutenção também.
    """
    resultados = (
        session.query(
            Quarto.numero.label("numero_quarto"),
            Quarto.tipo,
            Quarto.status,
            Quarto.tarifa_base_diaria,
            QuartoManutencao.motivo,
            QuartoManutencao.data_inicio,
            QuartoManutencao.data_fim_prevista
        )
        .outerjoin(
            QuartoManutencao,
            Quarto.numero == QuartoManutencao.numero_quarto
        )
        .order_by(asc(Quarto.numero))
        .all()
    )
    return resultados


# ============================================================
# CONSULTA 5 — FILTRO + ORDENAÇÃO: Quartos baratos disponíveis
# ============================================================

def quartos_disponiveis_baratos(session: Session,
                                 limite_tarifa: float = 300.0) -> list[Quarto]:
    """
    Filtra quartos disponíveis com tarifa abaixo do limite informado,
    ordenados pela tarifa (mais barato primeiro).
    """
    return (
        session.query(Quarto)
        .filter(
            Quarto.status == "DISPONIVEL",
            Quarto.tarifa_base_diaria < limite_tarifa
        )
        .order_by(asc(Quarto.tarifa_base_diaria))
        .all()
    )
