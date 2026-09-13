"""
harami_piercing_volume.py
Los otros dos patrones que la literatura señalaba como prometedores
con confirmación de volumen, tras el resultado negativo (e invertido)
del Bullish Engulfing.

Bullish Harami: vela 1 (ayer) bajista y grande; vela 2 (hoy) alcista,
con su cuerpo COMPLETAMENTE DENTRO del cuerpo de ayer (lo contrario
del engulfing: pequeña dentro de grande, no grande envolviendo a
pequeña).

Piercing Line: vela 1 (ayer) bajista; vela 2 (hoy) abre con hueco a la
baja (por debajo del cierre de ayer), pero cierra por encima de la
mitad del cuerpo de ayer, sin llegar a superar la apertura de ayer
(si la superara, sería un engulfing, no un piercing).

Misma metodología que el script anterior: comparar forward returns
entre "con volumen alto" y "sin volumen alto" para cada patrón.

Uso:
    python3 harami_piercing_volume.py
"""

import pandas as pd
import numpy as np
from reality_check import bootstrap_mean_confidence_interval

TICKER = "SPY"
VOLUME_MA_PERIOD = 20
VOLUME_THRESHOLD = 1.2
HORIZONTES = [5, 10, 20]


def cargar_precio(ticker: str) -> pd.DataFrame:
    import yfinance as yf
    df = yf.Ticker(ticker).history(period="max")
    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None).dt.normalize()
    return df[["Date", "Open", "High", "Low", "Close", "Volume"]].sort_values("Date").reset_index(drop=True)


def detectar_patrones(df: pd.DataFrame) -> pd.DataFrame:
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

    for h in HORIZONTES:
        df[f"fwd_{h}d"] = df["Close"].shift(-h) / df["Close"] - 1

    return df


def analizar_patron(df: pd.DataFrame, columna_patron: str, nombre_patron: str):
    patron = df[df[columna_patron]]
    con_volumen = patron[patron["volumen_alto"]]
    sin_volumen = patron[~patron["volumen_alto"]]

    print(f"\n{'='*60}")
    print(f"=== {nombre_patron} ===")
    print(f"{'='*60}")
    print(f"Total detectados: {len(patron)}  "
          f"(con volumen alto: {len(con_volumen)}, sin: {len(sin_volumen)})\n")

    for nombre, subset in [("CON volumen alto", con_volumen), ("SIN volumen alto", sin_volumen)]:
        print(f"--- {nombre} ---")
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


if __name__ == "__main__":
    print(f"Descargando histórico de {TICKER}...")
    try:
        import yfinance  # noqa: F401
    except ImportError:
        print("Falta yfinance. Corre: pip install yfinance --break-system-packages")
        raise SystemExit

    precio_df = cargar_precio(TICKER)
    df = detectar_patrones(precio_df)
    print(f"{len(df)} días de trading. {df['Date'].min().date()} -> {df['Date'].max().date()}")

    analizar_patron(df, "es_harami", "BULLISH HARAMI")
    analizar_patron(df, "es_piercing", "PIERCING LINE")

    print(f"\n{'='*60}")
    print("--- Aviso sobre búsqueda múltiple ---")
    print("Con este script + el de Bullish Engulfing anterior: 3 patrones x 2 grupos x 3")
    print("horizontes = 18 tests en total sobre la hipótesis 'velas + volumen'. Esperaríamos")
    print("~0.9 significativos por puro azar al 5%. Cuenta cuántos salen en total antes de")
    print("creerte ningún resultado aislado.")
