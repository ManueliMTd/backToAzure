import azure.functions as func
import json
from blob_utils import load_destinations, save_json_to_blob  # Importar funciones auxiliares
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
        # Parsear la solicitud JSON
        destination_data = req.get_json()

        # Validar que se hayan enviado los campos necesarios
        if "contRep" not in destination_data or "connection_name" not in destination_data:
            return func.HttpResponse(
                "Missing 'contRep' or 'connection_name' in request body",
                status_code=400,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                }
            )

        # Cargar destinos existentes desde el blob
        destinations = load_destinations()

        # Verificar si el destino ya existe
        if destination_data["contRep"] in destinations:
            return func.HttpResponse(
                "Destination already exists",
                status_code=400,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                }
            )

        # Agregar el nuevo destino
        destinations[destination_data["contRep"]] = destination_data

        # Guardar los destinos actualizados en el blob
        save_json_to_blob("connections", "destinations.json", destinations)

        return func.HttpResponse(
            "Destination added successfully",
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
        logging.error(f"Error in create_destination function: {e}")
        return func.HttpResponse(
            "Internal server error",
            status_code=500,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
