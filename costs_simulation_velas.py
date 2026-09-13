"""
costs_simulation_velas.py
El forward return positivo no es lo mismo que una estrategia operable
-- la lección de SOL/LINK. Aquí simulamos entrar en el cierre del día
de la señal, mantener 10 días, y salir en el cierre, con un coste de
ida y vuelta conservador para un ETF tan líquido como SPY (más alto
del que probablemente pagarías de verdad, para no sesgar a favor).

Coste usado: 0.05% de ida y vuelta -- bastante por encima de lo que
cuesta operar SPY con un broker moderno (comisión ~0, spread mínimo),
a propósito, para que el resultado sea creíble incluso siendo pesimista.

Uso:
    python3 costs_simulation_velas.py
"""

import pandas as pd
import numpy as np
from reality_check import bootstrap_mean_confidence_interval

TICKER = "SPY"
VOLUME_MA_PERIOD = 20
VOLUME_THRESHOLD = 1.2
HORIZONTE = 10
COSTE_IDA_Y_VUELTA = 0.0005  # 0.05%, conservador para un ETF muy líquido


def cargar_precio(ticker: str) -> pd.DataFrame:
    import yfinance as yf
    df = yf.Ticker(ticker).history(period="max")
    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None).dt.normalize()
    return df[["Date", "Open", "High", "Low", "Close", "Volume"]].sort_values("Date").reset_index(drop=True)


def detectar_ambos_patrones(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ayer_open = df["Open"].shift(1)
    ayer_close = df["Close"].shift(1)
    ayer_bajista = ayer_close < ayer_open
    hoy_alcista = df["Close"] > df["Open"]

    df["es_harami"] = (
        ayer_bajista & hoy_alcista &
        (df["Open"] >= ayer_close) & (df["Close"] <= ayer_open)
    )

    punto_medio_ayer = (ayer_open + ayer_close) / 2
    df["es_piercing"] = (
        ayer_bajista & hoy_alcista &
        (df["Open"] < ayer_close) &
        (df["Close"] > punto_medio_ayer) &
        (df["Close"] < ayer_open)
    )

    df["vol_ma"] = df["Volume"].rolling(VOLUME_MA_PERIOD).mean()
    df["volumen_alto"] = df["Volume"] > (VOLUME_THRESHOLD * df["vol_ma"])
    df["es_harami_sin_volumen"] = df["es_harami"] & (~df["volumen_alto"])
    df["es_piercing_sin_volumen"] = df["es_piercing"] & (~df["volumen_alto"])

    df[f"fwd_{HORIZONTE}d"] = df["Close"].shift(-HORIZONTE) / df["Close"] - 1
    return df


if __name__ == "__main__":
    print(f"Descargando histórico de {TICKER}...")
    try:
        import yfinance  # noqa: F401
    except ImportError:
        print("Falta yfinance. Corre: pip install yfinance --break-system-packages")
        raise SystemExit

    precio_df = cargar_precio(TICKER)
    df = detectar_ambos_patrones(precio_df)
    print(f"{len(df)} días totales.\n")
    print(f"Coste de ida y vuelta aplicado: {COSTE_IDA_Y_VUELTA*100:.2f}%\n")

    for columna, nombre in [("es_harami_sin_volumen", "HARAMI SIN VOLUMEN"),
                             ("es_piercing_sin_volumen", "PIERCING SIN VOLUMEN")]:
        eventos = df[df[columna]].dropna(subset=[f"fwd_{HORIZONTE}d"])
        retornos_brutos = eventos[f"fwd_{HORIZONTE}d"].values
        retornos_netos = retornos_brutos - COSTE_IDA_Y_VUELTA

        ganadoras = retornos_netos[retornos_netos > 0]
        perdedoras = retornos_netos[retornos_netos < 0]
        win_rate = (retornos_netos > 0).mean() * 100
        profit_factor = ganadoras.sum() / abs(perdedoras.sum()) if len(perdedoras) > 0 else float("inf")

        print(f"=== {nombre} ===")
        print(f"n={len(retornos_netos)}")
        print(f"Retorno bruto medio: {retornos_brutos.mean()*100:+.3f}%")
        print(f"Retorno NETO medio (tras coste): {retornos_netos.mean()*100:+.3f}%")
        print(f"Win rate neto: {win_rate:.1f}%")
        print(f"Profit factor neto: {profit_factor:.2f}")

        resultado = bootstrap_mean_confidence_interval(retornos_netos, mean_block_length=3.0,
                                                         n_bootstrap=3000, random_state=1)
        ic_low, ic_high = resultado["intervalo_confianza"]
        print(f"IC 95% del retorno neto: [{ic_low*100:+.3f}%, {ic_high*100:+.3f}%]  "
              f"significativo={resultado['significativo']}\n")

    print("--- Cómo leer esto ---")
    print("Si el retorno neto sigue siendo significativo y el profit factor > 1, la estrategia")
    print("sobrevive el roce con el mundo real. Si se cae al restar un coste tan pequeño, es la")
    print("misma trampa que SOL/LINK: ventaja estadística real, sin margen suficiente para operarla.")
