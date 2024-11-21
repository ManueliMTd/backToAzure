import os
import json
import logging
import hashlib
import base64
from azure.storage.blob import BlobServiceClient
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

# Configuración de logging
logging.basicConfig(level=logging.INFO)

# Configuración de la cadena de conexión desde una variable de entorno
connection_string = os.getenv("AzureWebJobsStorage")
if not connection_string:
    logging.error("La cadena de conexión de Blob Storage no está configurada.")
    raise ValueError("La cadena de conexión de Blob Storage no está configurada.")
else:
    logging.info(
        f"Cadena de conexión obtenida: {connection_string[:50]}..."
    )  # Mostrar solo una parte por seguridad

# Inicializa el cliente de Blob Storage
try:
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    logging.info("Cliente de Blob Service inicializado correctamente.")
except Exception as e:
    logging.error(f"Error al inicializar el cliente de Blob Service: {e}")
    raise


def load_json_from_blob(container_name: str, blob_name: str) -> dict:
    """
    Carga un archivo JSON desde Azure Blob Storage y lo convierte en un diccionario de Python.
    """
    logging.info(
        f"Cargando JSON desde el contenedor '{container_name}', blob '{blob_name}'..."
    )
    try:
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)

        # Descargar el contenido del blob
        download_stream = blob_client.download_blob()
        data = json.loads(download_stream.readall())
        logging.info(
            f"Archivo JSON '{blob_name}' cargado correctamente desde '{container_name}'."
        )
        return data
    except Exception as e:
        logging.error(
            f"Error cargando JSON desde blob '{blob_name}' en contenedor '{container_name}': {e}"
        )
        raise


def save_json_to_blob(container_name: str, blob_name: str, data: dict) -> None:
    """
    Guarda un diccionario de Python como un archivo JSON en Azure Blob Storage.
    """
    logging.info(
        f"Guardando JSON en el contenedor '{container_name}', blob '{blob_name}'..."
    )
    try:
        json_data = json.dumps(data)
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(json_data, overwrite=True)
        logging.info(
            f"Archivo JSON '{blob_name}' guardado correctamente en '{container_name}'."
        )
    except Exception as e:
        logging.error(
            f"Error guardando JSON en blob '{blob_name}' en contenedor '{container_name}': {e}"
        )
        raise


def load_connections() -> dict:
    """Cargar el archivo 'connections.json' desde el contenedor de Azure Blob Storage."""
    logging.info("Cargando 'connections.json' desde el contenedor 'connections'...")
    return load_json_from_blob("connections", "connections.json")


def load_destinations() -> dict:
    """Cargar el archivo 'destinations.json' desde el contenedor de Azure Blob Storage."""
    logging.info("Cargando 'destinations.json' desde el contenedor 'connections'...")
    return load_json_from_blob("connections", "destinations.json")


def generate_secKey(message: str) -> str:
    logging.info(f"Generando SecKey para el mensaje: {message}")
    hash_object = hashlib.sha256(message.encode())
    sec_key = base64.b64encode(hash_object.digest()).decode("utf-8")
    logging.info(f"SecKey generado: {sec_key}")
    return sec_key


def derive_key_from_docId(docId: str) -> bytes:
    """Deriva una clave de cifrado a partir del docId utilizando SHA-256"""
    logging.info(f"Derivando clave de cifrado desde docId: {docId}")
    key = hashlib.sha256(docId.encode()).digest()
    logging.info(f"Clave derivada: {key.hex()[:16]}...")  # Muestra parte de la clave
    return key


def encrypt_data(data: bytes, key: bytes) -> bytes:
    logging.info("Cifrando datos...")
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()

    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    logging.info("Datos cifrados correctamente.")
    return iv + encrypted_data


def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    logging.info("Descifrando datos...")
    iv = encrypted_data[:16]
    encrypted_data = encrypted_data[16:]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()

    logging.info("Datos descifrados correctamente.")
    return decrypted_data
