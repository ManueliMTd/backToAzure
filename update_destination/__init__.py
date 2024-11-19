import azure.functions as func
import json
from blob_utils import load_destinations, save_json_to_blob
import logging


def main(req: func.HttpRequest) -> func.HttpResponse:
    # Manejo de solicitudes OPTIONS para CORS
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
        )

    try:
        # Obtener el identificador del destino a actualizar
        contRep = req.route_params.get("contRep")
        updated_data = req.get_json()

        # Validar que el campo necesario esté presente en los datos
        connection_name = updated_data.get("connection_name")

        if not connection_name:
            return func.HttpResponse(
                "Missing 'connection_name' in request body",
                status_code=400,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization",
                },
            )

        # Cargar destinos desde el blob
        destinations = load_destinations()

        # Verificar si el destino existe
        if contRep not in destinations:
            return func.HttpResponse(
                "Destination not found",
                status_code=404,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization",
                },
            )

        # Actualizar el destino
        destinations[contRep] = connection_name

        # Guardar los destinos actualizados en el blob
        save_json_to_blob("connections", "destinations.json", destinations)

        return func.HttpResponse(
            "Destination updated successfully",
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
        )

    except ValueError:
        return func.HttpResponse(
            "Invalid JSON format",
            status_code=400,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
        )
    except Exception as e:
        logging.error(f"Error in update_destination function: {e}")
        return func.HttpResponse(
            "Internal server error",
            status_code=500,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
        )
