# otimizacao.py
import gurobipy as gp
from gurobipy import GRB, quicksum
import pandas as pd
import numpy as np
import config
from dados import carregar_dados
from e2sfca import calcular_parametros_e2sfca

def resolver_modelo_utopia(alpha_val, e2sfca_p, dados):
    """Função auxiliar para calcular os máximos de Eficiência e Equidade."""
    mod = gp.Model()
    mod.setParam('OutputFlag', 0)
    mod.setParam('TimeLimit', 300)
    mod.setParam('MIPGap', 0.001)

    y = mod.addVars(e2sfca_p["M_n"], vtype=GRB.BINARY)
    x = mod.addVars(e2sfca_p["M_n"], vtype=GRB.INTEGER)
    Z = mod.addVar(vtype=GRB.CONTINUOUS)

    def _expr_A(i):
        e = gp.LinExpr()
        for j in e2sfca_p["M_i"].get(i, []):
            w = e2sfca_p["w_df"].loc[i, j]
            denom = e2sfca_p["DEMANDA_PONDERADA"][j]
            if j in e2sfca_p["M_n"]:
                e.add(x[j], w / denom)
            elif j in e2sfca_p["M_e"]:
                e.addConstant(w * dados["x_hat"][j] / denom)
        return e

    ef = (1.0 / len(e2sfca_p["N"])) * quicksum(e2sfca_p["d_shortage"][i] * _expr_A(i) for i in e2sfca_p["N"])
    mod.setObjective(alpha_val * ef + (1 - alpha_val) * Z, GRB.MAXIMIZE)

    for i in e2sfca_p["nos_com_candidato"]:
        mod.addConstr(dados["d_i"][i] * _expr_A(i) >= Z)
    for j in e2sfca_p["M_n"]:
        mod.addConstr(x[j] >= config.K_MIN * y[j])
        mod.addConstr(x[j] <= config.K_MAX * y[j])
        
    mod.addConstr(quicksum(y[j] for j in e2sfca_p["M_n"]) == config.P_MAX)
    mod.addConstr(quicksum(x[j] for j in e2sfca_p["M_n"]) == config.Q_MAX)
    mod.optimize()

    if mod.SolCount > 0:
        ef_val = (1.0 / len(e2sfca_p["N"])) * sum(
            e2sfca_p["d_shortage"][i] * sum(
                e2sfca_p["w_df"].loc[i, j] * (x[j].x if j in e2sfca_p["M_n"] else dados["x_hat"].get(j, 0))
                / e2sfca_p["DEMANDA_PONDERADA"][j]
                for j in e2sfca_p["M_i"].get(i, [])
            ) for i in e2sfca_p["N"]
        )
        return ef_val, Z.x
    return config.EPSILON, config.EPSILON

def rodar_otimizacao():
    print("Carregando dados...")
    dados = carregar_dados()
    
    print("Calculando parâmetros E2SFCA...")
    e2sfca_p = calcular_parametros_e2sfca(dados)

    print("Calculando ponto utopia...")
    Ef_star, _ = resolver_modelo_utopia(1.0, e2sfca_p, dados)
    _, Z_star = resolver_modelo_utopia(0.0, e2sfca_p, dados)
    Ef_star = max(Ef_star, config.EPSILON)
    Z_star = max(Z_star, config.EPSILON)

    print(f"Eficiência máxima (α=1): {Ef_star:.6f} | Equidade máxima (α=0): {Z_star:.6f}")

    print("Montando modelo final...")
    m = gp.Model("E2SFCA_Sergipe")
    y = m.addVars(e2sfca_p["M_n"], vtype=GRB.BINARY, name="y")
    x = m.addVars(e2sfca_p["M_n"], vtype=GRB.INTEGER, name="x")
    Z = m.addVar(vtype=GRB.CONTINUOUS, name="Z")

    def expr_A_i(i):
        expr = gp.LinExpr()
        for j in e2sfca_p["M_i"].get(i, []):
            w = e2sfca_p["w_df"].loc[i, j]
            denom = e2sfca_p["DEMANDA_PONDERADA"][j]
            if j in e2sfca_p["M_n"]:
                expr.add(x[j], w / denom)
            elif j in e2sfca_p["M_e"]:
                expr.addConstant(w * dados["x_hat"][j] / denom)
        return expr

    eficiencia_norm = (1.0 / (len(e2sfca_p["N"]) * Ef_star)) * quicksum(e2sfca_p["d_shortage"][i] * expr_A_i(i) for i in e2sfca_p["N"])
    equidade_norm = (1.0 / Z_star) * Z
    m.setObjective(config.ALPHA * eficiencia_norm + (1 - config.ALPHA) * equidade_norm, GRB.MAXIMIZE)

    for i in e2sfca_p["nos_com_candidato"]:
        m.addConstr(dados["d_i"][i] * expr_A_i(i) >= Z)
    for j in e2sfca_p["M_n"]:
        m.addConstr(x[j] >= config.K_MIN * y[j])
        m.addConstr(x[j] <= config.K_MAX * y[j])
        
    m.addConstr(quicksum(y[j] for j in e2sfca_p["M_n"]) == config.P_MAX)
    m.addConstr(quicksum(x[j] for j in e2sfca_p["M_n"]) == config.Q_MAX)

    m.setParam('TimeLimit', 600)
    m.setParam('MIPGap', 0.001)
    m.optimize()

    # O código de exportação dos CSVs iria aqui (exatamente igual ao original).
    if m.status in (GRB.OPTIMAL, GRB.TIME_LIMIT) and m.SolCount > 0:
        print(f"\nOtimização concluída! Objetivo: {m.objVal:.6f}")
        # Coloque a geração dos DataFrames de saída aqui!

if __name__ == "__main__":
    rodar_otimizacao()
