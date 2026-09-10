"""
shock_move_analysis.py
Tras un movimiento brusco de precio (varias desviaciones típicas por
encima de lo normal), ¿el mercado tiende a seguir en esa dirección
(continuación/momentum) o a revertir (mean-reversion)? Se separan
subidas bruscas de bajadas bruscas — el mercado no tiene por qué
comportarse igual ante el pánico que ante la euforia.

Umbral RELATIVO a la volatilidad de los últimos 20 días, no un % fijo
— así el criterio de "brusco" se adapta solo a mercados tranquilos o
turbulentos, en vez de disparar demasiado en unos y nunca en otros.

Usa el índice ^GSPC (S&P 500), no el ETF SPY, para tener el máximo
histórico posible vía yfinance.

Uso:
    python3 shock_move_analysis.py
"""

import pandas as pd
import numpy as np
from reality_check import bootstrap_mean_confidence_interval

TICKER = "^GSPC"
VENTANA_VOLATILIDAD = 20
UMBRAL_DESVIACIONES = 2.5  # cuántas desv. típicas para considerar "brusco"
HORIZONTES = [1, 3, 5, 10]  # días hábiles hacia delante a medir


def cargar_precio(ticker: str) -> pd.DataFrame:
    import yfinance as yf
    df = yf.Ticker(ticker).history(period="max")
    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None).dt.normalize()
    return df[["Date", "Close"]].sort_values("Date").reset_index(drop=True)


def detectar_shocks(precio_df: pd.DataFrame, ventana: int, umbral: float) -> pd.DataFrame:
    df = precio_df.copy()
    df["retorno"] = df["Close"].pct_change()
    df["vol_movil"] = df["retorno"].rolling(ventana).std()
    df["z_score"] = df["retorno"] / df["vol_movil"]
    df["es_shock_alcista"] = df["z_score"] > umbral
    df["es_shock_bajista"] = df["z_score"] < -umbral

    for h in HORIZONTES:
        # retorno acumulado desde el propio día del shock hasta h días después
        # (definición estándar de "cumulative abnormal return" en estudios de eventos)
        df[f"fwd_{h}d"] = df["Close"].shift(-h) / df["Close"] - 1

    return df


if __name__ == "__main__":
    print(f"Descargando histórico completo de {TICKER}...")
    try:
        import yfinance  # noqa: F401
    except ImportError:
        print("Falta yfinance. Corre: pip install yfinance --break-system-packages")
        raise SystemExit

    precio_df = cargar_precio(TICKER)
    print(f"{len(precio_df)} días de trading. "
          f"{precio_df['Date'].min().date()} -> {precio_df['Date'].max().date()}\n")

    df = detectar_shocks(precio_df, VENTANA_VOLATILIDAD, UMBRAL_DESVIACIONES)

    shocks_alcistas = df[df["es_shock_alcista"]].dropna(subset=[f"fwd_{h}d" for h in HORIZONTES])
    shocks_bajistas = df[df["es_shock_bajista"]].dropna(subset=[f"fwd_{h}d" for h in HORIZONTES])

    print(f"Umbral: movimientos de más de {UMBRAL_DESVIACIONES} desviaciones típicas "
          f"(ventana móvil de {VENTANA_VOLATILIDAD} días)")
    print(f"Shocks alcistas detectados: {len(shocks_alcistas)}")
    print(f"Shocks bajistas detectados: {len(shocks_bajistas)}\n")

    for nombre, subset in [("ALCISTAS (tras una subida brusca)", shocks_alcistas),
                            ("BAJISTAS (tras una caída brusca)", shocks_bajistas)]:
        print(f"=== SHOCKS {nombre} — retorno futuro, por horizonte ===")
        for h in HORIZONTES:
            retornos = subset[f"fwd_{h}d"].values
            resultado = bootstrap_mean_confidence_interval(retornos, mean_block_length=3.0,
                                                             n_bootstrap=2000, random_state=h)
            ic_low, ic_high = resultado["intervalo_confianza"]
            interpretacion = ("CONTINUACIÓN" if resultado["media_observada"] > 0 and "ALCISTAS" in nombre
                               else "REVERSIÓN" if resultado["media_observada"] < 0 and "ALCISTAS" in nombre
                               else "REVERSIÓN (rebote)" if resultado["media_observada"] > 0 and "BAJISTAS" in nombre
                               else "CONTINUACIÓN (sigue cayendo)")
            print(f"  +{h}d: media={resultado['media_observada']*100:+.3f}%  "
                  f"IC=[{ic_low*100:+.3f}%, {ic_high*100:+.3f}%]  "
                  f"significativo={resultado['significativo']}  ({interpretacion})")
        print()

    print("--- Aviso sobre búsqueda múltiple ---")
    print(f"Se han hecho {len(HORIZONTES)*2} tests a la vez (4 horizontes x 2 direcciones).")
    print(f"Con eso, esperaríamos ~{len(HORIZONTES)*2*0.05:.1f} 'significativos' solo por azar al 5%.")
    print("Si aparece 1 solo resultado significativo aislado, trátalo con la misma sospecha que")
    print("aplicamos a los pares de cointegración que salieron 'bien' por casualidad.")
