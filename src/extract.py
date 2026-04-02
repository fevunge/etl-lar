import pandas as pd
from logs import logging
from config import DATA_RAW
import csv
from pathlib import Path

def _read_csv_resiliente(path: Path) -> pd.DataFrame:
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file, delimiter=",", quotechar='"')
        rows = list(reader)

    if not rows:
        return pd.DataFrame()

    header = [h.strip() for h in rows[0]]
    data = []
    expected_columns = len(header)

    for row in rows[1:]:
        if len(row) > expected_columns:
            row = row[: expected_columns - 1] + [", ".join(row[expected_columns - 1:])]
        elif len(row) < expected_columns:
            row = row + [""] * (expected_columns - len(row))
        data.append(row)

    return pd.DataFrame(data, columns=header)


def load_file(file_name):
    path = DATA_RAW / file_name
    try:
        if not path.exists():
            logging.error(f"Arquivo não encontrado: {path}")
            return None

        extension = path.suffix.lower()

        if extension == ".csv":
            df = _read_csv_resiliente(path)
        elif extension in {".xlsx", ".xls"}:
            df = pd.read_excel(path)
        else:
            logging.error(f"Formato não suportado: {extension}")
            return None

        logging.info(f"✅ Extract concluído — {file_name}: {len(df)} registros lidos")
        return df
    except Exception as e:
        logging.error(f"Erro ao carregar {file_name}: {e}")
        return None


def extract_all():
    return {
        "paciente": load_file("paciente.csv"),
        "medico": load_file("medico.csv"),
        "especialidade": load_file("especialidade.csv"),
        "consulta": load_file("consulta.csv"),
        "cirurgia": load_file("cirurgia.csv"),
        "internamento": load_file("internamento.csv"),
    }
