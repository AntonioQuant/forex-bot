"""
shock_continuation_stability.py
La continuación tras subidas bruscas salió significativa en +3d, +5d
y +10d, con casi un siglo de datos agregados. Pero un siglo agregado
puede esconder que el efecto solo viva en una era concreta (mercados
de los años 30-50, muy distintos estructuralmente a hoy) — la misma
comprobación que le hicimos a la cointegración con BTC/ETH antes de
creérnosla.

Se divide el histórico en 6 tramos cronológicos de tamaño similar
(mismo criterio que usamos en todo el proyecto de cripto) y se repite
el test de significancia en cada uno, para el horizonte +5d (el punto
medio de los tres que salieron significativos).

Uso:
    python3 shock_continuation_stability.py
"""

import pandas as pd
import numpy as np
from reality_check import bootstrap_mean_confidence_interval

TICKER = "^GSPC"
VENTANA_VOLATILIDAD = 20
UMBRAL_DESVIACIONES = 2.5
HORIZONTE = 5
N_TRAMOS = 6


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


def split_cronologico(df: pd.DataFrame, n: int):
    size = len(df) // n
    chunks = []
    for i in range(n):
        start = i * size
        end = (i + 1) * size if i < n - 1 else len(df)
        chunks.append(df.iloc[start:end].reset_index(drop=True))
    return chunks


if __name__ == "__main__":
    print(f"Descargando histórico completo de {TICKER}...")
    try:
        import yfinance  # noqa: F401
    except ImportError:
        print("Falta yfinance. Corre: pip install yfinance --break-system-packages")
        raise SystemExit

    precio_df = cargar_precio(TICKER)
    df = detectar_shocks_alcistas(precio_df)
    print(f"{len(df)} días totales. {df['Date'].min().date()} -> {df['Date'].max().date()}\n")

    tramos = split_cronologico(df, N_TRAMOS)

    print(f"=== ESTABILIDAD DEL PATRÓN 'CONTINUACIÓN A +{HORIZONTE}D TRAS SUBIDA BRUSCA' POR TRAMOS ===\n")
    resumen = []
    for idx, tramo in enumerate(tramos, start=1):
        fecha_ini, fecha_fin = tramo["Date"].min().date(), tramo["Date"].max().date()
        shocks_tramo = tramo[tramo["es_shock_alcista"]].dropna(subset=[f"fwd_{HORIZONTE}d"])

        if len(shocks_tramo) < 5:
            print(f"Tramo {idx}/{N_TRAMOS} ({fecha_ini} a {fecha_fin}): "
                  f"solo {len(shocks_tramo)} shocks, muestra insuficiente para un test fiable.\n")
            continue

        retornos = shocks_tramo[f"fwd_{HORIZONTE}d"].values
        resultado = bootstrap_mean_confidence_interval(retornos, mean_block_length=3.0,
                                                         n_bootstrap=1500, random_state=idx)
        ic_low, ic_high = resultado["intervalo_confianza"]

        print(f"Tramo {idx}/{N_TRAMOS} ({fecha_ini} a {fecha_fin}): "
              f"n_shocks={len(shocks_tramo)}  media={resultado['media_observada']*100:+.3f}%  "
              f"IC=[{ic_low*100:+.3f}%, {ic_high*100:+.3f}%]  significativo={resultado['significativo']}\n")

        resumen.append({"tramo": idx, "fechas": f"{fecha_ini} a {fecha_fin}",
                         "n_shocks": len(shocks_tramo), "media_%": resultado["media_observada"]*100,
                         "significativo": resultado["significativo"]})

    resumen_df = pd.DataFrame(resumen)
    print("=== RESUMEN ===")
    print(resumen_df.to_string(index=False))

    n_positivos = (resumen_df["media_%"] > 0).sum()
    n_significativos = resumen_df["significativo"].sum()
    print(f"\nTramos con media positiva (misma dirección que el agregado): {n_positivos}/{len(resumen_df)}")
    print(f"Tramos individualmente significativos: {n_significativos}/{len(resumen_df)}")
    print("\nBuscamos: la mayoría de tramos en la misma dirección, no solo 1-2 tramos cargando todo")
    print("el resultado agregado — la misma trampa en la que casi caímos con BTC/ETH.")
