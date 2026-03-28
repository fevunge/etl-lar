import pandas as pd
import numpy as np


def standardize_columns(df):
    """Padroniza nomes de colunas para minúsculas e sem espaços extras."""
    df.columns = [column.strip().lower() for column in df.columns]
    return df


def clean_dataframe(df):
    """Realiza limpeza básica removendo duplicatas e padronizando texto."""
    if df is None:
        return pd.DataFrame()

    data = df.copy()
    data = standardize_columns(data)
    data = data.drop_duplicates()

    for column in data.select_dtypes(include="object").columns:
        data[column] = (
            data[column]
            .astype(str)
            .str.strip()
            .replace({"nan": np.nan, "None": np.nan})
        )

    return data


def safe_convert_id(df, column_name):
    """Converte uma coluna de ID para numérico sem quebrar o pipeline."""
    if column_name in df.columns:
        df[column_name] = pd.to_numeric(df[column_name], errors="coerce")
    return df


def parse_mixed_date(series):
    """Converte datas com formatos mistos (day-first e month-first)."""
    normalized = series.astype(str).str.strip()

    formatos = [
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    ]

    resultado = pd.Series(pd.NaT, index=normalized.index, dtype="datetime64[ns]")

    for formato in formatos:
        parsed = pd.to_datetime(normalized, format=formato, errors="coerce")
        resultado = resultado.fillna(parsed)

    return resultado


