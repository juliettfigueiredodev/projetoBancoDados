from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# ==============================
# CONFIGURAÇÃO DA CONEXÃO
# ==============================
DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "postgres"
DB_PASSWORD = "1234"
DB_NAME = "sistema_hotel"

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_session():
    """Retorna uma sessão do banco de dados."""
    return SessionLocal()
