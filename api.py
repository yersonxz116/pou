import random
import unicodedata
import csv
import json
import os
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

import joblib

from fastapi import FastAPI
from pydantic import BaseModel

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.85"))
MEMORIA_PATH = Path("memoria_groq.csv")

# Cargar el modelo entrenado
modelo = joblib.load('modelo_chatbot.pkl')

# Crear la aplicación FastAPI
app = FastAPI(title="Chatbot API")

# Respuestas del chatbot sobre Pou. Las claves deben coincidir con las
# intenciones entrenadas en data.xlsx.
respuestas = {
    'saludo': [
        '¡Hola! Pregúntame cualquier cosa sobre Pou: cuidados, monedas, minijuegos, niveles o personalización.',
        '¡Hola! Estoy listo para ayudarte con dudas sobre el juego Pou.',
        '¡Bienvenido! Puedo responder preguntas sobre cómo cuidar y avanzar en Pou.',
        '¡Hola! Dime qué necesitas saber sobre Pou.'
    ],

    'despedida': [
        '¡Hasta luego! No olvides alimentar, limpiar y dormir a Pou.',
        '¡Nos vemos! Sigue jugando minijuegos para ganar monedas en Pou.',
        '¡Chao! Espero que tu Pou quede feliz y bien cuidado.',
        'Gracias por preguntar sobre Pou. ¡Hasta pronto!'
    ],

    'agradecimiento': [
        '¡De nada! Pregúntame cuando quieras sobre Pou.',
        'Con gusto. Puedo ayudarte con cuidados, monedas, niveles o accesorios de Pou.',
        'Me alegra ayudarte con el juego Pou.',
        '¡No hay de qué! Sigue cuidando bien a Pou.'
    ],

    'soporte': [
        'Pou es un juego de mascota virtual: debes alimentarlo, bañarlo, dormirlo, jugar con él y personalizarlo.',
        'El objetivo de Pou es mantener sus barras de hambre, salud, energía y diversión en buen estado mientras subes de nivel.',
        'En Pou ganas monedas jugando minijuegos y las usas para comprar comida, ropa, fondos, accesorios y pociones.',
        'Si Pou está mal, revisa sus necesidades: puede tener hambre, estar sucio, cansado, aburrido o enfermo.'
    ],

    'login': [
        'Para recuperar tu Pou en otro celular, revisa si el juego te permite iniciar sesión o restaurar progreso desde la cuenta vinculada.',
        'Si perdiste tu avance de Pou, intenta abrirlo con la misma cuenta o tienda de aplicaciones donde lo usabas antes.',
        'Al cambiar de celular, instala Pou y verifica las opciones de cuenta, copia de seguridad o restauración disponibles.',
        'Si tu Pou anterior no aparece, revisa que estés usando la misma cuenta del dispositivo donde guardaste el progreso.'
    ],

    'password': [
        'Si olvidaste datos de acceso relacionados con Pou, intenta recuperar la cuenta desde la tienda o correo vinculado.',
        'Para proteger tu progreso en Pou, usa una cuenta segura en tu dispositivo y evita borrar datos de la aplicación.',
        'Si Pou pide acceso o cuenta, verifica que el correo y la contraseña correspondan a la cuenta donde estaba guardado el avance.',
        'Cuando cambies datos de cuenta, confirma primero que tu progreso de Pou esté respaldado.'
    ],

    'cursos': [
        'Pou tiene varias secciones: cocina para comida, baño para limpieza, dormitorio para energía, laboratorio para pociones y sala de juegos para minijuegos.',
        'En la cocina alimentas a Pou; en el baño lo limpias; en el dormitorio apagas la luz para que duerma.',
        'El laboratorio sirve para usar pociones, por ejemplo para salud, hambre, energía o cambios especiales según el objeto disponible.',
        'La tienda permite comprar comida, ropa, accesorios, fondos y decoraciones usando monedas.'
    ],

    'tareas': [
        'Para cuidar a Pou, aliméntalo cuando tenga hambre, báñalo si está sucio, apaga la luz si está cansado y juega si está aburrido.',
        'Si Pou está enfermo, usa una poción de salud o revisa el laboratorio para curarlo.',
        'Para subir higiene, ve al baño y limpia a Pou con jabón o agua hasta que la barra mejore.',
        'Una buena rutina es revisar hambre, salud, energía y diversión cada vez que abras el juego.'
    ],

    'examenes': [
        'Los minijuegos de Pou sirven para ganar monedas y aumentar la diversión. Algunos son de reflejos, memoria, saltos, carreras o rompecabezas.',
        'Para ganar más monedas en Pou, juega los minijuegos donde consigas mejor puntaje de forma constante.',
        'Minijuegos como Food Drop, Sky Jump, Hill Drive, Connect o Color Match ayudan a practicar y reunir monedas.',
        'Si pierdes un minijuego no pasa nada grave: puedes volver a intentarlo para mejorar tu récord y ganar más monedas.'
    ],

    'notas': [
        'Pou sube de nivel cuando lo cuidas y juegas. Al avanzar puedes desbloquear más objetos, ropa, comida y decoraciones.',
        'Puedes revisar tu progreso mirando el nivel, la experiencia y los récords de minijuegos.',
        'Los mejores puntajes en minijuegos muestran qué tanto has mejorado y ayudan a medir tu avance.',
        'Si quieres subir más rápido, mantén a Pou cuidado y juega minijuegos con frecuencia.'
    ],

    'pagos': [
        'Las monedas de Pou sirven para comprar comida, ropa, accesorios, fondos, decoraciones y pociones.',
        'La forma principal de conseguir monedas en Pou es jugar minijuegos y mejorar tus puntajes.',
        'Para ahorrar monedas, compra primero comida y pociones necesarias; luego gasta en ropa o decoración.',
        'Si compras un objeto y no aparece, revisa la tienda, el inventario o reinicia el juego antes de intentar de nuevo.'
    ],

    'perfil': [
        'Puedes personalizar a Pou cambiando ropa, color, ojos, accesorios, sombreros, lentes y fondos.',
        'Para vestir a Pou, entra a la tienda o sección de personalización, compra un accesorio y aplícalo.',
        'Cambiar la apariencia no afecta sus necesidades, pero hace que tu Pou tenga un estilo propio.',
        'También puedes decorar las habitaciones con fondos y objetos desbloqueados o comprados con monedas.'
    ],

    'certificados': [
        'Pou tiene recompensas y desbloqueables: al subir de nivel puedes acceder a más comida, ropa, fondos, accesorios y objetos.',
        'Los logros o metas se consiguen cuidando a Pou, jugando minijuegos y progresando en niveles.',
        'No hay un certificado como tal en Pou, pero tu nivel, objetos y récords muestran tu progreso.',
        'Para desbloquear más recompensas, mantén a Pou feliz, gana monedas y juega con frecuencia.'
    ]
}

