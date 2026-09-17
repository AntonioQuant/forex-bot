# Diario de a bordo: construyendo (y desmontando) un bot de trading

## Capítulo 7 — Lo que enseña un manual de trading, puesto a prueba

### Un tercer tipo de verificación

Hasta ahora, este diario había investigado hipótesis propias — ideas que se nos ocurrían, o que sacábamos de la literatura académica. Esta vez cambié de método: en vez de partir de una idea mía, decidí someter un conjunto amplio de afirmaciones clásicas de análisis técnico —las que aparecen en cualquier manual de trading, las que millones de personas usan cada día para decidir cuándo comprar y cuándo vender— al mismo rigor que le hemos aplicado a todo lo demás.

Con una regla añadida desde el principio, que se volvería central más adelante: no basta con que una señal dé positivo — tiene que dar positivo **por encima** de lo que habría dado simplemente comprar y mantener el activo sin ninguna señal. Lo llamé el "exceso" sobre el benchmark incondicional. Si Bitcoin sube con el tiempo de todas formas, cualquier señal de compra va a parecer que "funciona" a menos que se le reste esa deriva de fondo.

### RSI y MACD, los dos indicadores más citados de cualquier curso

Empecé por los osciladores. El manual clásico: RSI por debajo de 30 y volviendo a subir, señal de compra. RSI por encima de 70 y bajando, señal de venta. Cruce de las líneas del MACD, lo mismo.

Con datos reales de Bitcoin y del S&P 500, y el control de exceso puesto: **24 tests en total, solo 1 significativo** — dentro de lo que esperaríamos por puro azar. El indicador más enseñado del mundo, sin ventaja demostrable una vez se descuenta la deriva del propio activo.

### Velas individuales y figuras de reversión, una tras otra

Seguí con Martillo y Estrella Fugaz — velas con mecha larga que, según el manual, marcan un giro "sin necesitar ninguna otra confirmación". Nada: 1 de 24 tests significativo, sin ninguna dirección consistente.

Doble Cima y Doble Fondo — dos picos o valles al mismo nivel, con ruptura de la línea del cuello como confirmación. Construir esto exigió una definición propia, con números concretos donde el manual solo da intuición visual. Resultado: nada, en ningún activo, en ningún horizonte.

Soporte y resistencia horizontal — la idea de que el precio rebota en niveles ya marcados antes. Aquí sí apareció algo, en apariencia: significativo en el S&P 500, con la muestra más grande de todo el proyecto (más de 5.600 eventos). Pero al dividirlo por sub-periodos de la historia, el patrón resultó estar sostenido casi por completo por un único tramo — la crisis financiera de 2008. Fuera de ahí, casi nada. Rechazado, con una explicación honesta detrás.

### El hallazgo que contradice al propio manual

Con casi todo cayendo, probé algo distinto: los retrocesos de Fibonacci. La idea clásica dice que, tras un movimiento fuerte, el precio retrocede hasta un nivel concreto (38.2%, 50%, 61.8% del movimiento) y luego **reanuda la dirección original**.

Los datos de Bitcoin dijeron lo contrario. Tras un movimiento alcista fuerte, cuando el precio tocaba uno de esos niveles de Fibonacci, **el precio seguía cayendo, no reanudaba la subida** — con una magnitud que crecía de forma ordenada con el tiempo, significativa en los tres horizontes que probé.

Lo repliqué en ETH, SOL y LTC. La fuerza varió bastante de un activo a otro, pero la dirección fue casi unánime: 11 de 12 tests, en cuatro criptoactivos distintos, apuntando en la misma dirección bajista. La probabilidad de eso por puro azar: 0.317%, calculado con precisión, no estimado a ojo.

Con costes de transacción reales incluidos, la estrategia (en corto, ya que la dirección era bajista) mantuvo un profit factor por encima de 1 en los horizontes más cortos. Era, con diferencia, el hallazgo más sólido de todo lo probado hasta ese momento — el único que sobrevivía de verdad, y encima contradiciendo justo lo que el manual enseña.

Estaba listo para darlo por bueno del todo.

No debería haberlo estado tan rápido.

---

*En el próximo capítulo: un resultado demasiado limpio en una prueba de volumen hace saltar una alarma que llevaba semanas sin sonar — y termina revelando un fallo real en nuestro propio método, no en el manual que estábamos verificando.*
