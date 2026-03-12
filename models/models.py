"""
models/models.py
Mapeamento ORM de todas as tabelas do sistema_hotel.
"""

from sqlalchemy import (
    Integer, String, Numeric, Date, Text,
    ForeignKey, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, timedelta
from database import Base


# ====================
# ENTIDADE: Hospede
# Relacionamentos:
#   1-N com Reserva (um hóspede pode ter várias reservas)
# ====================
class Hospede(Base):
    __tablename__ = "hospede"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo_documento: Mapped[str] = mapped_column(
        String(15), nullable=False
    )
    valor_documento: Mapped[str] = mapped_column(String(14), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    telefone: Mapped[str] = mapped_column(String(20), nullable=False)

    # Relacionamento 1-N: um hóspede → várias reservas
    reservas: Mapped[list["Reserva"]] = relationship(
        "Reserva", back_populates="hospede"
    )

    def __repr__(self):
        return f"<Hospede id={self.id} nome='{self.nome}'>"


# ====================
# ENTIDADE: Quarto
# Relacionamentos:
#   1-N com Reserva
#   1-N com QuartoManutencao
# ====================
class Quarto(Base):
    __tablename__ = "quarto"

    numero: Mapped[int] = mapped_column(Integer, primary_key=True)
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)
    capacidade: Mapped[int] = mapped_column(Integer, nullable=False)
    tarifa_base_diaria: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False)

    # Relacionamento 1-N: um quarto → várias reservas
    reservas: Mapped[list["Reserva"]] = relationship(
        "Reserva", back_populates="quarto"
    )

    # Relacionamento 1-N: um quarto → várias manutenções
    manutencoes: Mapped[list["QuartoManutencao"]] = relationship(
        "QuartoManutencao", back_populates="quarto"
    )

    def __repr__(self):
        return f"<Quarto numero={self.numero} tipo='{self.tipo}' status='{self.status}'>"


# ====================
# ENTIDADE: QuartoManutencao
# Relacionamentos:
#   N-1 com Quarto
# ====================
class QuartoManutencao(Base):
    __tablename__ = "quarto_manutencao"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    motivo: Mapped[str] = mapped_column(Text, nullable=False)
    data_inicio: Mapped[date] = mapped_column(
        Date, nullable=False, default=date.today
    )
    data_fim_prevista: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        default=lambda: date.today() + timedelta(days=7)
    )
    numero_quarto: Mapped[int] = mapped_column(
        Integer, ForeignKey("quarto.numero", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False
    )

    # Relacionamento N-1: várias manutenções → um quarto
    quarto: Mapped["Quarto"] = relationship(
        "Quarto", back_populates="manutencoes"
    )

    def __repr__(self):
        return f"<Manutencao id={self.id} quarto={self.numero_quarto}>"


# ====================
# ENTIDADE: Reserva
# Relacionamentos:
#   N-1 com Hospede
#   N-1 com Quarto
#   1-N com Pagamento
# ====================
class Reserva(Base):
    __tablename__ = "reserva"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    data_entrada: Mapped[date] = mapped_column(
        Date, nullable=False, default=date.today
    )
    data_saida: Mapped[date] = mapped_column(Date, nullable=False)
    nro_hospedes: Mapped[int] = mapped_column(Integer, nullable=False)
    origem: Mapped[str] = mapped_column(String(10), nullable=False)

    id_hospede: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("hospede.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False
    )
    numero_quarto: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("quarto.numero", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False
    )

    # Relacionamento N-1: várias reservas → um hóspede
    hospede: Mapped["Hospede"] = relationship(
        "Hospede", back_populates="reservas"
    )

    # Relacionamento N-1: várias reservas → um quarto
    quarto: Mapped["Quarto"] = relationship(
        "Quarto", back_populates="reservas"
    )

    # Relacionamento 1-N: uma reserva → vários pagamentos
    pagamentos: Mapped[list["Pagamento"]] = relationship(
        "Pagamento", back_populates="reserva"
    )

    def __repr__(self):
        return (
            f"<Reserva id={self.id} "
            f"entrada={self.data_entrada} saida={self.data_saida}>"
        )


# ====================
# ENTIDADE: Pagamento
# Relacionamentos:
#   N-1 com Reserva
# ====================
class Pagamento(Base):
    __tablename__ = "pagamento"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    data: Mapped[date] = mapped_column(Date, nullable=True)
    forma: Mapped[str] = mapped_column(String(10), nullable=False)
    valor: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    id_reserva: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("reserva.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False
    )

    # Relacionamento N-1: vários pagamentos → uma reserva
    reserva: Mapped["Reserva"] = relationship(
        "Reserva", back_populates="pagamentos"
    )

    def __repr__(self):
        return f"<Pagamento id={self.id} valor={self.valor} forma='{self.forma}'>"
