import azure.functions as func
import os
import logging
import json
# from azure.storage.blob import BlobServiceClient


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Inicio de ejecución de 'get_all_destinations'.")

    try:
        # Obtener la variable de entorno AzureWebJobsStorage
        connection_string = os.getenv("AzureWebJobsStorage")
        if not connection_string:
            logging.warning("AzureWebJobsStorage no configurada o no accesible.")
            return func.HttpResponse(
                json.dumps(
                    {"message": "AzureWebJobsStorage no configurada o no accesible."}
                ),
                status_code=200,
                mimetype="application/json",
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization",
                },
            )

        # Mostrar el connection string completo (solo para depuración)
        logging.info(f"Connection string completo: {connection_string}")
        # blob_service_client = BlobServiceClient.from_connection_string(
        #     connection_string
        # )

        return func.HttpResponse(
            json.dumps(
                {
                    "message": "AzureWebJobsStorage configurada correctamente.",
                    "connection_string": connection_string,
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
        logging.error(f"Error en 'get_all_destinations': {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"message": "Error interno.", "error": str(e)}),
            status_code=500,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
        )
