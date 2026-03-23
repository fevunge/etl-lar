import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

# ==========================================================
# CONFIGURAÇÃO DA CONEXÃO
# ==========================================================


def get_engine():

    url = URL.create(
        drivername="mysql+pymysql",
        username="root",
        password="Regi@8991_21",
        host="127.0.0.1",
        port=3307,
        database="hospital_dw"
    )

    engine = create_engine(url)

    return engine


# ==========================================================
# FUNÇÃO GENÉRICA DE CARGA
# ==========================================================

def load_table(df, nome_tabela, engine):
    if df is None or df.empty:
        print(f"Tabela {nome_tabela} vazia. Não carregada.")
        return

    try:
        df.to_sql(
            nome_tabela,
            con=engine,
            if_exists="append",
            index=False
        )
        print(f"Tabela {nome_tabela} carregada com sucesso.")
    except Exception as e:
        print(f"Erro ao carregar {nome_tabela}: {e}")


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
    engine = get_engine()

    # ==========================
    # CARGA DAS DIMENSÕES
    # ==========================
    load_table(paciente, "dim_paciente", engine)
    load_table(medico, "dim_medico", engine)
    load_table(especialidade, "dim_especialidade", engine)
    load_table(leito, "dim_leito", engine)
    load_table(tipo_cirurgia, "dim_tipo_cirurgia", engine)
    load_table(motivo_internamento, "dim_motivo_internamento", engine)
    load_table(dim_tempo, "dim_tempo", engine)

    # ==========================
    # CARGA DAS TABELAS FATO
    # ==========================
    load_table(consulta, "fato_consulta", engine)
    load_table(cirurgia, "fato_cirurgia", engine)
    load_table(internamento, "fato_internamento", engine)

    print("Carga completa finalizada.")
