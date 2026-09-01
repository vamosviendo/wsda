## Elementos. Distintos tipos

Agregar al modelo ElementoPage la posibilidad de guardar y mostrar contenido 
multimedia (audio/video) alojado en el propio servidor o en un servidor externo,
no solamente links a videos de youtube/vimeo.

A tal efecto, agregar un campo "contenido_multimedia" (o bien dos campos, 
"contenido_video" y "contenido_audio", lo que se considere más conveniente) que 
haga referencia a archivos de tipo audio/video. No sé si Django o Wagtail tienen
algún tipo de campo de este tipo o habrá que usar un FileField. Investigar.
Al mismo tiempo, el template correspondiente deberá incorporar un reproductor de 
audio/video en caso de encontrarse con un contenido de este tipo. 

De esta manera, ElementoPage sería capaz de contener tanto videos gestionados por 
el sitio como links a videos externos de youtube o vimeo (o audio de Spotify u
otras apps, aunque eso todavía no está implementado).
