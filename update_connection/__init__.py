import azure.functions as func
import json
from blob_utils import load_connections, save_json_to_blob
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Manejo de solicitudes OPTIONS para CORS
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )

    try:
        connection_name = req.route_params.get("connection_name")
        updated_data = req.get_json()

        # Cargar conexiones desde el blob
        connections = load_connections()

        # Verificar si la conexión existe
        if connection_name not in connections:
            return func.HttpResponse(
                "Connection not found",
                status_code=404,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                }
            )

        # Actualizar la conexión que va a subir
        connections[connection_name] = updated_data

        # Guardar las conexiones actualizadas en el blob
        save_json_to_blob("connections", "connections.json", connections)

        return func.HttpResponse(
            "Connection updated successfully",
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
    except ValueError:
        return func.HttpResponse(
            "Invalid JSON format",
            status_code=400,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
    except Exception as e:
        logging.error(f"Error in update_connection function: {e}")
        return func.HttpResponse(
            "Internal server error",
            status_code=500,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
