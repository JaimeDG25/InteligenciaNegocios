import numpy as np
import pandas as pd

# -----------------------------
# PARÁMETROS DEL PROBLEMA
# -----------------------------
SEATS_FIRST = 50
SEATS_ECON = 190

PRICE_FIRST = 600
PRICE_ECON = 300

P_SHOW_FIRST = 0.93
P_SHOW_ECON = 0.96

PENAL_FIRST = 500
PENAL_ECON = 200

MEAN_DEMAND_FIRST = 50
MEAN_DEMAND_ECON = 200

# Sobreventas permitidas
Sobreventa_Primera = [0, 5, 10]
Sobreventa_Economica = [0, 5, 10, 15, 20, 25]

# Número de simulaciones por política
N = 100000


# -----------------------------
# FUNCIÓN QUE SIMULA 1 POLÍTICA
# -----------------------------
def simulate_policy(first_over, econ_over, N=100000):

    profits = []
    denied_first_list = []
    denied_econ_list = []

    for _ in range(N):

        # 1. Demanda
        demand_first = np.random.poisson(MEAN_DEMAND_FIRST)
        demand_econ = np.random.poisson(MEAN_DEMAND_ECON)

        # 2. Boletos vendidos (limitados por el overbooking)
        sold_first = min(demand_first, SEATS_FIRST + first_over)
        sold_econ = min(demand_econ, SEATS_ECON + econ_over)

        # 3. Pasajeros que llegan
        arrive_first = np.random.binomial(sold_first, P_SHOW_FIRST)
        arrive_econ = np.random.binomial(sold_econ, P_SHOW_ECON)

        # 4. Asignación de asientos

        # ---- Primera clase ----
        if arrive_first <= SEATS_FIRST:
            denied_first = 0
            free_first = SEATS_FIRST - arrive_first
        else:
            denied_first = arrive_first - SEATS_FIRST
            free_first = 0

        # ---- Económica ----
        if arrive_econ <= SEATS_ECON + free_first:
            denied_econ = 0
        else:
            denied_econ = arrive_econ - (SEATS_ECON + free_first)

        # Registrar denegados
        denied_first_list.append(denied_first)
        denied_econ_list.append(denied_econ)

        # 5. Ingresos por venta
        revenue = sold_first * PRICE_FIRST + sold_econ * PRICE_ECON

        # 6. Costos por no-shows
        noshow_first = sold_first - arrive_first
        noshow_econ = sold_econ - arrive_econ

        refund_first = noshow_first * PRICE_FIRST  # reembolso total
        refund_econ = 0  # no hay reembolso en económica

        # 7. Costos por pasajeros negados
        penalty_first = denied_first * (PRICE_FIRST + PENAL_FIRST)
        penalty_econ = denied_econ * (PRICE_ECON + PENAL_ECON)

        # 8. Ganancia final del vuelo
        profit = revenue - refund_first - refund_econ - penalty_first - penalty_econ
        profits.append(profit)

    # Retorno de estadísticas
    return {
        "first_over": first_over,
        "econ_over": econ_over,
        "avg_profit": np.mean(profits),
        "avg_denied_first": np.mean(denied_first_list),
        "avg_denied_econ": np.mean(denied_econ_list)
    }


# -----------------------------
# SIMULAR LAS 18 POLÍTICAS
# -----------------------------
results = []

for fo in Sobreventa_Primera:
    for eo in Sobreventa_Economica:
        print(f"Simulando política -> Primera: {fo}, Económica: {eo}")
        results.append(simulate_policy(fo, eo, N))

df = pd.DataFrame(results)


# -----------------------------
# RESULTADOS
# -----------------------------
print("\n===== RESULTADOS COMPLETOS =====")
print(df)

print("\n===== MEJOR POLÍTICA (mayor ganancia promedio) =====")
best = df.loc[df["avg_profit"].idxmax()]
print(best)

print("\n===== MEJOR POLÍTICA CUANDO first_over = 0 =====")
best_no_first_over = df[df["first_over"] == 0].loc[df[df["first_over"] == 0]["avg_profit"].idxmax()]
print(best_no_first_over)
