import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from app import db, app
from models import Region, Comuna

BASE_URL = "https://apis.digital.gob.cl/dpa"

# Configuración de la sesión con reintentos y tiempos de espera
session = requests.Session()
retries = Retry(
    total=5,
    backoff_factor=2,  # Incrementa el tiempo entre reintentos: 2s, 4s, 8s, etc.
    status_forcelist=[500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retries)
session.mount("https://", adapter)
session.mount("http://", adapter)

def poblar_regiones():
    """
    Pobla la tabla `Region` con los datos obtenidos de la API.
    """
    url_regiones = f"{BASE_URL}/regiones"
    try:
        response = session.get(url_regiones, timeout=10)
        response.raise_for_status()

        regiones = response.json()
        for region in regiones:
            existe_region = Region.query.filter_by(id=region["codigo"]).first()
            if not existe_region:
                nueva_region = Region(
                    id=region["codigo"],
                    nombre=region["nombre"]
                )
                db.session.add(nueva_region)
            time.sleep(1)  # Espera de 1 segundo entre solicitudes

        db.session.commit()
        print("Regiones agregadas correctamente.")
    except requests.RequestException as e:
        print(f"Error al obtener regiones: {e}")
    except Exception as e:
        print(f"Error al procesar regiones: {e}")

def poblar_comunas():
    """
    Pobla la tabla `Comuna` con los datos obtenidos de la API.
    """
    url_regiones = f"{BASE_URL}/regiones"
    try:
        response_regiones = session.get(url_regiones, timeout=10)
        response_regiones.raise_for_status()

        regiones = response_regiones.json()
        for region in regiones:
            codigo_region = region["codigo"]
            url_comunas = f"{BASE_URL}/regiones/{codigo_region}/comunas"

            try:
                response_comunas = session.get(url_comunas, timeout=10)
                response_comunas.raise_for_status()

                comunas = response_comunas.json()
                for comuna in comunas:
                    existe_comuna = Comuna.query.filter_by(id=comuna["codigo"]).first()
                    if not existe_comuna:
                        nueva_comuna = Comuna(
                            id=comuna["codigo"],
                            nombre=comuna["nombre"],
                            region_id=codigo_region
                        )
                        db.session.add(nueva_comuna)
                time.sleep(1)  # Espera de 1 segundo entre solicitudes
            except requests.RequestException as e:
                print(f"Error al obtener comunas para región {codigo_region}: {e}")
            except Exception as e:
                print(f"Error al procesar comunas para región {codigo_region}: {e}")

        db.session.commit()
        print("Comunas agregadas correctamente.")
    except requests.RequestException as e:
        print(f"Error al obtener regiones: {e}")
    except Exception as e:
        print(f"Error al procesar regiones: {e}")

if __name__ == "__main__":
    with app.app_context():
        print("Poblando tabla `Region`...")
        poblar_regiones()
        print("Poblando tabla `Comuna`...")
        poblar_comunas()
        print("¡Tablas pobladas exitosamente!")
