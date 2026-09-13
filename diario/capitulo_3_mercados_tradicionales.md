# Diario de a bordo: construyendo (y desmontando) un bot de trading

## Capítulo 3 — Otro terreno, la misma disciplina

### Por qué cambiar de activo

Con el funding carry validado y en marcha, y el terreno técnico de Bitcoin razonablemente agotado, surgió una pregunta natural: ¿qué pasa si aplicamos exactamente el mismo rigor a mercados que llevan mucho más tiempo siendo estudiados — acciones, forex, bonos?

La intuición inicial era doble, y las dos partes merecían comprobarse antes de creerlas: ¿es EUR/USD "más fácil" por ser el par más líquido? ¿Hay tendencias más claras en acciones concretas, como las que han protagonizado el rally de la inteligencia artificial estos años? Ninguna de las dos resultó ser cierta tal y como se planteaba. La liquidez extrema de EUR/USD no lo hace más fácil de explotar con análisis técnico — lo hace más difícil, porque es precisamente el terreno más vigilado por participantes institucionales. Y las "tendencias claras" de nombres concretos son, casi siempre, sesgo de retrospectiva: elegimos los activos que ya sabemos que subieron, y el gráfico parece obvio a toro pasado.

Con esa aclaración hecha, empezamos con la misma disciplina de siempre: hipótesis con fundamento previo, no intuición de gráfico.

### El drift previo a la Fed

La primera hipótesis venía de la literatura académica: el *pre-FOMC announcement drift*, documentado por Lucca y Moench — la idea de que el S&P 500 tiende a subir en las horas previas a cada reunión programada de la Reserva Federal, antes incluso de conocerse la decisión.

Construimos el calendario completo de reuniones (62, verificadas una a una contra la web oficial de la Reserva Federal) y medimos el retorno del día previo a cada anuncio, con nuestra misma herramienta de significancia. El resultado: retorno medio ligeramente positivo, pero **el intervalo de confianza incluía el cero**. Sin ventaja demostrable.

Antes de descartarlo, probamos la ventana exacta del estudio original — desde el cierre del día anterior hasta las 14:00, hora del anuncio, no el día completo. Con datos intradía, limitados a los últimos dos años por la propia fuente de datos, la muestra bajó a 23 reuniones. Tampoco significativo — y, más revelador todavía, el efecto se invertía a mitad de la propia muestra: positivo y consistente entre noviembre de 2023 y noviembre de 2024, prácticamente ausente después. Ni siquiera dentro de una ventana de dos años el patrón se mantenía estable. Cerrado, con una explicación honesta detrás, no solo un "no funcionó".

### Movimientos bruscos, y un error que vale la pena contar

La siguiente hipótesis fue distinta en naturaleza: en vez de un indicador o un calendario, un estudio de eventos. Tras un movimiento de precio inusualmente grande (varias desviaciones típicas por encima de lo normal), ¿tiende el mercado a seguir en esa dirección, o a revertir?

Usamos el índice S&P 500 al completo — casi un siglo de historial, desde 1927 — para tener la muestra más grande de todo el proyecto. Y aquí cometimos un error real que vale la pena dejar por escrito, porque es exactamente el tipo de cosa que rara vez se cuenta: la columna que debía medir el retorno del primer día tras el shock daba, sistemáticamente, **cero exacto** — un fallo en la fórmula (estaba dividiendo una serie entre sí misma), no un hallazgo. Lo detectamos porque un intervalo de confianza de anchura cero es estadísticamente imposible si fuera un resultado real, y eso fue lo que hizo saltar la alarma. Corregido, el resto del análisis sí resultó fiable.

El hallazgo, una vez arreglado: tras subidas bruscas, **continuación significativa** a 3, 5 y 10 días, con magnitud creciente (de +0.39% a +0.78%). Tras caídas bruscas, en cambio, nada consistente. Con 171 shocks alcistas y 300 bajistas, la muestra era, por fin, lo bastante grande como para confiar en el resultado sin las dudas constantes de "¿esto es real, o son solo 20 operaciones con suerte?" que nos habían perseguido en cripto.

