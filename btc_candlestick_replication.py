"""
btc_candlestick_replication.py
¿Se replica el hallazgo de Harami y Piercing Line (sin volumen alto)
en un activo con una estructura de mercado completamente distinta?
BTC opera 24/7, sin apertura/cierre de sesión como una bolsa
tradicional — así que los "huecos" que definen estos patrones ocurren
de forma distinta. Si el patrón se replica también aquí, es indicio
de algo más universal (psicología de mercado) que de una peculiaridad
de cómo funciona SPY en concreto.

Mismo umbral de volumen, mismo horizonte (+10d), misma metodología
exacta que en SPY, para que la comparación sea justa.

Uso:
    python3 btc_candlestick_replication.py
"""

import pandas as pd
import numpy as np
from reality_check import bootstrap_mean_confidence_interval

TICKER = "BTC-USD"
VOLUME_MA_PERIOD = 20
VOLUME_THRESHOLD = 1.2
HORIZONTE = 10
COSTE_IDA_Y_VUELTA = 0.0011  # 0.055% x 2, coherente con lo usado en crypto_bot


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
    print(f"{len(df)} días totales. {df['Date'].min().date()} -> {df['Date'].max().date()}\n")
    print(f"Aviso: BTC opera 24/7 -- 'ayer' y 'hoy' aquí son velas diarias por convención")
    print(f"(medianoche UTC), no sesiones de mercado reales con apertura/cierre.\n")

    for columna, nombre in [("es_harami_sin_volumen", "HARAMI SIN VOLUMEN"),
                             ("es_piercing_sin_volumen", "PIERCING SIN VOLUMEN")]:
        eventos = df[df[columna]].dropna(subset=[f"fwd_{HORIZONTE}d"])
        if len(eventos) < 10:
            print(f"=== {nombre} ===\nMuestra insuficiente ({len(eventos)})\n")
            continue

        retornos_brutos = eventos[f"fwd_{HORIZONTE}d"].values
        retornos_netos = retornos_brutos - COSTE_IDA_Y_VUELTA

        ganadoras = retornos_netos[retornos_netos > 0]
        perdedoras = retornos_netos[retornos_netos < 0]
        win_rate = (retornos_netos > 0).mean() * 100
        profit_factor = ganadoras.sum() / abs(perdedoras.sum()) if len(perdedoras) > 0 else float("inf")

        print(f"=== {nombre} (BTC) ===")
        print(f"n={len(retornos_netos)}")
        print(f"Retorno bruto medio: {retornos_brutos.mean()*100:+.3f}%")
        print(f"Retorno NETO medio: {retornos_netos.mean()*100:+.3f}%")
        print(f"Win rate neto: {win_rate:.1f}%   Profit factor neto: {profit_factor:.2f}")

        resultado = bootstrap_mean_confidence_interval(retornos_netos, mean_block_length=3.0,
                                                         n_bootstrap=3000, random_state=1)
        ic_low, ic_high = resultado["intervalo_confianza"]
        print(f"IC 95% neto: [{ic_low*100:+.3f}%, {ic_high*100:+.3f}%]  "
              f"significativo={resultado['significativo']}\n")

    print("--- Cómo leer esto ---")
    print("Si ambos patrones (o al menos uno) se replican aquí -- significativos y rentables")
    print("netos de costes -- es la señal más fuerte posible de que esto es un fenómeno real")
    print("del comportamiento del mercado, no una peculiaridad de SPY. Si no se replica en")
    print("absoluto, sigue siendo un hallazgo válido en acciones, pero acotado a esa estructura")
    print("de mercado concreta -- no universal.")
