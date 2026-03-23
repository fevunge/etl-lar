import pandas as pd
import os
from config import DATA_RAW


def load_csv(file_name):
    path = os.path.join(DATA_RAW, file_name)
    try:
        df = pd.read_csv(
            path,
            sep=None,                # Detecta automaticamente separador
            engine="python",         # Mais tolerante que engine C
            encoding="utf-8",
            on_bad_lines="skip"      # Ignora linhas corrompidas
        )
        print(f"{file_name} carregado com sucesso. Linhas: {len(df)}")
        return df
    except Exception as e:
        print(f"Erro ao carregar {file_name}: {e}")
        return None


def extract_all():
    return {
        "paciente": load_csv("Paciente.csv"),
        "medico": load_csv("Medico.csv"),
        "especialidade": load_csv("Especialidade.csv"),
        "consulta": load_csv("Consulta.csv"),
        "cirurgia": load_csv("Cirurgia.csv"),
        "internamento": load_csv("Internamento.csv"),
    }