respuesta_fallback = [
    'No tengo un dato exacto para esa pregunta sobre Pou. Si preguntas por cuidados, monedas, minijuegos, requisitos, plataformas o personalizacion, puedo responder mejor.',
    'No encuentro una respuesta confiable para esa pregunta concreta de Pou. Prefiero no inventar datos.',
    'Esa informacion no esta clara en mis datos locales sobre Pou. Puedo ayudarte con datos generales, tecnicos y mecanicas del juego.'
]

def normalizar(texto: str) -> str:
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    return "".join(char for char in texto if unicodedata.category(char) != "Mn")

def contiene(texto: str, palabras: list[str]) -> bool:
    return any(palabra in texto for palabra in palabras)

def confianza_modelo(texto: str):
    if not hasattr(modelo, "predict_proba"):
        intent = modelo.predict([texto])[0]
        return intent, 1.0

    probabilidades = modelo.predict_proba([texto])[0]
    indice = int(probabilidades.argmax())
    return modelo.classes_[indice], float(probabilidades[indice])

def buscar_en_memoria(texto: str):
    if not MEMORIA_PATH.exists():
        return None

    texto_normalizado = normalizar(texto)
    with MEMORIA_PATH.open("r", encoding="utf-8", newline="") as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            if fila.get("pregunta_normalizada") == texto_normalizado:
                return fila.get("respuesta")

    return None

