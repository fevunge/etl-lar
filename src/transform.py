import pandas as pd
import numpy as np

# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================


def standardize_columns(df):
    if df is None:
        return None
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df


def clean_dataframe(df):
    if df is None:
        return None
    df = standardize_columns(df)
    df = df.drop_duplicates()
    df = df.dropna(how="all")
    return df


def safe_convert_id(df, column_name):
    if column_name in df.columns:
        df[column_name] = pd.to_numeric(
            df[column_name], errors="coerce"
        )
        df = df.dropna(subset=[column_name])
        df[column_name] = df[column_name].astype("Int64")
    return df

# ==========================================================
# TRANSFORMAÇÃO PACIENTE
# ==========================================================


def transform_paciente(df):
    df = clean_dataframe(df)
    df = safe_convert_id(df, "id_paciente")

    if "data_nascimento" in df.columns:
        df["data_nascimento"] = pd.to_datetime(
            df["data_nascimento"], errors="coerce", dayfirst=True
        )
        hoje = pd.Timestamp.today()
        df["idade"] = (hoje - df["data_nascimento"]).dt.days // 365
        df["idade"] = df["idade"].fillna(0)

    # preencher texto
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].fillna("Não informado")

    return df

# ==========================================================
# TRANSFORMAÇÃO MÉDICO
# ==========================================================


def transform_medico(df):
    df = clean_dataframe(df)
    df = safe_convert_id(df, "id_medico")

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].fillna("Não informado")

    return df

# ==========================================================
# TRANSFORMAÇÃO ESPECIALIDADE
# ==========================================================


def transform_especialidade(df):
    df = df.copy()

    df["id_especialidade"] = pd.to_numeric(
        df["id_especialidade"], errors="coerce"
    )

    df = df.dropna(subset=["id_especialidade"])

    df["id_especialidade"] = df["id_especialidade"].astype(int)

    df = df.drop_duplicates(subset=["id_especialidade"])

    return df

# ==========================================================
# TRANSFORMAÇÃO LEITO
# ==========================================================


def transform_leito(df):
    df = clean_dataframe(df)
    df = safe_convert_id(df, "id_leito")

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].fillna("Não informado")

    return df

# ==========================================================
# TRANSFORMAÇÃO TIPO CIRURGIA
# ==========================================================


def criar_dim_tipo_cirurgia(df_cirurgia):

    if df_cirurgia is None:
        return None

    dim = df_cirurgia[["tipo_cirurgia"]].dropna().drop_duplicates()

    if dim.empty:
        return None

    dim = dim.reset_index(drop=True)
    dim["id_tipo_cirurgia"] = dim.index + 1

    dim = dim[["id_tipo_cirurgia", "tipo_cirurgia"]]

    return dim
# ==========================================================
# TRANSFORMAÇÃO MOTIVO INTERNAMENTO
# ==========================================================


def criar_dim_motivo_internamento(df_internamento):

    dim = (
        df_internamento[["motivo"]]
        .dropna()
        .drop_duplicates()
        .reset_index(drop=True)
    )

    dim["id_motivo_internamento"] = dim.index + 1

    dim = dim.rename(columns={
        "motivo": "descricao_motivo"
    })

    dim = dim[[
        "id_motivo_internamento",
        "descricao_motivo"
    ]]

    return dim

# ==========================================================
# TRANSFORMAÇÃO CONSULTA
# ==========================================================


def transform_consulta(df):
    df = clean_dataframe(df)

    df = safe_convert_id(df, "id_consulta")
    df = safe_convert_id(df, "id_paciente")
    df = safe_convert_id(df, "id_medico")
    df = safe_convert_id(df, "id_especialidade")

    if "data_consulta" in df.columns:
        df["data_consulta"] = pd.to_datetime(
            df["data_consulta"], errors="coerce", dayfirst=True
        )
        df["ano_consulta"] = df["data_consulta"].dt.year
        df["mes_consulta"] = df["data_consulta"].dt.month

    if "valor_consulta" in df.columns:
        df["valor_consulta"] = pd.to_numeric(
            df["valor_consulta"], errors="coerce"
        ).fillna(0)

    return df

# ==========================================================
# TRANSFORMAÇÃO CIRURGIA
# ==========================================================


def transform_cirurgia(df):
    df = clean_dataframe(df)

    df = safe_convert_id(df, "id_cirurgia")
    df = safe_convert_id(df, "id_paciente")
    df = safe_convert_id(df, "id_medico")
    df = safe_convert_id(df, "id_especialidade")
    df = safe_convert_id(df, "id_tipo_cirurgia")

    if "data_cirurgia" in df.columns:
        df["data_cirurgia"] = pd.to_datetime(
            df["data_cirurgia"], errors="coerce", dayfirst=True
        )
        df["ano_cirurgia"] = df["data_cirurgia"].dt.year
        df["mes_cirurgia"] = df["data_cirurgia"].dt.month

    if "valor_cirurgia" in df.columns:
        df["valor_cirurgia"] = pd.to_numeric(
            df["valor_cirurgia"], errors="coerce"
        ).fillna(0)

    df["quantidade_cirurgia"] = 1

    return df

# ==========================================================
# TRANSFORMAÇÃO INTERNAMENTO
# ==========================================================


