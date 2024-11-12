import os
import sys
import logging
import hashlib
import base64
from azure.storage.blob import BlobServiceClient
from azure.functions import HttpRequest, HttpResponse
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from http.client import HTTPException

# Añadir el directorio padre a sys.path para importar módulos externos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from blob_utils import load_destinations

logger = logging.getLogger("azure")


# Funciones auxiliares para generar claves y cifrar/descifrar
def generate_secKey(message: str) -> str:
    hash_object = hashlib.sha256(message.encode())
    sec_key = base64.b64encode(hash_object.digest()).decode("utf-8")
    logger.info(f"SecKey generado: {sec_key}")
    return sec_key


def derive_key_from_docId(docId: str) -> bytes:
    return hashlib.sha256(docId.encode()).digest()


def encrypt_data(data: bytes, key: bytes) -> bytes:
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return iv + encrypted_data


def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    iv = encrypted_data[:16]
    encrypted_data = encrypted_data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
    return decrypted_data


def get_destination(contRep: str) -> dict:
    # Cargar configuraciones y obtener el destino específico
    destinations = load_destinations()
    if contRep in destinations:
        return destinations[contRep]
    else:
        raise ValueError(f"Destino '{contRep}' no encontrado.")


# Punto de entrada principal de la función de Azure
def main(req: HttpRequest) -> HttpResponse:
    method = req.method
    command = req.params.get("command", "get" if method == "GET" else "create")

    if method == "GET":
        return handle_get(req, command)
    elif method == "POST":
        return handle_post(req, command)
    else:
        return HttpResponse("Método no permitido", status_code=405)


# Procesamiento del método GET
def handle_get(req: HttpRequest, command: str) -> HttpResponse:
    pVersion = req.params.get("pVersion")
    contRep = req.params.get("contRep")
    docId = req.params.get("docId")

    if command == "serverInfo":
        return handle_server_info(pVersion, contRep)

    if not contRep or not docId:
        return HttpResponse("Faltan parámetros requeridos para 'get'", status_code=400)

    try:
        connection_info = get_destination(contRep)
        cloud_type = connection_info["cloud"]
        connection_data = connection_info["data"]

        if cloud_type == "AZURE":
            blob_service_client = BlobServiceClient.from_connection_string(
                connection_data["connection_string"]
            )
            container_client = blob_service_client.get_container_client(
                connection_data["container_name"]
            )
        else:
            raise ValueError(f"Tipo de nube no soportado: {cloud_type}")

    except ValueError as e:
        logger.error(str(e))
        return HttpResponse(str(e), status_code=400)

    if command == "get":
        encryption_key = derive_key_from_docId(docId)
        found_blob = None
        try:
            blobs_list = container_client.list_blobs(name_starts_with=f"{contRep}/")
            for blob in blobs_list:
                if docId in blob.name:
                    found_blob = blob.name
                    break

            if found_blob:
                blob_client = container_client.get_blob_client(found_blob)
                download_stream = blob_client.download_blob()
                encrypted_content = download_stream.readall()

                try:
                    decrypted_content = decrypt_data(encrypted_content, encryption_key)
                except Exception as e:
                    logger.error(f"Error al descifrar el documento {docId}: {e}")
                    return HttpResponse(
                        f"Error al descifrar el documento: {str(e)}", status_code=500
                    )

                temp_file_path = f"/tmp/{docId}.pdf"
                with open(temp_file_path, "wb") as temp_file:
                    temp_file.write(decrypted_content)

                response = func.FileResponse(
                    temp_file_path, media_type="application/pdf"
                )
                response.call_on_close(lambda: os.remove(temp_file_path))
                return response
            else:
                logger.error(f"Documento {docId} no encontrado en Azure Blob Storage.")
                return HttpResponse(
                    f"Documento con docId '{docId}' no encontrado en Azure Blob Storage.",
                    status_code=404,
                )

        except Exception as e:
            logger.error(f"Error al recuperar el documento de Azure Blob Storage: {e}")
            return HttpResponse(
                f"Error al recuperar el documento: {str(e)}", status_code=500
            )

    # Manejo del comando 'info'
    elif command == "info":
        found_blob = None
        try:
            blobs_list = container_client.list_blobs(name_starts_with=f"{contRep}/")
            for blob in blobs_list:
                if docId in blob.name:
                    found_blob = blob.name
                    break

            if found_blob:
                blob_client = container_client.get_blob_client(found_blob)
                props = blob_client.get_blob_properties()

                return HttpResponse(
                    content={
                        "message": "Información del documento recuperada",
                        "command": command,
                        "contRep": contRep,
                        "docId": docId,
                        "status": "active",
                        "file_size": f"{props.size / 1024} KB",
                        "last_modified": props.last_modified,
                    },
                    status_code=200,
                )
            else:
                return HttpResponse(
                    f"Documento con docId '{docId}' no encontrado en Azure Blob Storage.",
                    status_code=404,
                )

        except Exception as e:
            logger.error(f"Error al recuperar información del documento: {e}")
            return HttpResponse(
                f"Error al recuperar información del documento: {str(e)}",
                status_code=500,
            )

    else:
        return HttpResponse("Comando no reconocido", status_code=400)


