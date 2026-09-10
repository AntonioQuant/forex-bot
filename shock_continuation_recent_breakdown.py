"""
shock_continuation_recent_breakdown.py
El patrón de continuación tras subidas bruscas se apagó en el tramo
más reciente (2010-2026). ¿Se diluye poco a poco, o hay un punto de
quiebre concreto? Se divide ese tramo en ventanas más finas para
verlo con más detalle — con el aviso honesto de que la muestra ya
era pequeña (26 shocks) y al partirla en más trozos, esto es
exploratorio/descriptivo, no un test formal con la misma potencia
que los anteriores.

Uso:
    python3 shock_continuation_recent_breakdown.py
"""

import pandas as pd
import numpy as np

TICKER = "^GSPC"
VENTANA_VOLATILIDAD = 20
UMBRAL_DESVIACIONES = 2.5
HORIZONTE = 5
FECHA_INICIO_TRAMO_RECIENTE = "2010-04-05"

VENTANAS_FINAS = [
    ("2010-04-05", "2015-12-31", "2010-2015 (post-crisis, QE)"),
    ("2016-01-01", "2019-12-31", "2016-2019 (expansión tardía)"),
    ("2020-01-01", "2020-12-31", "2020 (pandemia, aislado)"),
    ("2021-01-01", "2022-12-31", "2021-2022 (subida de tipos)"),
    ("2023-01-01", "2026-09-04", "2023-2026 (más reciente)"),
]


def cargar_precio(ticker: str) -> pd.DataFrame:
    import yfinance as yf
    df = yf.Ticker(ticker).history(period="max")
    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None).dt.normalize()
    return df[["Date", "Close"]].sort_values("Date").reset_index(drop=True)


def detectar_shocks_alcistas(precio_df: pd.DataFrame) -> pd.DataFrame:
    df = precio_df.copy()
    df["retorno"] = df["Close"].pct_change()
    df["vol_movil"] = df["retorno"].rolling(VENTANA_VOLATILIDAD).std()
    df["z_score"] = df["retorno"] / df["vol_movil"]
    df["es_shock_alcista"] = df["z_score"] > UMBRAL_DESVIACIONES
    df[f"fwd_{HORIZONTE}d"] = df["Close"].shift(-HORIZONTE) / df["Close"] - 1
    return df


if __name__ == "__main__":
    print(f"Descargando histórico completo de {TICKER}...")
    try:
        import yfinance  # noqa: F401
    except ImportError:
        print("Falta yfinance. Corre: pip install yfinance --break-system-packages")
        raise SystemExit

    precio_df = cargar_precio(TICKER)
    df = detectar_shocks_alcistas(precio_df)

    print(f"=== DESGLOSE FINO DEL TRAMO RECIENTE (desde {FECHA_INICIO_TRAMO_RECIENTE}) ===")
    print("(exploratorio — muestras pequeñas, no un test formal como los anteriores)\n")

    resumen = []
    for fecha_ini, fecha_fin, etiqueta in VENTANAS_FINAS:
        ventana = df[(df["Date"] >= fecha_ini) & (df["Date"] <= fecha_fin)]
        shocks = ventana[ventana["es_shock_alcista"]].dropna(subset=[f"fwd_{HORIZONTE}d"])

        if len(shocks) == 0:
            print(f"{etiqueta}: sin shocks detectados en esta ventana.\n")
            continue

        media = shocks[f"fwd_{HORIZONTE}d"].mean()
        positivos = (shocks[f"fwd_{HORIZONTE}d"] > 0).sum()
        print(f"{etiqueta}: n={len(shocks)}  media={media*100:+.3f}%  "
              f"positivos={positivos}/{len(shocks)}")

        resumen.append({"ventana": etiqueta, "n_shocks": len(shocks),
                         "media_%": media*100, "positivos": f"{positivos}/{len(shocks)}"})

    print("\n=== RESUMEN ===")
    print(pd.DataFrame(resumen).to_string(index=False))

    print("\n--- Nota honesta ---")
    print("Con 4-8 shocks por ventana, cualquier patrón aquí es más ilustrativo que concluyente.")
    print("Sirve para ver SI hay un punto de quiebre visible (ej. la pandemia, o el ciclo de subida")
    print("de tipos), no para confirmar estadísticamente nada nuevo.")
