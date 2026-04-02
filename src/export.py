import pandas as pd

from config import OUTPUT_DIR
from logs import logging


def _consolidar_dataframes(dataframes):
    frames = []

    for table_name, dataframe in dataframes.items():
        if dataframe is None or dataframe.empty:
            continue

        temporary = dataframe.copy()
        temporary["_tabela"] = table_name
        frames.append(temporary)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True, sort=False)


def exportar_csv(dataframes):
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        path = OUTPUT_DIR / "dados_limpos.csv"

        dataframe = _consolidar_dataframes(dataframes)
        dataframe.to_csv(path, index=False, encoding="utf-8")

        logging.info(f"✅ CSV exportado → {path}")
    except Exception as error:
        logging.error(f"Erro ao exportar CSV: {error}")


def exportar_excel(dataframes):
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        path = OUTPUT_DIR / "dados_limpos.xlsx"

        ordem_tabelas = [
            "dim_paciente",
            "dim_medico",
            "dim_especialidade",
            "dim_leito",
            "dim_tipo_cirurgia",
            "dim_motivo_internamento",
            "dim_tempo",
            "fato_consulta",
            "fato_cirurgia",
            "fato_internamento",
        ]

        relacoes = [
            {
                "tabela_filha": "fato_consulta",
                "coluna_filha": "id_paciente",
                "tabela_pai": "dim_paciente",
                "coluna_pai": "id_paciente",
            },
            {
                "tabela_filha": "fato_consulta",
                "coluna_filha": "id_medico",
                "tabela_pai": "dim_medico",
                "coluna_pai": "id_medico",
            },
            {
                "tabela_filha": "fato_consulta",
                "coluna_filha": "id_especialidade",
                "tabela_pai": "dim_especialidade",
                "coluna_pai": "id_especialidade",
            },
            {
                "tabela_filha": "fato_cirurgia",
                "coluna_filha": "id_paciente",
                "tabela_pai": "dim_paciente",
                "coluna_pai": "id_paciente",
            },
            {
                "tabela_filha": "fato_cirurgia",
                "coluna_filha": "id_medico",
                "tabela_pai": "dim_medico",
                "coluna_pai": "id_medico",
            },
            {
                "tabela_filha": "fato_cirurgia",
                "coluna_filha": "id_tipo_cirurgia",
                "tabela_pai": "dim_tipo_cirurgia",
                "coluna_pai": "id_tipo_cirurgia",
            },
            {
                "tabela_filha": "fato_internamento",
                "coluna_filha": "id_paciente",
                "tabela_pai": "dim_paciente",
                "coluna_pai": "id_paciente",
            },
            {
                "tabela_filha": "fato_internamento",
                "coluna_filha": "id_leito",
                "tabela_pai": "dim_leito",
                "coluna_pai": "id_leito",
            },
            {
                "tabela_filha": "fato_internamento",
                "coluna_filha": "id_motivo_internamento",
                "tabela_pai": "dim_motivo_internamento",
                "coluna_pai": "id_motivo_internamento",
            },
        ]

        dataframes_validos = {
            nome: df
            for nome, df in dataframes.items()
            if df is not None and not df.empty
        }

        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            for table_name in ordem_tabelas:
                dataframe = dataframes_validos.get(table_name)
                if dataframe is None:
                    continue

                dataframe.to_excel(writer, sheet_name=table_name[:31], index=False)

            restantes = [
                nome for nome in dataframes_validos.keys() if nome not in ordem_tabelas
            ]
            for table_name in restantes:
                dataframes_validos[table_name].to_excel(
                    writer,
                    sheet_name=table_name[:31],
                    index=False,
                )

            relacoes_df = pd.DataFrame(relacoes)
            relacoes_df.to_excel(writer, sheet_name="relacoes", index=False)

        logging.info(f"✅ Excel exportado → {path}")
    except Exception as error:
        logging.error(f"Erro ao exportar Excel: {error}")


def _sql_value(value):
    if pd.isna(value):
        return "NULL"

    if isinstance(value, pd.Timestamp):
        return f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'"

    if isinstance(value, str):
        escaped = value.replace("'", "''")
        return f"'{escaped}'"

    return str(value)


def exportar_sql(dataframes):
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        path = OUTPUT_DIR / "dados_limpos.sql"

        with open(path, "w", encoding="utf-8") as file:
            for table_name, dataframe in dataframes.items():
                if dataframe is None or dataframe.empty:
                    continue

                columns = ", ".join(f"`{col}`" for col in dataframe.columns)

                for _, row in dataframe.iterrows():
                    values = ", ".join(_sql_value(row[col]) for col in dataframe.columns)
                    file.write(
                        f"INSERT INTO `{table_name}` ({columns}) VALUES ({values});\n"
                    )

        logging.info(f"✅ SQL exportado → {path}")
    except Exception as error:
        logging.error(f"Erro ao exportar SQL: {error}")