# Manejo del comando 'serverInfo'
def handle_server_info(pVersion, contRep):
    server_info = (
        f'serverStatus="running";'
        f'serverVendorId="Auritas-ContentServer-4.5";'
        f'serverVersion="4.5.1";'
        f'serverTime="12:00:00";'
        f'serverDate="2024-10-24";'
        f'pVersion="{pVersion or "0047"}";\r\n'
    )

    if contRep:
        repository_info = (
            f'contRep="{contRep}";'
            f'contRepDescription="Repositorio de contenido para {contRep}";'
            f'contRepStatus="running";'
            f'contRepStatusDescription="Repositorio de contenido operativo";'
            f'pVersion="{pVersion or "0047"}";\r\n'
        )
        response = server_info + repository_info
    else:
        response = server_info

    return HttpResponse(content=response, mimetype="text/plain", status_code=200)


# Procesamiento del método POST
def handle_post(req: HttpRequest, command: str) -> HttpResponse:
    pVersion = req.params.get("pVersion")
    contRep = req.params.get("contRep")
    docId = req.params.get("docId")

    if not contRep or not docId:
        return HttpResponse(
            "Faltan parámetros requeridos para 'create'", status_code=400
        )

    try:
        connection_info = get_destination(contRep)
        cloud_type = connection_info["cloud"]
        connection_data = connection_info["data"]
    except ValueError as e:
        logger.error(str(e))
        return HttpResponse(str(e), status_code=400)

    encryption_key = derive_key_from_docId(docId)
    body = req.get_body()
    content_type = req.headers.get("Content-Type", "")
    boundary = content_type.split("boundary=")[-1]

    parts = body.split(f"--{boundary}".encode())
    file_info = []

    for part in parts:
        part_str = part.decode(errors="replace")
        if "Content-Disposition" in part_str and "filename" in part_str:
            filename_start = part_str.find('filename="') + 10
            filename_end = part_str.find('"', filename_start)
            filename = part_str[filename_start:filename_end]
            file_start = part.find(b"\r\n\r\n") + 4
            file_content = part[file_start:].strip(b"--\r\n")

            try:
                encrypted_content = encrypt_data(file_content, encryption_key)
            except Exception as e:
                logger.error(f"Error al cifrar el archivo {filename}: {e}")
                return HttpResponse(
                    f"Error al cifrar el archivo: {str(e)}", status_code=500
                )

            if cloud_type == "AZURE":
                blob_name = f"{contRep}/{docId}_{filename}"
                blob_client = (
                    BlobServiceClient.from_connection_string(
                        connection_data["connection_string"]
                    )
                    .get_container_client(connection_data["container_name"])
                    .get_blob_client(blob_name)
                )
                try:
                    blob_client.upload_blob(encrypted_content, overwrite=True)
                    logger.debug(f"Archivo subido a Azure Blob: {blob_name}")
                    file_info.append(
                        {
                            "filename": filename,
                            "blob_name": blob_name,
                            "size": len(file_content),
                        }
                    )
                except Exception as e:
                    logger.error(f"Error al subir archivo a Azure Blob: {e}")
                    return HttpResponse(
                        f"Error al subir archivo: {str(e)}", status_code=500
                    )

    return HttpResponse(
        content={
            "message": "Archivos subidos exitosamente.",
            "status": 201,
            "details": {
                "command": command,
                "contRep": contRep,
                "docId": docId,
                "files": file_info,
            },
        },
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
        status_code=201,
    )
