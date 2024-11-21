import azure.functions as func
from azure.storage.blob import BlobServiceClient
import os
import logging
import json


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Received request to list containers in Azure Blob Storage.")

    # Obtener el connection string desde las variables de entorno
    connection_string = os.getenv("AzureWebJobsStorage")
    if not connection_string:
        logging.error("AzureWebJobsStorage is not configured.")
        return func.HttpResponse(
            json.dumps({"message": "AzureWebJobsStorage is not configured."}),
            status_code=200,
            mimetype="application/json",
        )

    try:
        # Inicializar el cliente de Blob Service
        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        logging.info("BlobServiceClient initialized successfully.")

        # Listar todos los contenedores
        containers = blob_service_client.list_containers()
        container_names = [container.name for container in containers]
        logging.info(f"Containers found: {container_names}")

        return func.HttpResponse(
            json.dumps(
                {
                    "message": "Containers retrieved successfully.",
                    "containers": container_names,
                }
            ),
            status_code=200,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
        )
    except Exception as e:
        logging.error(f"Error listing containers: {e}")
        return func.HttpResponse(
            json.dumps({"message": "Error listing containers.", "error": str(e)}),
            status_code=500,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
        )
