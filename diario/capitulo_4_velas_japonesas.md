# Diario de a bordo: construyendo (y desmontando) un bot de trading

## Capítulo 4 — El patrón que no debía sobrevivir

### Un final sin punto de quiebre limpio

Antes de cerrar del todo la investigación de los shocks del capítulo anterior, quedaba una pregunta suelta: la continuación tras subidas bruscas se apagaba en el tramo más reciente del S&P 500 — pero, ¿se apagaba de golpe, en un punto concreto, o poco a poco?

Dividimos ese último tramo (2010-2026) en ventanas más finas. El resultado no tuvo la limpieza que esperábamos: 2010-2015 seguía positivo (+0.32%), 2016-2019 ya negativo (-0.54%), y 2020 mostraba una caída enorme (-6.75%) que resultó ser un solo dato — casi con toda seguridad el propio crash de marzo del COVID, no una tendencia. Con muestras de 1 a 11 eventos por ventana, no había forma honesta de sacar más historia de ahí. El declive fue real, pero irregular, sin un culpable identificable. A veces la respuesta más honesta es esa: "se apagó, y no sabemos exactamente por qué".

### El patrón que confirmaba lo contrario de lo esperado

Con esa vía cerrada, decidimos abrir una completamente nueva: velas japonesas, con confirmación de volumen. La literatura popular de trading retail es casi unánime en esto — Harami y Piercing Line, dos patrones de reversión alcista clásicos, "ganan credibilidad" cuando van acompañados de volumen alto. Antes de creérnoslo, lo comprobamos con datos propios sobre SPY, empezando por el patrón más simple: Bullish Engulfing.

El resultado fue el primer indicio de que algo no encajaba con la sabiduría popular: de 273 patrones detectados, ninguno de los grupos con volumen alto salió significativo en ningún horizonte. El único resultado significativo apareció en el grupo **sin** volumen alto, y solo en el horizonte más largo — justo la dirección contraria a la que veníamos buscando.

### Harami y Piercing: la señal real, escondida donde no la buscábamos

En vez de descartar la categoría entera, probamos los otros dos patrones que la literatura señalaba: Bullish Harami y Piercing Line. Esta vez, con 18 tests en total (3 patrones × 2 grupos de volumen × 3 horizontes), **8 salieron significativos** — muy por encima de los ~0.9 que esperaríamos por puro azar.

Y el patrón se repetía: Harami sin volumen alto, significativo en los tres horizontes probados. Piercing sin volumen alto, significativo en dos de tres. El volumen alto, en ambos casos, no ayudaba — si acaso, diluía la señal. Confirmamos que no era una particularidad nuestra: casi toda la literatura de trading retail sobre estos patrones dice justo lo contrario de lo que mostraban nuestros datos.

Antes de llamarlo un hallazgo, tocaba corregir por el hecho de haber probado seis candidatos a la vez. Con Bonferroni (el umbral más exigente que el 0.05 habitual, dividido entre el número de candidatos), solo dos sobrevivieron: **Piercing sin volumen** (p = 0.0000) y **Harami sin volumen** (p = 0.006). No era casualidad de haber buscado mucho — había algo real detrás.

### Estabilidad de 33 años, y costes reales

Con dos candidatos genuinos, tocaba la misma comprobación que nos había salvado antes de creernos algo prematuramente: estabilidad por sub-periodos, sobre 33 años de SPY.

Harami salió sólido en 5 de 6 tramos positivos, con el único tramo negativo coincidiendo con la crisis financiera de 2008 — una excepción explicable, no una tendencia. Piercing fue todavía más limpio: **6 de 6 tramos en positivo**, sin una sola excepción en tres décadas, incluido el tramo más reciente.

Y al simular con costes de transacción reales (0.05% de ida y vuelta, conservador para un ETF tan líquido como SPY), ambos sobrevivieron con margen amplio: Harami con un profit factor neto de 1.49, Piercing con 3.09 — muy lejos del límite en el que se cayó SOL/LINK semanas atrás en cripto.

### La réplica que confirma, matiza, y en parte contradice

Quedaba la pregunta decisiva: ¿es un fenómeno real del comportamiento del mercado, o una peculiaridad de SPY? Lo replicamos en tres activos de naturaleza completamente distinta: BTC (estructura de mercado 24/7, sin sesiones), GLD (oro, dinámica de refugio) y AAPL (una acción individual, sin la diversificación de un índice).

**Harami se replicó de forma casi perfecta**: significativo en SPY, GLD y AAPL; en BTC, no llegó a significancia, pero mantuvo la misma dirección positiva, probablemente por la mayor volatilidad de fondo de cripto, que ensancha los intervalos de confianza sin cambiar el signo. Tres de cuatro confirmados, el cuarto apuntando en la misma dirección.

**Piercing, en cambio, se rompió justo donde menos lo esperábamos**: funcionó en SPY y AAPL —los dos activos de renta variable—, pero se invirtió por completo en GLD (retorno neto negativo, profit factor por debajo de 1). La lectura más plausible: Harami parece un fenómeno genuinamente universal, mientras que Piercing podría estar ligado específicamente a la psicología de quien compra y vende acciones, que no se traslada igual a un activo refugio como el oro, con una base de participantes distinta.

### Lo que este capítulo enseñó de verdad

No descubrimos algo desconocido para la ciencia — Harami y Piercing llevan siglos documentados. Lo que sí encontramos, con nuestro propio rigor, fue algo que **contradice casi toda la sabiduría popular del trading retail** sobre cómo interpretar estos patrones: el volumen alto, lejos de confirmar la señal, la diluye. Y encontramos, además, sus límites exactos — un patrón que parece universal (Harami) y otro que parece específico de un tipo de mercado (Piercing) — con la misma honestidad con la que hemos tratado cada resultado, bueno o malo, desde el primer capítulo.

---

*En el próximo capítulo: la confirmación más limpia de todo el proyecto en mercados tradicionales, una de las anomalías académicas mejor replicadas de las finanzas — y dos señales reales pero frágiles, con la misma lección compartida sobre los límites de la potencia estadística.*
