# dados.py
import pandas as pd
import config

def carregar_dados():
    """Lê os CSVs e retorna os dados baseados formatados."""
    
    # Lendo origens e facilidades
    origem_alvo_df = pd.read_csv(config.PATH_ORIGEM_ALVO)
    facilidades_df = pd.read_csv(config.PATH_FACILIDADES)

    # Matriz de tempos
    A_total_df = pd.read_csv(config.PATH_MATRIZ_ROTAS).fillna(1e9)
    col_dem = [c for c in A_total_df.columns if c.startswith('D_')]
    col_fac = [c for c in A_total_df.columns if c.startswith('F_')]
    colunas = col_dem + col_fac

    A_total_df.index = col_dem
    durations_min = A_total_df[colunas].to_numpy()

    # Demanda d_i (Lembrando de forçar o tipo str para CD_SETOR!)
    demanda_df = pd.read_csv(config.PATH_DEMANDA_SET, dtype={"CD_SETOR": str})
    if "CD_setor" in demanda_df.columns:
        demanda_df = demanda_df.rename(columns={"CD_setor": "CD_SETOR"})
        
    setores_df = pd.read_csv(config.PATH_SETORES_POP, dtype={"CD_SETOR": str})
    df_join = demanda_df.merge(setores_df, on="CD_SETOR", how="right").fillna(0)
    agrupado = df_join.groupby("ID_divisao")["necessidade_total_leitos"].sum()
    d_i = {f"D_{k}": v for k, v in agrupado.to_dict().items()}

    # Suprimentos existentes
    x_hat = {f"F_{row['CO_UNIDADE']}": row['leitos'] for _, row in facilidades_df.iterrows()}

    return {
        "col_dem": col_dem,
        "col_fac": col_fac,
        "colunas": colunas,
        "durations_min": durations_min,
        "d_i": d_i,
        "x_hat": x_hat
    }
