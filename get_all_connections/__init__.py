import azure.functions as func
import json
from blob_utils import load_connections
import logging


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Received request to get all connections.")

    # Manejo de solicitudes OPTIONS para CORS
    if req.method == "OPTIONS":
        logging.info("Handling OPTIONS request for CORS preflight.")
        return func.HttpResponse(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )

    try:
        logging.info("Attempting to load connections from blob storage.")

        # Cargar conexiones desde el blob
        connections = load_connections()
        logging.info(f"Loaded {len(connections)} connections successfully.")

        return func.HttpResponse(
            json.dumps(connections),
            status_code=200,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
    except FileNotFoundError as fnfe:
        logging.error(f"File not found: {fnfe}", exc_info=True)
        return func.HttpResponse(
            "File not found in blob storage.",
            status_code=404,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
    except Exception as e:
        logging.error(f"Unexpected error while loading connections: {str(e)}", exc_info=True)
        return func.HttpResponse(
            f"Error loading connections: {str(e)}",
            status_code=500,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
