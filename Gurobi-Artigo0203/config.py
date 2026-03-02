# config.py

# ==========================================
# CAMINHOS DOS ARQUIVOS (Ajuste conforme necessário)
# ==========================================
PATH_ORIGEM_ALVO = 'Downloads/SE_coords_medias_divisoes.csv'
PATH_FACILIDADES = 'Downloads/Hospitais_gerais_CNES.csv'
PATH_MATRIZ_ROTAS = 'matriz_rotas_NOSxFAC.csv'
PATH_DEMANDA_SET = 'setores_populacao_ajustada.csv'
PATH_SETORES_POP = 'Downloads/SE_setores_populacao.csv'

# ==========================================
# PARÂMETROS DO MODELO E2SFCA / GUROBI
# ==========================================
T_0 = 45          # Tempo máximo aceitável de viagem (minutos)
P_MAX = 12        # Número de novas facilidades a abrir
Q_MAX = 1200      # Total de leitos novos a distribuir
K_MIN = 50        # Mínimo de leitos por nova facilidade aberta
K_MAX = 200       # Máximo de leitos por nova facilidade aberta
ALPHA = 0.5       # 0 = só equidade, 1 = só eficiência, 0.5 = balanceado
BETA = 0.09       # Fator de decaimento (w_ij)
EPSILON = 1e-6    # Tolerância para evitar divisão por zero
