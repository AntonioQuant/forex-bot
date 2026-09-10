"""
precursor_volatility_analysis.py
¿Los movimientos bruscos llegan sin aviso, o hay una señal previa
detectable? Se comprueba la hipótesis de la "calma antes de la
tormenta": volatilidad reciente (10 días) inusualmente BAJA respecto
a la de fondo (60 días) en los días previos a un shock, comparado con
un día cualquiera.

No busca predecir DIRECCIÓN (eso ya lo separamos alcista/bajista en
el script anterior) — busca predecir la PROBABILIDAD de que ocurra
un movimiento grande, útil para gestión de riesgo (reducir tamaño de
posición, ajustar stops) aunque no diga hacia dónde.

Uso:
    python3 precursor_volatility_analysis.py
"""

import pandas as pd
import numpy as np
from reality_check import bootstrap_mean_confidence_interval

TICKER = "^GSPC"
VENTANA_VOLATILIDAD_SHOCK = 20
UMBRAL_DESVIACIONES = 2.5
VENTANA_CORTA = 10
VENTANA_LARGA = 60
DIAS_ANTES_A_MIRAR = 5


def cargar_precio(ticker: str) -> pd.DataFrame:
    import yfinance as yf
    df = yf.Ticker(ticker).history(period="max")
    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None).dt.normalize()
    return df[["Date", "Close"]].sort_values("Date").reset_index(drop=True)


def preparar_datos(precio_df: pd.DataFrame) -> pd.DataFrame:
    df = precio_df.copy()
    df["retorno"] = df["Close"].pct_change()

    df["vol_shock"] = df["retorno"].rolling(VENTANA_VOLATILIDAD_SHOCK).std()
    df["z_score"] = df["retorno"] / df["vol_shock"]
    df["es_shock"] = df["z_score"].abs() > UMBRAL_DESVIACIONES

    df["vol_corta"] = df["retorno"].rolling(VENTANA_CORTA).std()
    df["vol_larga"] = df["retorno"].rolling(VENTANA_LARGA).std()
    df["ratio_compresion"] = df["vol_corta"] / df["vol_larga"]

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

    df = preparar_datos(precio_df)

    df["ratio_compresion_previo"] = df["ratio_compresion"].shift(DIAS_ANTES_A_MIRAR)

    shocks = df[df["es_shock"]].dropna(subset=["ratio_compresion_previo"])
    todos_los_dias = df.dropna(subset=["ratio_compresion_previo"])

    print(f"Shocks detectados (>{UMBRAL_DESVIACIONES} desv. típicas, cualquier dirección): {len(shocks)}")
    print(f"Total de días con datos suficientes: {len(todos_los_dias)}\n")

    ratio_antes_de_shocks = shocks["ratio_compresion_previo"].values
    ratio_dia_cualquiera = todos_los_dias["ratio_compresion_previo"].values

    print("=== RATIO DE COMPRESIÓN (vol. 10d / vol. 60d) ===")
    print(f"En días CUALQUIERA: media={ratio_dia_cualquiera.mean():.3f}  "
          f"(1.0 = volatilidad normal, <1 = comprimida, >1 = ya elevada)")
    print(f"{DIAS_ANTES_A_MIRAR} días ANTES de un shock: media={ratio_antes_de_shocks.mean():.3f}\n")

    print("=== SIGNIFICANCIA: ¿la compresión previa a un shock es distinta de un día cualquiera? ===")
    diferencia = ratio_antes_de_shocks - ratio_dia_cualquiera.mean()
    resultado = bootstrap_mean_confidence_interval(diferencia, mean_block_length=3.0,
                                                     n_bootstrap=3000, random_state=1)
    ic_low, ic_high = resultado["intervalo_confianza"]
    print(f"Diferencia media: {resultado['media_observada']:.4f}")
    print(f"Intervalo de confianza 95%: [{ic_low:.4f}, {ic_high:.4f}]")
    print(f"¿Significativamente distinto de cero?: {resultado['significativo']}")

    print("\n--- Cómo leer esto ---")
    print("Si la diferencia es NEGATIVA y significativa: los shocks SÍ tienden a llegar tras un")
    print("periodo de calma anómala (volatilidad comprimida) — un aviso previo real y potencialmente")
    print("útil para reducir tamaño de posición antes de que llegue el golpe.")
    print("Si no es significativa, o es positiva: los shocks llegan sin ese aviso concreto — no")
    print("descarta que exista otra señal, pero esta hipótesis en particular no se sostiene.")
