

# VISÃO GERAL DO PROJETO PRÁTICO
## Pipeline ETL para Integração de Dados Hospitalares (Oftalmologia)

---

## 1. OBJETIVO DO PIPELINE
Construir um pipeline ETL completo e robusto que:
1. Extrai dados clínicos a partir de ficheiros CSV
2. Carrega os dados em tabelas staging no MySQL
3. Transforma os dados para o modelo final
4. Disponibiliza os dados para análise no Power BI

---

## 2. TECNOLOGIAS ENVOLVIDAS
- Python 3.x
- MySQL Server
- phpMyAdmin (gestão visual)
- pandas
- SQLAlchemy
- PyMySQL
- Power BI
- Sistema Operativo: Windows

---

## 3. ARQUITETURA DO PIPELINE
```
CSV (Mockaroo)
↓
EXTRAÇÃO (Python / pandas)
↓
TRANSFORMAÇÃO (SQL + Python)
↓
TABELAS FINAIS
↓
POWER BI
```

---

## 4. ESTRUTURA DO PROJETO
```
projeto_etl/
│
├── data/
│   ├── raw/          # CSV originais
│   └── processed/    # CSV tratados (opcional)
│
├── config/
│   └── db_config.py  # credenciais MySQL
│
├── extract/
│   └── extract_data.py
│
├── transform/
│   └── transform_data.py
│
├── load/
│   └── load_data.py
│
├── logs/
│   └── etl.log
│
├── main.py
└── requirements.txt
```

---

## 5. BASE DE DADOS (MODELO LÓGICO)

### 5.1 Banco de Dados
`etl_oftalmo`

### 5.2 Tabelas STAGING (EXTRAÇÃO)
- staging_paciente
- staging_medico
- staging_especialidade
- staging_consulta
- staging_exame
- staging_cirurgia
- staging_internamento
- staging_leito
- staging_transferencia

Estrutura idêntica aos CSV, sem regras de negócio.

### 5.3 Tabelas FINAIS (TRANSFORMAÇÃO)
- paciente
- medico
- especialidade
- consulta
- exame
- cirurgia
- internamento
- leito
- transferencia

Com:
- chaves primárias
- chaves estrangeiras
- normalização
- tipos de dados corretos

---

## 6. ETAPA 1 — EXTRAÇÃO (CSV → STAGING)

**Responsabilidades**
- Ler automaticamente todos os CSV
- Validar existência dos ficheiros
- Inserir dados nas tabelas staging
- Tratar encoding e datas

**Ferramentas**
- `pandas.read_csv()`
- `DataFrame.to_sql()`

---

## 7. ETAPA 2 — TRANSFORMAÇÃO

**Exemplos**
- Converter datas
- Normalizar sexo
- Eliminar duplicados
- Criar chaves
- Validar integridade

**Local**
- SQL (MySQL)
- Python (transform_data.py)

---

## 8. ETAPA 3 — CARGA FINAL
- Inserção nas tabelas definitivas
- Garantia de integridade referencial
- Preparação para análise

---

## 9. LOGS E CONTROLO

**Registo de:**
- início do ETL
- erros
- quantidade de registos processados

**Arquivo:** `logs/etl.log`

---

## 10. VALIDAÇÃO
- Contagem de registos (CSV × MySQL)
- Verificação de chaves
- Testes simples de consulta SQL

---

## 11. VISUALIZAÇÃO (POWER BI)

Conexão direta ao MySQL. Criação de indicadores:
- número de consultas
- patologias mais frequentes
- ocupação de leitos
- exames por período

---

## 12. RESULTADO FINAL
Um pipeline funcional, reprodutível, académico e alinhado com boas práticas, adequado:
- ao Instituto Oftalmológico Nacional de Angola
- a uma monografia técnica
- a uma defesa prática

---

---

# 📋 RESUMO E EXPLICAÇÃO

## O que é este projeto?
Este documento descreve um **pipeline ETL** (Extract, Transform, Load) académico, desenvolvido em Python, voltado para a gestão de dados clínicos de uma instituição de oftalmologia — o **Instituto Oftalmológico Nacional de Angola**.

## O que é um pipeline ETL?
Um pipeline ETL é um fluxo automatizado de dados dividido em três grandes fases:

| Fase | O que faz |
|------|-----------|
| **Extract (Extração)** | Lê os dados brutos de ficheiros CSV gerados com Mockaroo |
| **Transform (Transformação)** | Limpa, normaliza e estrutura os dados (datas, duplicados, chaves) |
| **Load (Carga)** | Insere os dados tratados nas tabelas finais do MySQL |

## Como os dados fluem?
1. Os dados clínicos (pacientes, médicos, consultas, cirurgias, etc.) são gerados em **ficheiros CSV**
2. Python lê esses ficheiros com **pandas** e carrega-os em **tabelas staging** no MySQL — uma zona temporária sem regras de negócio
3. A camada de transformação aplica regras (normalização, validação, criação de chaves) para produzir as **tabelas finais**
4. O **Power BI** conecta-se diretamente ao MySQL para criar dashboards e indicadores clínicos

## Estrutura técnica resumida
- **Linguagem:** Python 3.x
- **Base de dados:** MySQL (`etl_oftalmo`), gerida via phpMyAdmin
- **Bibliotecas:** pandas, SQLAlchemy, PyMySQL
- **Visualização:** Power BI
- **Organização:** pastas separadas por responsabilidade (extract, transform, load, config, logs)

## Por que duas camadas de tabelas?
As **tabelas staging** recebem os dados exatamente como vieram do CSV, sem qualquer validação. Isso protege o processo de erros imediatos. Só depois, na transformação, é que se aplicam as regras de negócio e se criam as **tabelas finais** com integridade referencial.

## Para que serve no fim?
O resultado é um sistema reprodutível, documentado e alinhado com boas práticas de Engenharia de Dados, adequado para:
- uma **monografia técnica** universitária
- uma **defesa prática** académica
- aplicação real no contexto hospitalar angolano
