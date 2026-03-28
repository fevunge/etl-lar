from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.exc import OperationalError
from logs import logging
from config import DB_CONFIG

# ==========================================================
# CONFIGURAÇÃO DA CONEXÃO
# ==========================================================


def get_engine():
    """Cria e retorna engine SQLAlchemy para conexão com MySQL."""
    url = URL.create(
        drivername="mysql+pymysql",
        username=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        database=DB_CONFIG["database"]
    )

    engine = create_engine(url, pool_pre_ping=True)

    return engine


# ==========================================================
# FUNÇÃO GENÉRICA DE CARGA
# ==========================================================

def load_table(df, nome_tabela, engine):
    """Carrega um dataframe para uma tabela MySQL com logs e tratamento de erros."""
    if df is None or df.empty:
        logging.warning(f"Tabela {nome_tabela} vazia. Não carregada.")
        return 0

    try:
        df.to_sql(
            nome_tabela,
            con=engine,
            if_exists="append",
            index=False
        )
        logging.info(f"✅ Load concluído — {nome_tabela}: {len(df)} registros no MySQL")
        return len(df)
    except Exception as e:
        logging.error(f"Erro ao carregar {nome_tabela}: {e}")

        mensagem_original = str(e)
        erro_conexao_mysql = (
            isinstance(e, OperationalError)
            or "Can't connect to MySQL server" in mensagem_original
            or "Connection refused" in mensagem_original
            or "(2003" in mensagem_original
        )

        if erro_conexao_mysql:
            raise RuntimeError(
                f"Erro ao carregar {nome_tabela}: {mensagem_original}\n"
                "MySQL indisponível. Disponibilize o serviço do banco MySQL "
                "(host/porta/credenciais) e tente novamente."
            ) from e

        raise RuntimeError(
            f"Erro ao carregar {nome_tabela}: {mensagem_original}"
        ) from e


# ==========================================================
# FUNÇÃO PRINCIPAL DE LOAD
# ==========================================================

def load_all(
    paciente,
    medico,
    especialidade,
    leito,
    tipo_cirurgia,
    motivo_internamento,
    dim_tempo,
    consulta,
    cirurgia,
    internamento
):
    """Executa carga de todas as dimensões e fatos para o Data Warehouse."""
    engine = get_engine()
    total = 0

    # ==========================
    # CARGA DAS DIMENSÕES
    # ==========================
    total += load_table(paciente, "dim_paciente", engine)
    total += load_table(medico, "dim_medico", engine)
    total += load_table(especialidade, "dim_especialidade", engine)
    total += load_table(leito, "dim_leito", engine)
    total += load_table(tipo_cirurgia, "dim_tipo_cirurgia", engine)
    total += load_table(motivo_internamento, "dim_motivo_internamento", engine)
    total += load_table(dim_tempo, "dim_tempo", engine)

    # ==========================
    # CARGA DAS TABELAS FATO
    # ==========================
    total += load_table(consulta, "fato_consulta", engine)
    total += load_table(cirurgia, "fato_cirurgia", engine)
    total += load_table(internamento, "fato_internamento", engine)

    return total
