# e2sfca.py
import numpy as np
import pandas as pd
import config

def calcular_parametros_e2sfca(dados):
    """Calcula áreas de captação, pesos, demandas ponderadas e baseline (A_antes)."""
    
    col_dem = dados["col_dem"]
    col_fac = dados["col_fac"]
    colunas = dados["colunas"]
    durations_min = dados["durations_min"]
    d_i = dados["d_i"]
    x_hat = dados["x_hat"]

    # Áreas de captação
    M_i = {
        col_dem[i]: [colunas[j] for j in range(durations_min.shape[1]) if durations_min[i, j] <= config.T_0]
        for i in range(len(col_dem))
    }
    N_j = {
        colunas[j]: [col_dem[i] for i in range(len(col_dem)) if durations_min[i, j] <= config.T_0]
        for j in range(durations_min.shape[1])
    }

    # Decaimento
    w_df = pd.DataFrame(np.exp(-config.BETA * durations_min), index=col_dem, columns=colunas)

    # Demanda Ponderada Base
    DEMANDA_PONDERADA = {}
    for j in colunas:
        dem_total = sum(w_df.loc[i, j] * d_i.get(i, 0.0) for i in N_j[j])
        DEMANDA_PONDERADA[j] = max(dem_total, config.EPSILON)

    # Acessibilidade Antes (Baseline)
    R_existente = {j: x_hat[j] / DEMANDA_PONDERADA[j] for j in col_fac}
    A_antes = {}
    for i in col_dem:
        A_antes[i] = sum(w_df.loc[i, j] * R_existente[j] for j in M_i.get(i, []) if j in col_fac)

    # Shortage e Demanda Ponderada para Candidatos
    A_vals_pos = [v for v in A_antes.values() if v > 0]
    limiar_acesso = np.median(A_vals_pos) if A_vals_pos else config.EPSILON
    
    shortage = {i: max(1.0 - A_antes[i] / limiar_acesso, 0.0) for i in col_dem}
    d_shortage = {i: d_i.get(i, 0.0) * shortage[i] for i in col_dem}

    DEMANDA_PONDERADA_CAND = {}
    for j in col_dem: # Candidatos são col_dem
        dem_total = sum(w_df.loc[i, j] * d_shortage.get(i, 0.0) for i in N_j[j])
        DEMANDA_PONDERADA_CAND[j] = max(dem_total, config.EPSILON)

    # Filtro de Equidade (Correção do seu notebook)
    nos_com_candidato = {
        i for i in col_dem
        if d_i.get(i, 0.0) > 0.5 and any(j in col_dem for j in M_i.get(i, []))
    }

    return {
        "N": col_dem, "M_e": col_fac, "M_n": col_dem, 
        "M_i": M_i, "N_j": N_j, "w_df": w_df,
        "DEMANDA_PONDERADA": DEMANDA_PONDERADA,
        "DEMANDA_PONDERADA_CAND": DEMANDA_PONDERADA_CAND,
        "A_antes": A_antes, "d_shortage": d_shortage,
        "nos_com_candidato": nos_com_candidato
    }
