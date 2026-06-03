import pymongo
import redis
import time
import uuid

# =========================
# CONEXIÓN A BASES DE DATOS
# =========================

# Conexión a MongoDB (base de datos principal)
mongo_client = pymongo.MongoClient(
    "mongodb+srv://jbrea:Uade123@bbdd2.z7uyid0.mongodb.net/?appName=bbdd2"
)
db = mongo_client["clinica_medica"]
coleccion_turnos = db["turnos"]

# Conexión a Redis (para manejo de concurrencia)
redis_client = redis.Redis(
    host='redis-10452.crce220.us-east-1-4.ec2.cloud.redislabs.com',
    port=10452,
    username="master",
    password="Uade123+",
    decode_responses=True
)

# =========================
# INICIALIZACIÓN DE DATOS
# =========================

def inicializar_turnos():
    """
    Inserta datos de prueba en MongoDB.
    Se utiliza para simular un sistema real con turnos ya cargados.
    """

    # Descomentar si se quiere resetear la colección
    # coleccion_turnos.delete_many({})

    turnos_prueba = [
        {"_id": "T1", "medico": "Dr. Favaloro", "especialidad": "Cardiología", "horario": "09:00",
         "estado": "disponible", "paciente": None},
        {"_id": "T2", "medico": "Dr. Favaloro", "especialidad": "Cardiología", "horario": "09:30",
         "estado": "disponible", "paciente": None},
        {"_id": "T3", "medico": "Dr. Favaloro", "especialidad": "Cardiología", "horario": "10:00",
         "estado": "reservado", "paciente": "Marta"},
        {"_id": "T4", "medico": "Dra. Grierson", "especialidad": "Clínica Médica", "horario": "10:00",
         "estado": "disponible", "paciente": None},
        {"_id": "T5", "medico": "Dra. Grierson", "especialidad": "Clínica Médica", "horario": "10:30",
         "estado": "disponible", "paciente": None},
        {"_id": "T6", "medico": "Dra. Grierson", "especialidad": "Clínica Médica", "horario": "11:00",
         "estado": "reservado", "paciente": "Carlos"},
        {"_id": "T7", "medico": "Dr. Bilardo", "especialidad": "Traumatología", "horario": "15:00",
         "estado": "disponible", "paciente": None}
    ]

    coleccion_turnos.insert_many(turnos_prueba)
    print("✅ Base de datos inicializada con turnos de prueba.\n")

# =========================
# CONSULTA DE TURNOS
# =========================

def consultar_disponibles():
    """
    Muestra en consola todos los turnos que todavía no fueron reservados.
    """

    print("--- Turnos Disponibles ---")

    try:
        turnos = coleccion_turnos.find({"estado": "disponible"})

        for t in turnos:
            print(f"ID: {t['_id']} | Médico: {t['medico']} | Horario: {t['horario']}")

    except Exception as e:
        print(f"❌ Error al consultar turnos: {e}")

    print("-" * 30)

# =========================
# RESERVA DE TURNOS
# =========================

def reservar_turno(turno_id, nombre_paciente):
    """
    Intenta reservar un turno de forma segura evitando conflictos de concurrencia.

    Usa:
    - Redis: para generar un bloqueo (lock)
    - MongoDB: para actualizar el estado de forma atómica
    """

    # Validación básica de entrada
    if not nombre_paciente or not isinstance(nombre_paciente, str):
        print("❌ Nombre de paciente inválido.")
        return

    # Clave única para el lock
    lock_key = f"bloqueo:turno:{turno_id}"

    # Token único para asegurar que solo este proceso libere el lock
    token = str(uuid.uuid4())

    try:
        # Intento de adquirir el lock (NX = solo si no existe)
        bloqueo = redis_client.set(lock_key, token, nx=True, ex=10)

        if not bloqueo:
            print(f"[{nombre_paciente}] ⏳ El turno {turno_id} está siendo procesado por otro usuario.")
            return

        print(f"[{nombre_paciente}] 🔒 Lock adquirido. Procesando reserva...")

        # Simulación de procesamiento lento
        time.sleep(2)

        # =========================
        # OPERACIÓN ATÓMICA
        # =========================
        # Se actualiza SOLO si el turno sigue disponible
        resultado = coleccion_turnos.update_one(
            {"_id": turno_id, "estado": "disponible"},
            {"$set": {"estado": "reservado", "paciente": nombre_paciente}}
        )

        if resultado.modified_count == 1:
            print(f"[{nombre_paciente}] ✅ Reserva confirmada.")
        else:
            print(f"[{nombre_paciente}] ❌ El turno ya no está disponible.")

    except Exception as e:
        print(f"[{nombre_paciente}] ❌ Error durante la reserva: {e}")

    finally:
        # Liberar el lock SOLO si sigue siendo de este proceso
        try:
            current_value = redis_client.get(lock_key)

            if current_value == token:
                redis_client.delete(lock_key)
                print(f"[{nombre_paciente}] 🔓 Lock liberado.")
        except Exception as e:
            print(f"[{nombre_paciente}] ⚠ Error al liberar lock: {e}")

# =========================
# PROGRAMA PRINCIPAL
# =========================

if __name__ == "__main__":

    # Inicializa datos de prueba
    inicializar_turnos()

    # Muestra los turnos antes de reservar
    consultar_disponibles()

    # Simulación de concurrencia: dos usuarios intentando el mismo turno
    reservar_turno("T5", "Pedro")
    reservar_turno("T5", "Tomás")

    # Muestra resultado final
    consultar_disponibles()