# Diario de a bordo: construyendo (y desmontando) un bot de trading

## Capítulo 6 — Cerrar la lista, no la investigación

### Un rechazo por impracticable, no por refutado

La última hipótesis pendiente era el Índice Arms (TRIN), una medida clásica de amplitud de mercado — cuántas acciones suben frente a las que bajan, ponderado por su volumen. Antes de construirlo a mano, comprobamos si algún proveedor de datos ya lo ofrecía calculado.

El resultado fue una lección sobre verificar antes de confiar, no sobre el índice en sí: uno de los símbolos que probamos ("TRIN", sin el prefijo correcto) sí devolvía datos — pero con valores que no tenían ningún sentido como índice de amplitud. Resultó ser una coincidencia de tickers: TRIN es también el símbolo bursátil de Trinity Capital, una empresa de financiación completamente ajena al índice que buscábamos. Los símbolos correctos no existían en la fuente que usamos. Construirlo desde cero habría exigido datos de amplitud de cientos de componentes del S&P 500, día a día — una tarea desproporcionada frente a lo que quedaba por investigar. Cerramos esta vía no porque el fenómeno esté refutado, sino porque el coste de comprobarlo bien no compensaba.

### El balance final de las diez hipótesis

Con esto, la lista completa queda así:

- **Sólido, con réplica en varios activos**: Harami y Piercing sin volumen alto, PEAD.
- **Real, pero con potencia estadística insuficiente**: vuelta a tendencia EMA, compras de insiders.
- **Rechazado con una explicación honesta detrás**: el drift previo al FOMC, la continuación tras shocks (con su propia "era dorada" 1961-2010), Bullish Engulfing.
- **Descartado por impracticable**: el Índice Arms.

Ningún resultado se forzó para que encajara en una narrativa más bonita de la que los datos sostenían. Es, probablemente, el resumen más honesto que podíamos escribir hasta ahora.

### Una lectura que no esperaba, y que le dio lenguaje a todo esto

En medio de cerrar esta lista, alguien cercano me pasó un libro que no tenía nada que ver con trading: *Ontología del Lenguaje*, de Rafael Echeverría. Lo leí buscando otra cosa, y encontré una distinción que describe, con más precisión de la que yo mismo había usado, lo que hemos estado haciendo estas semanas.

El libro separa dos tipos de afirmaciones: una **afirmación verificable**, que describe algo comprobable con evidencia, y un **juicio**, que no es verdadero ni falso, sino fundado o infundado según lo que lo respalda. Y añade algo que conecta de lleno con este proyecto: una predicción es un tipo particular de afirmación, que no se puede corroborar hasta que el futuro llega — pero que exige preguntarse, igual que un juicio, qué la fundamenta.

Es, en otras palabras, la pregunta que nos hemos hecho delante de cada estrategia, cada patrón, cada newsletter que hemos revisado estas semanas: ¿esto es una afirmación fundada, con datos detrás, o un juicio disfrazado de hecho? El libro también defendía algo que ya intuíamos sin nombrarlo: que las historias no son un envoltorio alrededor de los datos — son la forma natural en que cualquier hallazgo, por riguroso que sea, adquiere sentido para quien lo lee. Incluidas las explicaciones científicas, que también son narrativas, solo que mejor fundamentadas que otras.

### Lo que este capítulo cierra, y lo que no

Esta lista de diez hipótesis está agotada. La investigación no. Ya hay un hilo nuevo tomando forma —distinto en naturaleza a todo lo anterior, todavía sin resultados que mostrar— y es muy probable que, según avance, salgan más ideas de las que hoy ni siquiera imaginamos, como nos ha pasado una y otra vez desde el primer capítulo.

No sé todavía qué será el capítulo 7. Y por primera vez en este diario, eso no lo escribo como una carencia — lo escribo como lo que realmente es: la investigación sigue abierta, y el próximo hallazgo se anunciará cuando exista, no antes.

---

*Continuará.*