def transform_internamento(df):
    df = clean_dataframe(df)

    df = safe_convert_id(df, "id_internamento")
    df = safe_convert_id(df, "id_paciente")
    df = safe_convert_id(df, "id_medico")
    df = safe_convert_id(df, "id_especialidade")
    df = safe_convert_id(df, "id_motivo_internamento")
    df = safe_convert_id(df, "id_leito")

    if "data_entrada" in df.columns:
        df["data_entrada"] = pd.to_datetime(
            df["data_entrada"], errors="coerce", dayfirst=True
        )
    if "data_alta" in df.columns:
        df["data_alta"] = pd.to_datetime(
            df["data_alta"], errors="coerce", dayfirst=True
        )

    if "data_entrada" in df.columns and "data_alta" in df.columns:
        df["dias_internado"] = (
            df["data_alta"] - df["data_entrada"]
        ).dt.days
        df["dias_internado"] = df["dias_internado"].fillna(0)

    df["quantidade_internamento"] = 1

    return df

# ==========================================================
# CRIAÇÃO DA DIMENSÃO TEMPO
# ==========================================================


def criar_dim_tempo(*dataframes):
    datas = pd.Series(dtype="datetime64[ns]")

    for df in dataframes:
        if df is not None:
            for col in df.columns:
                if "data" in col:
                    datas = pd.concat([datas, df[col]])

    datas = datas.dropna().drop_duplicates().sort_values()

    dim_tempo = pd.DataFrame()
    dim_tempo["data_completa"] = datas
    dim_tempo["dia"] = dim_tempo["data_completa"].dt.day
    dim_tempo["mes"] = dim_tempo["data_completa"].dt.month
    dim_tempo["ano"] = dim_tempo["data_completa"].dt.year
    dim_tempo["trimestre"] = dim_tempo["data_completa"].dt.quarter
    dim_tempo["nome_mes"] = dim_tempo["data_completa"].dt.month_name()
    dim_tempo["dia_semana"] = dim_tempo["data_completa"].dt.dayofweek
    dim_tempo["nome_dia_semana"] = dim_tempo["data_completa"].dt.day_name()

    return dim_tempo


def criar_dim_leito(internamento_df):
    if internamento_df is None:
        return None

    if "id_leito" not in internamento_df.columns:
        return None

    dim_leito = internamento_df[["id_leito"]].dropna().drop_duplicates()

    dim_leito["id_leito"] = dim_leito["id_leito"].astype("Int64")

    return dim_leito


def criar_dim_tipo_cirurgia(df_cirurgia):

    dim = (
        df_cirurgia[["tipo_cirurgia"]]
        .dropna()
        .drop_duplicates()
        .reset_index(drop=True)
    )

    dim["id_tipo_cirurgia"] = dim.index + 1

    dim = dim[["id_tipo_cirurgia", "tipo_cirurgia"]]

    return dim


def criar_dim_motivo_internamento(internamento_df):
    if internamento_df is None:
        return None

    if "id_motivo_internamento" not in internamento_df.columns:
        return None

    dim_motivo = internamento_df[[
        "id_motivo_internamento"]].dropna().drop_duplicates()

    dim_motivo["id_motivo_internamento"] = dim_motivo["id_motivo_internamento"].astype(
        "Int64")

    return dim_motivo


def transformar_fato_consulta(df_consulta):
    df = df_consulta.copy()

    df["data_consulta"] = pd.to_datetime(
        df["data_consulta"],
        dayfirst=True,
        errors="coerce"
    )

    df["id_consulta"] = pd.to_numeric(df["id_consulta"], errors="coerce")
    df["id_paciente"] = pd.to_numeric(df["id_paciente"], errors="coerce")
    df["id_medico"] = pd.to_numeric(df["id_medico"], errors="coerce")

    # AQUI ESTÁ A CORREÇÃO
    df["id_especialidade"] = pd.to_numeric(
        df["especialidade_id"], errors="coerce"
    )

    df = df.dropna(subset=[
        "id_consulta",
        "id_paciente",
        "id_medico",
        "id_especialidade",
        "data_consulta"
    ])

    df = df[[
        "id_consulta",
        "id_paciente",
        "id_medico",
        "id_especialidade",
        "data_consulta"
    ]]

    return df


def transformar_fato_cirurgia(df_cirurgia, dim_tipo_cirurgia):
    df = df_cirurgia.copy()

    df["data_cirurgia"] = pd.to_datetime(
        df["data_cirurgia"],
        dayfirst=True,
        errors="coerce"
    )

    df["id_cirurgia"] = pd.to_numeric(df["id_cirurgia"], errors="coerce")
    df["id_paciente"] = pd.to_numeric(df["id_paciente"], errors="coerce")
    df["id_medico"] = pd.to_numeric(df["id_medico"], errors="coerce")

    df = df.merge(
        dim_tipo_cirurgia,
        on="tipo_cirurgia",
        how="left"
    )

    df = df.dropna(subset=[
        "id_cirurgia",
        "id_paciente",
        "id_medico",
        "id_tipo_cirurgia",
        "data_cirurgia"
    ])

    df = df[[
        "id_cirurgia",
        "id_paciente",
        "id_medico",
        "id_tipo_cirurgia",
        "data_cirurgia"
    ]]

    return df


def transformar_fato_internamento(df_internamento, dim_motivo):
    df = df_internamento.copy()

    df["data_internamento"] = pd.to_datetime(
        df["data_internamento"],
        dayfirst=True,
        errors="coerce"
    )

    df["id_internamento"] = pd.to_numeric(
        df["id_internamento"], errors="coerce")
    df["id_paciente"] = pd.to_numeric(df["id_paciente"], errors="coerce")
    df["id_leito"] = pd.to_numeric(df["id_leito"], errors="coerce")

    df = df.merge(
        dim_motivo,
        left_on="motivo",
        right_on="descricao_motivo",
        how="left"
    )

    df = df.dropna(subset=[
        "id_internamento",
        "id_paciente",
        "id_leito",
        "id_motivo_internamento",
        "data_internamento"
    ])

    df = df[[
        "id_internamento",
        "id_paciente",
        "id_leito",
        "id_motivo_internamento",
        "data_internamento"
    ]]

    return df
