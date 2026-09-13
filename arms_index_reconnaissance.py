"""
arms_index_reconnaissance.py
El Índice Arms (TRIN) mide amplitud de mercado -- no se puede calcular
desde el precio de un solo activo. Necesita datos agregados de todo
el mercado (nº de acciones que suben/bajan y su volumen). Antes de
intentar construirlo a mano (mucho trabajo, requiere datos de todos
los componentes de un índice), comprobamos si yfinance ya tiene un
ticker con el índice pre-calculado.

Uso:
    python3 arms_index_reconnaissance.py
"""

if __name__ == "__main__":
    try:
        import yfinance as yf
    except ImportError:
        print("Falta yfinance. Corre: pip install yfinance --break-system-packages")
        raise SystemExit

    candidatos = ["^TRIN", "^ARMS", "TRIN", "^TRINQ"]

    for simbolo in candidatos:
        print(f"=== Probando '{simbolo}' ===")
        try:
            data = yf.Ticker(simbolo).history(period="1y")
            if data.empty:
                print(f"  Sin datos (vacío).")
            else:
                print(f"  ¡Funciona! {len(data)} filas. Rango: {data.index.min()} -> {data.index.max()}")
                print(f"  Últimos valores de 'Close':")
                print(data["Close"].tail(5).to_string())
        except Exception as e:
            print(f"  Error: {type(e).__name__}: {e}")
        print()

    print("--- Siguiente paso ---")
    print("Si alguno de estos funcionó con histórico razonable, construimos el análisis")
    print("directamente sobre esos valores. Si ninguno funciona, la alternativa es construir")
    print("el índice a mano desde datos de amplitud de mercado (más trabajo, y puede que no")
    print("compense frente a lo que queda por investigar) -- lo decidimos según lo que salga aquí.")
