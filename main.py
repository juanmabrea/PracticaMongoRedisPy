import pymongo
import redis
import time


mongo_client = pymongo.MongoClient("mongodb+srv://jbrea:jbrea@bbdd2.z7uyid0.mongodb.net/?appName=bbdd2")
db = mongo_client["clinica_medica"]
coleccion_turnos = db["turnos"]

redis_client = redis.Redis(host='redis-10452.crce220.us-east-1-4.ec2.cloud.redislabs.com:10452', port=6379, db=0, decode_responses=True)


def inicializar_turnos():

    coleccion_turnos.delete_many({})
    turnos_prueba = [
        {"_id": "T1", "medico": "Dra. Gomez", "horario": "10:00", "estado": "disponible", "paciente": None},
        {"_id": "T2", "medico": "Dr. Perez", "horario": "10:30", "estado": "disponible", "paciente": None},
        {"_id": "T3", "medico": "Dra. Gomez", "horario": "11:00", "estado": "disponible", "paciente": None}
    ]
    coleccion_turnos.insert_many(turnos_prueba)
    print("Base de datos MongoDB inicializada con turnos de prueba.\n")


()