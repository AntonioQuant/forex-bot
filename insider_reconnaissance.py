"""
insider_reconnaissance.py
Compras de directivos de su propia empresa (Form 4 ante la SEC) --
dato público que no hemos usado todavía. Comprobamos qué método y qué
forma de datos ofrece yfinance antes de construir el análisis
completo.

Uso:
    python3 insider_reconnaissance.py
"""

if __name__ == "__main__":
    try:
        import yfinance as yf
    except ImportError:
        print("Falta yfinance. Corre: pip install yfinance --break-system-packages")
        raise SystemExit

    ticker = yf.Ticker("AAPL")

    metodos_candidatos = [
        "insider_transactions",
        "insider_purchases",
        "insider_roster_holders",
    ]

    for nombre_metodo in metodos_candidatos:
        print(f"=== Probando '.{nombre_metodo}' ===")
        try:
            atributo = getattr(ticker, nombre_metodo)
            if atributo is None:
                print("  Devuelve None.")
            elif hasattr(atributo, "empty") and atributo.empty:
                print("  DataFrame vacío.")
            else:
                print(f"  Tipo: {type(atributo)}")
                if hasattr(atributo, "columns"):
                    print(f"  Columnas: {list(atributo.columns)}")
                    print(f"  Filas: {len(atributo)}")
                    print(atributo.head(10).to_string())
                else:
                    print(atributo)
        except AttributeError as e:
            print(f"  El método no existe en esta versión: {e}")
        except Exception as e:
            print(f"  Error: {type(e).__name__}: {e}")
        print()

    print("--- Siguiente paso ---")
    print("Con las columnas reales delante, construimos el análisis: ¿el precio sube más de lo")
    print("normal en las semanas siguientes a compras de insiders con volumen relevante?")
