import psycopg2
from src.schemas.vehiculo import TarjetaPropiedadCreate

def insert_tarjeta_propiedad(db: psycopg2.extensions.connection, tarjeta: TarjetaPropiedadCreate, placa: str, cilindraje: int, marca: str):
    """
    Inserta una nueva tarjeta de propiedad.
    Recibe la placa, cilindraje y marca para rellenar los datos duplicados de la tabla.
    No hace commit, para mantener la atomicidad de la transacción.
    """
    query = """
    INSERT INTO tarjetapropiedad (
        numero_tarjeta, nombre_propietario, cilindraje, documento_propietario, 
        marca, clase_vehiculo, modelo, capacidad, servicio, tipo_carroceria, 
        linea_vehiculo, numero_motor, combustible, color, placa, fk_placavehiculo
    ) VALUES (
        %(numero_tarjeta)s, %(nombre_propietario)s, %(cilindraje)s, %(documento_propietario)s, 
        %(marca)s, %(clase_vehiculo)s, %(modelo)s, %(capacidad)s, %(servicio)s, %(tipo_carroceria)s, 
        %(linea_vehiculo)s, %(numero_motor)s, %(combustible)s, %(color)s, %(placa)s, %(fk_placavehiculo)s
    )
    ON CONFLICT (numero_tarjeta) DO UPDATE SET
        nombre_propietario = EXCLUDED.nombre_propietario,
        documento_propietario = EXCLUDED.documento_propietario,
        cilindraje = EXCLUDED.cilindraje,
        marca = EXCLUDED.marca,
        clase_vehiculo = EXCLUDED.clase_vehiculo,
        modelo = EXCLUDED.modelo,
        capacidad = EXCLUDED.capacidad,
        servicio = EXCLUDED.servicio,
        tipo_carroceria = EXCLUDED.tipo_carroceria,
        linea_vehiculo = EXCLUDED.linea_vehiculo,
        numero_motor = EXCLUDED.numero_motor,
        combustible = EXCLUDED.combustible,
        color = EXCLUDED.color,
        placa = EXCLUDED.placa,
        fk_placavehiculo = EXCLUDED.fk_placavehiculo
    """

    data = tarjeta.model_dump()
    data["placa"] = placa
    data["fk_placavehiculo"] = placa
    data["cilindraje"] = cilindraje
    data["marca"] = marca

    with db.cursor() as cursor:
        cursor.execute(query, data)
        return True

def find_by_placa(db: psycopg2.extensions.connection, placa: str):
    """
    Obtiene la tarjeta de propiedad de un vehículo por su placa.
    """
    query = """
        SELECT numero_tarjeta, nombre_propietario, cilindraje, documento_propietario,
               marca, clase_vehiculo, modelo, capacidad, servicio, tipo_carroceria,
               linea_vehiculo, numero_motor, combustible, color, placa
        FROM tarjetapropiedad
        WHERE fk_placavehiculo = %(placa)s
    """
    with db.cursor() as cursor:
        cursor.execute(query, {"placa": placa})
        resultado = cursor.fetchone()
        return dict(resultado) if resultado else None

