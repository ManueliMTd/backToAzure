import azure.functions as func
from azure.storage.blob import BlobServiceClient
import os
import json
import logging


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Received request to test Blob Storage connection.")

    # Obtener la variable de entorno
    connection_string = os.getenv("AzureWebJobsStorage")
    if not connection_string:
        return func.HttpResponse(
            json.dumps({"message": "AzureWebJobsStorage is not configured."}),
            status_code=200,
            mimetype="application/json",
        )

    try:
        # Inicializa el cliente de Blob Storage
        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        logging.info("BlobServiceClient initialized successfully.")

        # Lista los contenedores
        containers = blob_service_client.list_containers()
        container_names = [container.name for container in containers]

        return func.HttpResponse(
            json.dumps(
                {
                    "message": "Blob Storage is accessible.",
                    "containers": container_names,
                }
            ),
            status_code=200,
            mimetype="application/json",
        )
    except Exception as e:
        logging.error(f"Error accessing Blob Storage: {e}")
        return func.HttpResponse(
            json.dumps({"message": "Error accessing Blob Storage.", "error": str(e)}),
            status_code=500,
            mimetype="application/json",
        )
