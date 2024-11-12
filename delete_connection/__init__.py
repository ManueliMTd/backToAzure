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
                "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )

    try:
        connection_name = req.route_params.get("connection_name")

        # Cargar conexiones desde el blob
        connections = load_connections()

        # Verificar si la conexión existe
        if connection_name not in connections:
            return func.HttpResponse(
                "Connection not found",
                status_code=404,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                }
            )

        # Eliminar la conexión
        del connections[connection_name]

        # Guardar las conexiones actualizadas en el blob
        save_json_to_blob("connections", "connections.json", connections)

        return func.HttpResponse(
            "Connection deleted successfully",
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
    except Exception as e:
        logging.error(f"Error in delete_connection function: {e}")
        return func.HttpResponse(
            "Internal server error",
            status_code=500,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
