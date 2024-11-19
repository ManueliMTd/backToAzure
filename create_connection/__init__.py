import azure.functions as func
import json
from blob_utils import load_connections, save_json_to_blob  # Importar funciones auxiliares
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Manejo de solicitudes OPTIONS para CORS
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )

    try:
        connection_data = req.get_json()

        # Validar que se haya enviado un nombre de conexión
        if "connection_name" not in connection_data:
            return func.HttpResponse(
                "Missing 'name' in request body",
                status_code=400,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                }
            )

        # Cargar conexiones existentes desde el blob
        connections = load_connections()

        # Verificar si la conexión ya existe
        if connection_data["connection_name"] in connections:
            return func.HttpResponse(
                "Connection already exists",
                status_code=400,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                }
            )

        # Agregar la nueva conexión
        connections[connection_data["connection_name"]] = connection_data

        # Guardar las conexiones actualizadas en el blob
        save_json_to_blob("connections", "connections.json", connections)

        return func.HttpResponse(
            "Connection added successfully",
            status_code=201,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )

    except ValueError:
        return func.HttpResponse(
            "Invalid JSON format",
            status_code=400,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
    except Exception as e:
        logging.error(f"Error in create_connection function: {e}")
        return func.HttpResponse(
            "Internal server error",
            status_code=500,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