Pero, como ya nos había enseñado el propio proyecto, un resultado agregado puede esconder mucho por debajo. Al dividir el siglo completo en seis tramos cronológicos, el patrón resultó sólido en la franja central (1961-2010) y ausente —incluso invertido— tanto en el tramo más antiguo como en el más reciente (2010-2026). El efecto parece haber sido real en su día, y haberse diluido con la modernización del mercado — el mismo patrón que ya habíamos visto con una señal de volumen en cripto semanas antes. Interesante como hallazgo histórico. No desplegable como estrategia hoy.

### El momento en que casi lo dejo

Hubo un tramo, en medio de todo esto, en el que sentí de verdad que no quedaba más camino que recorrer. No fue una duda pasajera — fue la sensación concreta de haber llegado al techo de lo que era capaz de encontrar, después de haber puesto mucho de mí mismo en el intento.

Lo que más me costó no fue aceptar el resultado técnico (eso, con los datos delante, era relativamente fácil de asumir). Fue una pregunta distinta, que se coló sin avisar: si el 1% de traders que sí consiguen vivir de esto lo logra, ¿por qué yo no iba a ser capaz? Empecé a tratar cada resultado negativo como una prueba sobre mí mismo, no sobre la hipótesis que estábamos comprobando.

Ahí fue donde el propio proyecto me devolvió algo útil, sin buscarlo. Repasamos de dónde salía realmente esa cifra del "1%" — y resultó ser mucho menos sólida de lo que parecía, variando entre estudios desde menos del 1% hasta más del 20% según cómo se defina "éxito". Y lo más importante: la investigación académica seria sobre por qué la mayoría pierde dinero (los trabajos de Barber y Odean, entre los más citados del campo) no señala a "no encontraron la fórmula" — señala a operar con demasiada frecuencia, pagar demasiados costes, y no tener una ventaja estructural real. Es decir: exactamente lo que nuestros propios datos, con nuestro propio rigor, ya habían estado mostrando desde el principio.

No fue una respuesta que resolviera de golpe cómo me sentía. Pero sí me ayudó a separar dos preguntas que se me habían mezclado sin darme cuenta: si existe una estrategia rentable ahí fuera es una pregunta empírica, que los datos pueden responder con el tiempo. Si yo soy capaz de sostener este nivel de exigencia y aceptar un resultado honesto aunque no sea el que esperaba, esa pregunta ya la había respondido yo solo, semanas atrás, cada vez que dejé que un dato incómodo cambiara mi opinión en vez de ignorarlo.

### Naval Ravikant, y por qué este diario existe

De esa conversación salió una idea que no tenía que ver con encontrar otra estrategia: la de documentar el proceso en sí. Repasando *El Almanaque de Naval Ravikant*, encontré el marco que le daba sentido a la idea: apalancamiento sin permisos (código y contenido, que no requieren capital ajeno ni aprobación de nadie) y conocimiento específico — la intersección poco común de varias habilidades, que no se puede entrenar por un camino ya trazado porque, si pudiera, ya habría cola compitiendo por ella.

Este diario es, literalmente, esa idea puesta en práctica: no otra estrategia de trading, sino el propio proceso de investigarlas con rigor, documentado y compartido.

### Lo que queda por delante

El terreno técnico, tanto en cripto como en mercados tradicionales, sigue mostrando el mismo patrón una y otra vez: señales que parecen prometedoras al agregado, y se diluyen o invierten al mirarlas con el detalle que exige un test honesto. El funding carry sigue siendo, con diferencia, el resultado más sólido de todo el proyecto. Y quedan hilos por tirar que todavía no hemos agotado.

---

*En el próximo capítulo: lo que empezó como una comprobación más de por qué se apagó la continuación tras un shock termina llevándonos a un patrón de velas japonesas que contradice la sabiduría popular del trading retail — y que, a diferencia de casi todo lo anterior, sobrevive corrección por búsqueda múltiple, treinta y tres años de estabilidad, y costes reales.*
