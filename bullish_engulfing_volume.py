"""
bullish_engulfing_volume.py
Patrón de vela envolvente alcista (Bullish Engulfing): el cuerpo de la
vela de hoy, alcista, envuelve por completo al cuerpo de la vela de
ayer, bajista. La literatura académica es mixta sobre si esto predice
algo por sí solo — pero un estudio (mercado chino) encontró que SÍ
funciona mejor quando va acompañado de volumen por encima de la media,
sugiriendo que el volumen separa la señal real del ruido.

Se prueban dos grupos por separado: engulfing CON volumen alto,
engulfing SIN volumen alto — para ver si el matiz de la literatura
se sostiene con datos propios.

Uso:
    python3 bullish_engulfing_volume.py
"""

import pandas as pd
import numpy as np
from reality_check import bootstrap_mean_confidence_interval

TICKER = "SPY"
VOLUME_MA_PERIOD = 20
VOLUME_THRESHOLD = 1.2  # volumen "alto" = 20% por encima de su media de 20 días
HORIZONTES = [5, 10, 20]


def cargar_precio(ticker: str) -> pd.DataFrame:
    import yfinance as yf
    df = yf.Ticker(ticker).history(period="max")
    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None).dt.normalize()
    return df[["Date", "Open", "High", "Low", "Close", "Volume"]].sort_values("Date").reset_index(drop=True)


def detectar_bullish_engulfing(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cuerpo_hoy_alcista = df["Close"] > df["Open"]
    cuerpo_ayer_bajista = df["Close"].shift(1) < df["Open"].shift(1)
    envuelve = (df["Open"] < df["Close"].shift(1)) & (df["Close"] > df["Open"].shift(1))

    df["es_engulfing"] = cuerpo_hoy_alcista & cuerpo_ayer_bajista & envuelve

    df["vol_ma"] = df["Volume"].rolling(VOLUME_MA_PERIOD).mean()
    df["volumen_alto"] = df["Volume"] > (VOLUME_THRESHOLD * df["vol_ma"])

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
    df = detectar_bullish_engulfing(precio_df)

    print(f"{len(df)} días de trading. {df['Date'].min().date()} -> {df['Date'].max().date()}\n")

    engulfing = df[df["es_engulfing"]]
    con_volumen = engulfing[engulfing["volumen_alto"]]
    sin_volumen = engulfing[~engulfing["volumen_alto"]]

    print(f"Total Bullish Engulfing detectados: {len(engulfing)}")
    print(f"  Con volumen alto (>{VOLUME_THRESHOLD}x su media de {VOLUME_MA_PERIOD}d): {len(con_volumen)}")
    print(f"  Sin volumen alto: {len(sin_volumen)}\n")

    for nombre, subset in [("CON volumen alto", con_volumen), ("SIN volumen alto", sin_volumen)]:
        print(f"=== {nombre} ===")
        for h in HORIZONTES:
            datos = subset.dropna(subset=[f"fwd_{h}d"])
            if len(datos) < 10:
                print(f"  +{h}d: muestra insuficiente ({len(datos)})")
                continue
            retornos = datos[f"fwd_{h}d"].values
            resultado = bootstrap_mean_confidence_interval(retornos, mean_block_length=3.0,
                                                             n_bootstrap=2000, random_state=h)
            ic_low, ic_high = resultado["intervalo_confianza"]
            print(f"  +{h}d: n={len(datos)}  media={resultado['media_observada']*100:+.3f}%  "
                  f"IC=[{ic_low*100:+.3f}%, {ic_high*100:+.3f}%]  significativo={resultado['significativo']}")
        print()

    print("--- Aviso ---")
    print("6 tests en total (3 horizontes x 2 grupos). Si solo uno sale significativo de forma")
    print("aislada, la misma sospecha de siempre. Buscamos: el grupo CON volumen mostrando una")
    print("ventaja que el grupo SIN volumen no tiene -- eso confirmaría la pista de la literatura.")
