import azure.functions as func
import json
from blob_utils import load_destinations, save_json_to_blob
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        contRep = req.route_params.get("contRep")
        updated_data = req.get_json()

        # Cargar destinos desde el blob
        destinations = load_destinations()

        # Verificar si el destino existe
        if contRep not in destinations:
            return func.HttpResponse(
                "Destination not found",
                status_code=404
            )

        # Actualizar el destino
        destinations[contRep] = updated_data

        # Guardar los destinos actualizados en el blob
        save_json_to_blob("connections", "destinations.json", destinations)

        return func.HttpResponse(
            "Destination updated successfully",
            status_code=200
        )
    except ValueError:
        return func.HttpResponse(
            "Invalid JSON format",
            status_code=400
        )
    except Exception as e:
        logging.error(f"Error in update_destination function: {e}")
        return func.HttpResponse(
            "Internal server error",
            status_code=500
        )
