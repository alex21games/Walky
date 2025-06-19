# Walky - Un chat ligero y seguro para tu compañia

## Que es Walky?

Walky es un chat hecho en python con el proposito de ser veloz, simple y ser seguro para toda la gente que lo use,
es por eso que la aplicacion esta destinada a usarse en un servidor LAN, y cuenta con un archivo de servidor y setup de base de datos ya pre hecho para funcionar correctamente con el cliente.

Con sistema de aceptar o rechazar solicitudes de manera comoda, para que sepas quien te manda mensajes, timestamps y un acabado hermoso para el apartado grafico.

## Como usarlo o instalarlo?

El setup de walky es muy sencillo, solo requiere un par de prerequisitos:

+ El codigo fuente disponible en el repositorio.
+ La version mas reciente de python con las siguientes librerias extras: customtkinter, socket, threading, sqlite3. LA LISTA CONTINUARA EN UN FUTURO PARA SETUPS PERSONALIZADOS
+ Pyinstaller para compilar el proyecto
+ Y MUCHAS ganas de hacerlo

Cabe recalcar que tambien existen las versiones precompiladas del proyecto, pero el setup del servidor se tiene que seguir haciendo manualmente.

Entonces, una vez aclarado eso pasemos al setup:

Al extraer el codigo este te deja dos carpetas principales: Client y Server, en una terminal accede a la direccion de la carpeta Server y ejecuta:
``` py maindb.py ```
Este debe marcar un mensaje: "Base de datos inicializada correctamente"
Si eso es asi, vamos bien. Es importante saber que si la carpeta generada "DataBase" se genera a fuera de la carpeta Server, debes meterla dentro de esta misma para que quede: Server/Database/chat_data.db

Ahora, en la misma direccion /Server/ ejecuta el siguiente comando:
``` py client_handler.py ```
Esto deberia dejarte con un mensaje exitoso tipo: "Servidor corriendo en puerto 8080", si no quieres usar localhost como ruta predeterminaada, en windows ve a tu terminal y escribe 
``` ipconfig ```
Copia tu direccion ipv4 y al final añadele ":8080" quedaria como: 192.x.xxx.xxx:8080, pero si no tienes problemas usando la palabra clave localhost puedes seguir.

Ahora, en una terminal accede a la ruta de /Client/ en la cual puedes hacer dos cosas: empaquetarlo o ejecutarlo en crudo.
Si decides ejecutarlo en crudo simplemente escribe en la ruta antes mencionada:
``` py main.py ```

Pero si quieres que el programa este siempre disponible en ejecutable sin necesidad de todas las librerias, en la misma direccion ejecuta:
``` pyinstaller --onefile main.py ```
Esto te dejara una version compilada del programa en la carpeta /Dist/ que se genero en el mismo directorio de /Client/, es completamente portable y movible sin problemas o complicaciones, puedes renombrarlo o si te apetece agregarle un logo ya que por defecto no contamos con un logo.

Con esos pasos el programa estaria listo para usarse!

El programa es muy sencillo de usar por lo que un manual no es requerido, pero si las funciones que este implementa:

Login o registro: Este apartado es el primero en aparecer cada vez que abres el programa, tienes dos opciones, loguearte con una cuenta ya existente o crear una nueva, no hay limite de creacion pero es recomendable usar dos como maximo. La primera casilla es para el nombre, la segunda es para la contraseña, y como recuerdo tienes dos opciones, loguearte o registrarte, si te registras tendras que darle luego al boton de loguearte.

Direccion ip: Esta opcion le permite al usuario elegir a que servidor conectarse, dependiendo de a cual se conecte puede que este registrado o no, tenga contactos o chats registrados o si siquiera tenga permitido entrar! como recomendacion, solo pon localhost si tu empresa corre unicamente un servidor, si te dice lo contrario escribe la ip proporcionada.

Chat principal: Al pasar las otras pantallas se te presenta la app como tal, tienes los contactos en forma de lista, un boton de "+" para añadir uno nuevo, y elminiar para eliminar un contacto que ya no deseas que te lleguen sus mensajes, tambien la casilla de texto, donde aparece texto en burbujas para cada uno y ademas la caja de texto para mandar un mensaje.



El programa le pertenece a Secure. Inc. No lo modifique maliciosamente ni se lucre de el, no esta permitido.
