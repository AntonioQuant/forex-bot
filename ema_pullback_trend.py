"""
ema_pullback_trend.py
La idea original de Antonio: no el cruce de EMAs en sí (ya lo
descartamos hace semanas en cripto) -- sino la entrada de "vuelta a
tendencia": el precio toca o cae por debajo de la EMA corta y luego
la vuelve a cruzar al alza, MIENTRAS la EMA corta sigue por encima de
la larga (tendencia de fondo intacta). Es una entrada de "comprar el
retroceso dentro de una tendencia ya confirmada", distinta en
naturaleza del cruce puro.

Mismas EMAs que usamos en todo el proyecto de cripto (21/55).

Uso:
    python3 ema_pullback_trend.py
"""

import pandas as pd
import numpy as np
from reality_check import bootstrap_mean_confidence_interval

TICKER = "SPY"
EMA_FAST = 21
EMA_SLOW = 55
HORIZONTES = [5, 10, 20]
COSTE_IDA_Y_VUELTA = 0.0005


def cargar_precio(ticker: str) -> pd.DataFrame:
    import yfinance as yf
    df = yf.Ticker(ticker).history(period="max")
    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None).dt.normalize()
    return df[["Date", "Close"]].sort_values("Date").reset_index(drop=True)


def detectar_pullback(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ema_fast"] = df["Close"].ewm(span=EMA_FAST, adjust=False).mean()
    df["ema_slow"] = df["Close"].ewm(span=EMA_SLOW, adjust=False).mean()

    tendencia_alcista = df["ema_fast"] > df["ema_slow"]
    ayer_bajo_ema_fast = df["Close"].shift(1) < df["ema_fast"].shift(1)
    hoy_sobre_ema_fast = df["Close"] > df["ema_fast"]

    df["es_pullback_entry"] = tendencia_alcista & ayer_bajo_ema_fast & hoy_sobre_ema_fast

    for h in HORIZONTES:
        df[f"fwd_{h}d"] = df["Close"].shift(-h) / df["Close"] - 1

    return df


if __name__ == "__main__":
    print(f"Descargando histórico de {TICKER}...")
    try:
        import yfinance  # noqa: F401
    except ImportError:
        print("Falta yfinance. Corre: pip install yfinance --break-system-packages")
        raise SystemExit

    precio_df = cargar_precio(TICKER)
    df = detectar_pullback(precio_df)
    print(f"{len(df)} días totales. {df['Date'].min().date()} -> {df['Date'].max().date()}\n")

    eventos_totales = df[df["es_pullback_entry"]]
    print(f"Señales de vuelta a tendencia detectadas: {len(eventos_totales)}\n")

    for h in HORIZONTES:
        eventos = df[df["es_pullback_entry"]].dropna(subset=[f"fwd_{h}d"])
        if len(eventos) < 10:
            print(f"+{h}d: muestra insuficiente ({len(eventos)})")
            continue

        retornos_brutos = eventos[f"fwd_{h}d"].values
        retornos_netos = retornos_brutos - COSTE_IDA_Y_VUELTA

        ganadoras = retornos_netos[retornos_netos > 0]
        perdedoras = retornos_netos[retornos_netos < 0]
        win_rate = (retornos_netos > 0).mean() * 100
        profit_factor = ganadoras.sum() / abs(perdedoras.sum()) if len(perdedoras) > 0 else float("inf")

        resultado = bootstrap_mean_confidence_interval(retornos_netos, mean_block_length=3.0,
                                                         n_bootstrap=3000, random_state=h)
        ic_low, ic_high = resultado["intervalo_confianza"]

        print(f"=== +{h}d ===")
        print(f"n={len(retornos_netos)}  bruto={retornos_brutos.mean()*100:+.3f}%  "
              f"neto={retornos_netos.mean()*100:+.3f}%")
        print(f"Win rate neto: {win_rate:.1f}%   Profit factor neto: {profit_factor:.2f}")
        print(f"IC 95% neto: [{ic_low*100:+.3f}%, {ic_high*100:+.3f}%]  "
              f"significativo={resultado['significativo']}\n")

    print("--- Aviso ---")
    print("3 horizontes probados -- esperaríamos ~0.15 significativos por azar al 5%.")
