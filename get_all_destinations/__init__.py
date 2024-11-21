import azure.functions as func
import json
from blob_utils import load_destinations
import logging
import os


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Received request to get all destinations.")

    # Verifica la conexión a Azure Blob Storage
    # connection_string = os.getenv("AzureWebJobsStorage")
    # if not connection_string:
    #     logging.error("AzureWebJobsStorage is not set in the environment variables.")
    #     return func.HttpResponse(
    #         "AzureWebJobsStorage is not configured.",
    #         status_code=500,
    #         headers={
    #             "Access-Control-Allow-Origin": "*",
    #             "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    #             "Access-Control-Allow-Headers": "Content-Type, Authorization",
    #         },
    #     )

    # Log para confirmar que se lee la cadena de conexión
    logging.info(f"AzureWebJobsStorage connection string: {connection_string[:50]}...")

    # Manejo de solicitudes OPTIONS para CORS
    if req.method == "OPTIONS":
        logging.info("Handling OPTIONS request for CORS preflight.")
        return func.HttpResponse(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
        )

    try:
        logging.info("Attempting to load destinations from blob storage.")

        # Cargar destinos desde el blob
        destinations = load_destinations()

        if destinations:
            logging.info(f"Loaded {len(destinations)} destinations successfully.")
        else:
            logging.warning("No destinations found in the blob storage.")

        # Responder con los datos cargados
        response_content = json.dumps(destinations)
        logging.info("Returning response with destinations data.")

        return func.HttpResponse(
            response_content,
            status_code=200,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
        )

    except FileNotFoundError as fnfe:
        logging.error(f"File not found: {fnfe}", exc_info=True)
        return func.HttpResponse(
            "File not found in blob storage.",
            status_code=404,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
        )
    except Exception as e:
        logging.error(f"Unexpected error while loading destinations: {str(e)}", exc_info=True)
        return func.HttpResponse(
            f"Error loading destinations: {str(e)}",
            status_code=500,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
        )