def guardar_en_memoria(texto: str, respuesta: str, intent: str, confianza: float):
    existe = MEMORIA_PATH.exists()
    with MEMORIA_PATH.open("a", encoding="utf-8", newline="") as archivo:
        campos = ["fecha", "pregunta", "pregunta_normalizada", "respuesta", "intent", "confianza", "modelo"]
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        if not existe:
            escritor.writeheader()
        escritor.writerow({
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "pregunta": texto,
            "pregunta_normalizada": normalizar(texto),
            "respuesta": respuesta,
            "intent": intent,
            "confianza": f"{confianza:.4f}",
            "modelo": GROQ_MODEL,
        })

def consultar_groq(texto: str):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None, "GROQ_API_KEY no esta configurada"

    prompt_sistema = (
        "Eres un asistente experto en el juego Pou. "
        "Responde en español, de forma muy corta y directa: maximo 2 frases. "
        "No uses listas, introducciones ni cierre conversacional. "
        "Si no sabes un dato exacto, dilo y explica que puede variar por version, tienda o dispositivo. "
        "No inventes numeros exactos de colores, trajes, accesorios o minijuegos. "
        "Centra la respuesta solo en Pou."
    )
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": texto},
        ],
        "temperature": 0.2,
        "max_completion_tokens": 80,
    }
    request = urllib.request.Request(
        GROQ_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "pou-chatbot/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detalle = error.read().decode("utf-8", errors="replace")
        if error.code == 403 and "1010" in detalle:
            return None, "HTTP 403 error 1010: Groq/Cloudflare bloqueo la peticion. Se agrego User-Agent; reinicia Uvicorn y vuelve a probar. Si persiste, crea una API key nueva."
        return None, f"HTTP {error.code}: {detalle[:300]}"
    except urllib.error.URLError as error:
        return None, f"Error de conexion: {error.reason}"
    except TimeoutError:
        return None, "Timeout consultando Groq"
    except json.JSONDecodeError:
        return None, "Groq respondio JSON invalido"

    try:
        return data["choices"][0]["message"]["content"].strip(), None
    except (KeyError, IndexError, TypeError):
        return None, f"Respuesta inesperada de Groq: {str(data)[:300]}"

def tipo_interaccion_basica(texto: str):
    texto = normalizar(texto).strip()
    saludos = {"hola", "holas", "ola", "buenas", "buenos dias", "buenas tardes", "buenas noches", "hey", "saludos", "que tal", "que mas"}
    despedidas = {"adios", "chao", "bye", "hasta luego", "nos vemos", "hasta pronto"}
    agradecimientos = {"gracias", "muchas gracias", "ok gracias", "listo gracias", "perfecto gracias"}

    if texto in saludos:
        return "saludo"
    if texto in despedidas:
        return "despedida"
    if texto in agradecimientos:
        return "agradecimiento"

    if contiene(texto, ["hola pou", "hola chatbot"]):
        return "saludo"
    if contiene(texto, ["gracias por", "muchas gracias"]):
        return "agradecimiento"
    if contiene(texto, ["hasta luego", "nos vemos"]):
        return "despedida"

    return None

def es_interaccion_basica(texto: str) -> bool:
    return tipo_interaccion_basica(texto) is not None

def es_pregunta_cantidad(texto: str) -> bool:
    return contiene(texto, ["cuantos ", "cuantas ", "cuanto ", "cuanta ", "cuantos hay", "cuantas hay", "numero de", "cantidad de"])

def respuesta_especifica(texto: str):
    texto = normalizar(texto)
    palabras = set(texto.split())

    if contiene(texto, ["cuanto mide", "altura de pou", "tamano fisico", "tamaño fisico", "estatura de pou", "medidas de pou"]):
        return "Pou no tiene una medida oficial de altura o tamaño fisico dentro del juego. Es un personaje virtual, asi que no conviene inventar una estatura exacta."

    if contiene(texto, ["cuanto pesa pou", "peso de pou", "masa de pou"]):
        return "Pou no tiene un peso oficial como personaje. Si te refieres al tamaño de la app, en App Store figura cerca de 104 MB, aunque puede variar por version."

    if contiene(texto, ["cuantos anos tiene pou", "cuantos años tiene pou", "edad de pou", "edad tiene pou", "que edad tiene pou", "edad del personaje", "edad de la mascota"]):
        return "Pou no tiene una edad oficial como personaje. El juego fue lanzado originalmente en 2012, pero la mascota no maneja una edad real fija."

    if contiene(texto, ["personas pueden jugar", "cuantas personas", "cuantos jugadores", "jugar a la vez", "mismo dispositivo", "multijugador"]):
        return "Pou esta pensado principalmente como una mascota virtual para un jugador por dispositivo o perfil. No es un juego multijugador simultaneo local en el mismo dispositivo."

    if contiene(texto, ["en que ano salio", "en que año salio", "cuando salio", "fecha de lanzamiento", "lanzado", "lanzamiento"]):
        return "Pou fue lanzado originalmente en 2012. Primero se hizo popular en moviles como Android y luego tambien llego a iOS."

    if contiene(texto, ["quien creo", "quien invento", "desarrollador", "creador de pou", "quien desarrollo", "quien publico", "zakeh"]):
        return "Pou fue desarrollado por Zakeh. Su creador asociado es Paul Salameh, y el juego se conoce como una mascota virtual movil."

    menciona_plataforma = (
        contiene(texto, ["plataforma", "blackberry", "google play", "app store"])
        or bool(palabras & {"android", "iphone", "ipad", "ios", "ipados"})
    )
    if menciona_plataforma:
        if contiene(texto, ["app store"]) or bool(palabras & {"ios", "ipados", "iphone", "ipad"}):
            return "En iPhone y iPad, Pou aparece en App Store con requisito de iOS/iPadOS 13.0 o superior. La compatibilidad exacta depende de la version publicada en la tienda."
        if contiene(texto, ["google play"]) or "android" in palabras:
            return "En Android, Pou se instala desde Google Play si el dispositivo aparece como compatible. La version minima puede variar segun la actualizacion y el equipo."
        return "Pou esta disponible para moviles, principalmente Android e iOS. Tambien tuvo versiones en otras plataformas moviles como BlackBerry."

    if contiene(texto, ["requisitos", "especificaciones", "celular necesito", "telefono necesito", "compatible", "compatibilidad", "memoria", "almacenamiento", "espacio", "tamano", "tamaño", "pesa"]):
        return "Para jugar Pou necesitas un movil compatible, espacio libre de almacenamiento y una version del sistema aceptada por la tienda. En App Store figura iOS/iPadOS 13.0 o superior y un tamano cercano a 104 MB."

    if contiene(texto, ["privacidad", "datos", "recopila", "comparte datos", "cifra", "cifrado", "eliminar datos"]):
        return "La ficha de Google Play indica que Pou puede recopilar datos como informacion personal, actividad de la app e identificadores. Tambien muestra opciones relacionadas con eliminacion de datos; revisa la tienda para la version vigente."

    if contiene(texto, ["anuncio", "publicidad", "compras integradas", "compras dentro", "microtransacciones", "comprar monedas", "pagar"]):
        return "Pou puede incluir anuncios y compras dentro de la app, como monedas u objetos. Aun asi, se puede jugar cuidando a Pou y ganando monedas con minijuegos."

    if contiene(texto, ["descargas", "mil millones", "1000 millones", "1b", "resenas", "reseñas", "calificacion", "rating"]):
        return "Pou es un juego muy popular: en Google Play aparece con mas de 1000 millones de descargas y millones de reseñas. La calificacion exacta puede cambiar con el tiempo."

    if contiene(texto, ["soporte oficial", "correo de soporte", "pagina de ayuda", "help.pou.me", "contactar soporte", "ayuda oficial"]):
        return "Para soporte oficial de Pou puedes revisar la ayuda del juego o el sitio help.pou.me. En las tiendas tambien aparece informacion de contacto del desarrollador."

    if contiene(texto, ["version", "actualizacion", "ultima actualizacion", "novedades", "bug fixes", "errores corregidos"]):
        return "Pou sigue recibiendo actualizaciones con correcciones y contenido como escenas, fondos, trajes o accesorios. La version exacta cambia segun App Store o Google Play."

    if contiene(texto, ["idioma", "idiomas", "espanol", "español", "ingles", "english"]):
        return "Pou esta disponible en varios idiomas, incluyendo español e ingles. La lista completa puede variar segun la tienda y la version."

    if contiene(texto, ["clasificacion", "ninos", "niños", "apto", "familiar", "family", "edad recomendada", "para que edad"]):
        return "Pou es un juego familiar de mascota virtual. En App Store aparece con clasificacion 4+, y en Android suele mostrarse como apto para publico general."

    if contiene(texto, ["alien", "alienigena", "alienígena", "mascota alien"]):
        return "Pou es presentado como una mascota alienigena virtual: el jugador lo cuida, lo alimenta, lo limpia, juega con el y personaliza su apariencia."

    if contiene(texto, ["cuantos colores", "cuantas opciones de color", "numero de colores", "colores tiene"]):
        return "Pou tiene varias opciones de color en personalizacion. No conviene dar un numero fijo porque puede variar segun la version y los objetos desbloqueados."

    if contiene(texto, ["cuantos trajes", "cuanta ropa", "cuantos accesorios", "numero de trajes", "ropa hay"]):
        return "Pou tiene muchas prendas y accesorios, como sombreros, lentes, bigotes, ojos, bocas, ropa y fondos. El total exacto puede variar por version y desbloqueos."

    if contiene(texto, ["cuantos minijuegos", "cuantos juegos", "lista de minijuegos", "que minijuegos existen"]):
        return "Pou incluye muchos minijuegos para ganar monedas, como Food Drop, Sky Jump, Hill Drive, Color Match, Connect, Memory y otros segun la version."

    if contiene(texto, ["cuantas habitaciones", "cuartos tiene", "habitaciones tiene"]):
        return "Las secciones principales de Pou incluyen cocina, baño, dormitorio, laboratorio, sala de juegos y tienda o personalizacion."

    if contiene(texto, ["necesita internet", "sin internet", "offline", "online", "conexion"]):
        return "Pou se puede jugar principalmente sin internet para cuidar la mascota y jugar. Algunas funciones, anuncios, compras o sincronizacion pueden necesitar conexion."

    if contiene(texto, ["es gratis", "cuesta dinero", "hay que pagar"]):
        return "Pou suele jugarse gratis, pero puede incluir anuncios o compras dentro de la aplicacion segun la version y la tienda."

    if contiene(texto, ["puede morir", "muere pou", "si no cuido", "abandono a pou"]):
        return "Pou no funciona como un juego de muerte permanente: si lo descuidas, sus barras bajan y se ve mal, pero puedes recuperarlo cuidandolo otra vez."

    if contiene(texto, ["que es pou", "de que trata", "tipo de juego", "objetivo"]):
        return "Pou es un juego de mascota virtual donde cuidas a un personaje: lo alimentas, lo bañas, lo duermes, juegas minijuegos y compras objetos."

    if not es_pregunta_cantidad(texto):
        if contiene(texto, ["alimento", "alimentar", "comida", "hambre", "darle de comer"]):
            return "Para alimentar a Pou, entra a la cocina, elige una comida y dásela hasta que suba la barra de hambre."

        if contiene(texto, ["limpio", "limpiar", "bano", "baño", "sucio", "suciedad", "higiene", "jabon"]):
            return "Para limpiar a Pou, ve al baño y usa el jabón o el agua hasta que desaparezca la suciedad y suba la higiene."

        if contiene(texto, ["duerme", "dormir", "sueno", "sueño", "cansado", "energia", "energía", "luz"]):
            return "Para que Pou duerma, ve al dormitorio y apaga la luz. Eso recupera su energía."

        if contiene(texto, ["enfermo", "salud", "curar", "medicina", "pocion", "poción"]):
            return "Si Pou está enfermo, entra al laboratorio y usa una poción de salud para recuperarlo."

        if contiene(texto, ["moneda", "dinero", "comprar", "tienda", "gratis"]):
            return "Las monedas se consiguen principalmente jugando minijuegos. Sirven para comprar comida, ropa, accesorios, fondos y pociones."

        if contiene(texto, ["minijuego", "juego", "record", "puntaje", "sky jump", "food drop", "hill drive"]):
            return "Los minijuegos de Pou sirven para divertirse y ganar monedas. Mientras mejor sea tu puntaje, más monedas puedes conseguir."

        if contiene(texto, ["laboratorio", "lab"]):
            return "El laboratorio de Pou sirve para usar pociones, por ejemplo para recuperar salud, energía o cambiar ciertos estados del personaje."

        if contiene(texto, ["nivel", "subir", "experiencia", "progreso", "desbloquear"]):
            return "Pou sube de nivel cuando lo cuidas y juegas. Al subir de nivel se desbloquean más comidas, ropa, accesorios y decoraciones."

        if contiene(texto, ["ropa", "vestir", "color", "personalizar", "accesorio", "sombrero", "lentes", "apariencia"]):
            return "Puedes personalizar a Pou desde la tienda o el menú de apariencia, comprando ropa, colores, lentes, sombreros, fondos y accesorios."

        if contiene(texto, ["cuenta", "recuperar", "progreso", "celular", "telefono", "sesion"]):
            return "Para recuperar tu progreso de Pou, usa la misma cuenta o tienda de aplicaciones del dispositivo anterior y revisa las opciones de restauración."

    return None

class Mensaje(BaseModel):
    texto: str
    
@app.get("/")
def home():
    return {"message": "¡Bienvenido al Chatbot de Pou! Envíame una pregunta sobre el juego."}

@app.post("/chat")
def chat(data: Mensaje):
    intent, confianza = confianza_modelo(data.texto)

    respuesta = None
    origen = None
    groq_error = None

    # 1. Interacciones básicas (saludo, despedida, agradecimiento)
    tipo_basico = tipo_interaccion_basica(data.texto)
    if tipo_basico:
        respuesta = random.choice(respuestas[tipo_basico])
        origen = "local"

    # 2. Respuestas específicas por keywords
    if respuesta is None:
        respuesta = respuesta_especifica(data.texto)
        if respuesta:
            origen = "local"

    # 3. Modelo entrenado con data.xlsx — si la confianza es suficiente
    if respuesta is None and confianza >= CONFIDENCE_THRESHOLD and intent in respuestas:
        respuesta = random.choice(respuestas[intent])
        origen = "local"

    # 4. Si no pudo responder localmente, usar Groq como fallback
    if respuesta is None:
        respuesta_groq, groq_error = consultar_groq(data.texto)
        if respuesta_groq:
            guardar_en_memoria(data.texto, respuesta_groq, intent, confianza)
            respuesta = respuesta_groq
            origen = "groq"

    # 5. Si Groq tampoco respondió, mensaje genérico
    if respuesta is None:
        respuesta = random.choice(respuesta_fallback)
        origen = "fallback"

    return {
        "mensaje": data.texto,
        "intencion": intent,
        "respuesta": respuesta
    }
    


