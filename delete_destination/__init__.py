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
                "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )

    try:
        contRep = req.route_params.get("contRep")

        # Cargar destinos desde el blob
        destinations = load_destinations()

        # Verificar si el destino existe
        if contRep not in destinations:
            return func.HttpResponse(
                "Destination not found",
                status_code=404,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                }
            )

        # Eliminar el destino
        del destinations[contRep]

        # Guardar los destinos actualizados en el blob
        save_json_to_blob("connections", "destinations.json", destinations)

        return func.HttpResponse(
            "Destination deleted successfully",
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
    except Exception as e:
        logging.error(f"Error in delete_destination function: {e}")
        return func.HttpResponse(
            "Internal server error",
            status_code=500,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