def transform_paciente(df):
    """Limpa e transforma a dimensão paciente."""
    data = clean_dataframe(df)
    data = safe_convert_id(data, "id_paciente")

    if "data_nascimento" in data.columns:
        data["data_nascimento"] = parse_mixed_date(data["data_nascimento"])
        current_date = pd.Timestamp.today().normalize()
        data["idade"] = ((current_date - data["data_nascimento"]).dt.days // 365)
        data["idade"] = data["idade"].fillna(0).astype(int)

    for column in data.select_dtypes(include="object").columns:
        data[column] = data[column].fillna("Não informado")

    return data


def transform_medico(df):
    """Limpa e transforma a dimensão médico."""
    data = clean_dataframe(df)
    data = safe_convert_id(data, "id_medico")

    for column in data.select_dtypes(include="object").columns:
        data[column] = data[column].fillna("Não informado")

    return data


def transform_especialidade(df):
    """Limpa e transforma a dimensão especialidade."""
    data = clean_dataframe(df)
    data = safe_convert_id(data, "id_especialidade")

    for column in data.select_dtypes(include="object").columns:
        data[column] = data[column].fillna("Não informado")

    return data


def criar_dim_leito(internamento_df):
    """Cria dimensão de leitos a partir dos internamentos."""
    data = clean_dataframe(internamento_df)

    if "id_leito" not in data.columns:
        return pd.DataFrame(columns=["id_leito"])

    dim_leito = pd.DataFrame({
        "id_leito": pd.to_numeric(data["id_leito"], errors="coerce")
    }).dropna().drop_duplicates()

    dim_leito["id_leito"] = dim_leito["id_leito"].astype(int)
    return dim_leito


def criar_dim_tipo_cirurgia(df_cirurgia):
    """Cria dimensão de tipo de cirurgia."""
    data = clean_dataframe(df_cirurgia)

    if "tipo_cirurgia" not in data.columns:
        return None

    dim = data[["tipo_cirurgia"]].dropna().drop_duplicates().reset_index(drop=True)

    if dim.empty:
        return None

    dim["id_tipo_cirurgia"] = dim.index + 1
    return dim[["id_tipo_cirurgia", "tipo_cirurgia"]]


def criar_dim_motivo_internamento(df_internamento):
    """Cria dimensão de motivos de internamento."""
    data = clean_dataframe(df_internamento)

    if "motivo" not in data.columns:
        return None

    dim = data[["motivo"]].dropna().drop_duplicates().reset_index(drop=True)

    if dim.empty:
        return None

    dim["id_motivo_internamento"] = dim.index + 1
    dim = dim.rename(columns={"motivo": "descricao_motivo"})

    return dim[["id_motivo_internamento", "descricao_motivo"]]


def transformar_fato_consulta(df_consulta):
    """Transforma dados de consulta para a tabela fato."""
    data = clean_dataframe(df_consulta)

    required_columns = [
        "id_consulta", "id_paciente", "id_medico", "especialidade_id", "data_consulta"
    ]

    for column in required_columns:
        if column not in data.columns:
            return pd.DataFrame(columns=[
                "id_consulta", "id_paciente", "id_medico", "id_especialidade", "data_consulta"
            ])

    data["data_consulta"] = parse_mixed_date(data["data_consulta"])
    data["id_consulta"] = pd.to_numeric(data["id_consulta"], errors="coerce")
    data["id_paciente"] = pd.to_numeric(data["id_paciente"], errors="coerce")
    data["id_medico"] = pd.to_numeric(data["id_medico"], errors="coerce")
    data["id_especialidade"] = pd.to_numeric(data["especialidade_id"], errors="coerce")

    data = data.dropna(subset=[
        "id_consulta", "id_paciente", "id_medico", "id_especialidade", "data_consulta"
    ])

    return data[[
        "id_consulta", "id_paciente", "id_medico", "id_especialidade", "data_consulta"
    ]]


def transformar_fato_cirurgia(df_cirurgia, dim_tipo_cirurgia):
    """Transforma dados de cirurgia para a tabela fato."""
    data = clean_dataframe(df_cirurgia)

    if data.empty or dim_tipo_cirurgia is None:
        return pd.DataFrame()

    data["data_cirurgia"] = parse_mixed_date(data["data_cirurgia"])
    data["id_cirurgia"] = pd.to_numeric(data["id_cirurgia"], errors="coerce")
    data["id_paciente"] = pd.to_numeric(data["id_paciente"], errors="coerce")
    data["id_medico"] = pd.to_numeric(data["id_medico"], errors="coerce")

    data = data.merge(dim_tipo_cirurgia, on="tipo_cirurgia", how="left")

    data = data.dropna(subset=[
        "id_cirurgia", "id_paciente", "id_medico", "id_tipo_cirurgia", "data_cirurgia"
    ])

    return data[[
        "id_cirurgia", "id_paciente", "id_medico", "id_tipo_cirurgia", "data_cirurgia"
    ]]


def transformar_fato_internamento(df_internamento, dim_motivo):
    """Transforma dados de internamento para a tabela fato."""
    data = clean_dataframe(df_internamento)

    if data.empty or dim_motivo is None:
        return pd.DataFrame()

    for column in ["id_internamento", "id_paciente", "id_leito"]:
        if column in data.columns:
            data[column] = pd.to_numeric(data[column], errors="coerce")

    if "data_internamento" in data.columns:
        data["data_internamento"] = parse_mixed_date(data["data_internamento"])
    elif "data_entrada" in data.columns:
        data["data_internamento"] = parse_mixed_date(data["data_entrada"])
    else:
        data["data_internamento"] = pd.NaT

    data = data.merge(
        dim_motivo,
        left_on="motivo",
        right_on="descricao_motivo",
        how="left"
    )

    data = data.dropna(subset=[
        "id_internamento", "id_paciente", "id_leito", "id_motivo_internamento", "data_internamento"
    ])

    return data[[
        "id_internamento", "id_paciente", "id_leito", "id_motivo_internamento", "data_internamento"
    ]]


def criar_dim_tempo(*dataframes):
    """Cria dimensão tempo com base nas datas das tabelas fato."""
    datas = []

    for dataframe in dataframes:
        if dataframe is None or dataframe.empty:
            continue

        for column in ["data_consulta", "data_cirurgia", "data_internamento"]:
            if column in dataframe.columns:
                datas.extend(dataframe[column].dropna().tolist())

    if not datas:
        return pd.DataFrame(columns=["id_tempo", "data", "ano", "mes", "dia"])

    serie_datas = pd.Series(pd.to_datetime(datas, errors="coerce")).dropna().drop_duplicates().sort_values()

    dim_tempo = pd.DataFrame({"data": serie_datas})
    dim_tempo["ano"] = dim_tempo["data"].dt.year
    dim_tempo["mes"] = dim_tempo["data"].dt.month
    dim_tempo["dia"] = dim_tempo["data"].dt.day
    dim_tempo["id_tempo"] = dim_tempo["data"].dt.strftime("%Y%m%d").astype(int)

    return dim_tempo[["id_tempo", "data", "ano", "mes", "dia"]]
