"""
pead_reconnaissance.py
Antes de construir el análisis de PEAD (Post-Earnings Announcement
Drift): comprobar qué forma tienen los datos de sorpresas de
beneficios que ofrece yfinance -- no los hemos usado nunca en este
proyecto, todo lo anterior era precio y volumen.

Uso:
    python3 pead_reconnaissance.py
"""

if __name__ == "__main__":
    try:
        import yfinance as yf
    except ImportError:
        print("Falta yfinance. Corre: pip install yfinance --break-system-packages")
        raise SystemExit

    ticker = yf.Ticker("AAPL")

    print("=== Intentando get_earnings_dates() ===")
    try:
        earnings = ticker.get_earnings_dates(limit=40)
        print(f"Tipo de dato: {type(earnings)}")
        print(f"Columnas: {list(earnings.columns)}")
        print(f"Número de filas: {len(earnings)}")
        print(f"\nRango de fechas: {earnings.index.min()} -> {earnings.index.max()}")
        print(f"\nPrimeras 10 filas:")
        print(earnings.head(10).to_string())
    except Exception as e:
        print(f"Error con get_earnings_dates(): {type(e).__name__}: {e}")
        print("\nProbando earnings_dates (atributo, sin paréntesis, en versiones antiguas)...")
        try:
            earnings = ticker.earnings_dates
            print(f"Columnas: {list(earnings.columns)}")
            print(earnings.head(10).to_string())
        except Exception as e2:
            print(f"También falló: {type(e2).__name__}: {e2}")

    print("\n--- Siguiente paso ---")
    print("Con esto ya sabemos qué columnas usar (probablemente algo como 'Surprise(%)' o")
    print("similar) y cuántos trimestres de histórico hay disponibles por acción, antes de")
    print("construir el análisis completo sobre varias acciones a la vez.")
