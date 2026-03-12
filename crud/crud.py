"""
crud/crud.py
Operações CRUD via ORM (Create, Read, Update, Delete).
"""

from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from models.models import Hospede, Quarto, Reserva, Pagamento, QuartoManutencao
from datetime import date


# ============================================================
# CREATE — Inserção de registros
# ============================================================

def criar_hospede(session: Session, nome: str, tipo_documento: str,
                  valor_documento: str, email: str, telefone: str) -> Hospede:
    """Insere um novo hóspede no banco, ou retorna o existente se o e-mail já estiver cadastrado."""
    existente = session.query(Hospede).filter(Hospede.email == email).first()
    if existente:
        print(f"  ℹ Hóspede já existe, usando cadastro atual: {existente}")
        return existente

    hospede = Hospede(
        nome=nome,
        tipo_documento=tipo_documento,
        valor_documento=valor_documento,
        email=email,
        telefone=telefone
    )
    session.add(hospede)
    session.commit()
    session.refresh(hospede)
    print(f"  ✔ Hóspede criado: {hospede}")
    return hospede


def criar_quarto(session: Session, numero: int, tipo: str,
                 capacidade: int, tarifa: float, status: str) -> Quarto:
    existente = session.query(Quarto).filter(Quarto.numero == numero).first()
    if existente:
        print(f"  ℹ Quarto já existe, usando cadastro atual: {existente}")
        return existente
    """Insere um novo quarto no banco."""
    quarto = Quarto(
        numero=numero,
        tipo=tipo,
        capacidade=capacidade,
        tarifa_base_diaria=tarifa,
        status=status
    )
    session.add(quarto)
    session.commit()
    session.refresh(quarto)
    print(f"  ✔ Quarto criado: {quarto}")
    return quarto


def criar_reserva(session: Session, data_entrada: date, data_saida: date,
                  nro_hospedes: int, origem: str,
                  id_hospede: int, numero_quarto: int) -> Reserva:
    """Insere uma nova reserva no banco, ou retorna a existente se já houver
    uma reserva para o mesmo hóspede, quarto e data de entrada."""
    existente = session.query(Reserva).filter(
        Reserva.id_hospede == id_hospede,
        Reserva.numero_quarto == numero_quarto,
        Reserva.data_entrada == data_entrada
    ).first()
    if existente:
        print(f"  ℹ Reserva já existe, usando cadastro atual: {existente}")
        return existente

    reserva = Reserva(
        data_entrada=data_entrada,
        data_saida=data_saida,
        nro_hospedes=nro_hospedes,
        origem=origem,
        id_hospede=id_hospede,
        numero_quarto=numero_quarto
    )
    session.add(reserva)
    session.commit()
    session.refresh(reserva)
    print(f"  ✔ Reserva criada: {reserva}")
    return reserva

def criar_pagamento(session: Session, data: date, forma: str,
                    valor: float, id_reserva: int) -> Pagamento:
    """Insere um novo pagamento no banco."""
    pagamento = Pagamento(
        data=data,
        forma=forma,
        valor=valor,
        id_reserva=id_reserva
    )
    session.add(pagamento)
    session.commit()
    session.refresh(pagamento)
    print(f"  ✔ Pagamento criado: {pagamento}")
    return pagamento


# ============================================================
# READ — Listagem com paginação e ordenação
# ============================================================

def listar_hospedes(session: Session, pagina: int = 1,
                    por_pagina: int = 15) -> list[Hospede]:
    """
    Lista hóspedes com paginação simples.
    pagina=1 retorna os primeiros `por_pagina` registros.
    """
    offset = (pagina - 1) * por_pagina
    hospedes = (
        session.query(Hospede)
        .order_by(asc(Hospede.nome))
        .offset(offset)
        .limit(por_pagina)
        .all()
    )
    return hospedes


def listar_quartos_disponiveis(session: Session) -> list[Quarto]:
    """Lista quartos com status DISPONIVEL, ordenados pela tarifa."""
    return (
        session.query(Quarto)
        .filter(Quarto.status == "DISPONIVEL")
        .order_by(asc(Quarto.tarifa_base_diaria))
        .all()
    )


def listar_reservas(session: Session, pagina: int = 1,
                    por_pagina: int = 15) -> list[Reserva]:
    """Lista reservas ordenadas por data de entrada, com paginação."""
    offset = (pagina - 1) * por_pagina
    return (
        session.query(Reserva)
        .order_by(asc(Reserva.data_entrada))
        .offset(offset)
        .limit(por_pagina)
        .all()
    )


# ============================================================
# UPDATE — Atualização de registros
# ============================================================

def atualizar_status_quarto(session: Session, numero_quarto: int,
                             novo_status: str) -> Quarto | None:
    """Atualiza o status de um quarto."""
    quarto = session.query(Quarto).filter(
        Quarto.numero == numero_quarto
    ).first()

    if not quarto:
        print(f"  ✘ Quarto {numero_quarto} não encontrado.")
        return None

    quarto.status = novo_status
    session.commit()
    session.refresh(quarto)
    print(f"  ✔ Quarto {numero_quarto} atualizado para status '{novo_status}'")
    return quarto


def atualizar_email_hospede(session: Session, id_hospede: int,
                             novo_email: str) -> Hospede | None:
    """Atualiza o e-mail de um hóspede."""
    hospede = session.query(Hospede).filter(
        Hospede.id == id_hospede
    ).first()

    if not hospede:
        print(f"  ✘ Hóspede {id_hospede} não encontrado.")
        return None

    hospede.email = novo_email
    session.commit()
    session.refresh(hospede)
    print(f"  ✔ E-mail do hóspede '{hospede.nome}' atualizado para '{novo_email}'")
    return hospede


# ============================================================
# DELETE — Remoção de registros
# ============================================================

def deletar_hospede(session: Session, id_hospede: int) -> bool:
    hospede = session.query(Hospede).filter(
        Hospede.id == id_hospede
    ).first()

    if not hospede:
        print(f"  ✘ Hóspede {id_hospede} não encontrado.")
        return False

    # Verifica se o hóspede possui reservas antes de tentar remover
    tem_reservas = session.query(Reserva).filter(
        Reserva.id_hospede == id_hospede
    ).first()

    if tem_reservas:
        print(f"  ✘ Não é possível remover o hóspede '{hospede.nome}' "
              f"pois ele possui reservas vinculadas.")
        return False

    try:
        session.delete(hospede)
        session.commit()
        print(f"  ✔ Hóspede '{hospede.nome}' removido com sucesso.")
        return True
    except Exception as e:
        session.rollback()
        print(f"  ✘ Erro inesperado ao remover hóspede '{hospede.nome}': {e}")
        return False


def deletar_pagamento(session: Session, id_pagamento: int) -> bool:
    """Remove um pagamento pelo ID."""
    pagamento = session.query(Pagamento).filter(
        Pagamento.id == id_pagamento
    ).first()

    if not pagamento:
        print(f"  ✘ Pagamento {id_pagamento} não encontrado.")
        return False

    session.delete(pagamento)
    session.commit()
    print(f"  ✔ Pagamento {id_pagamento} removido com sucesso.")
    return True
