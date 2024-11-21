import azure.functions as func
import os
import logging
import json


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Received request to test AzureWebJobsStorage connection string.")

    # Obtener la variable de entorno
    connection_string = os.getenv("AzureWebJobsStorage")

    if not connection_string:
        logging.warning("AzureWebJobsStorage is not configured or accessible.")
        return func.HttpResponse(
            json.dumps(
                {"message": "AzureWebJobsStorage is not configured or accessible."}
            ),
            status_code=200,  # Retorna 200 para indicar "no hay" en lugar de un error
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
        )

    # Devuelve parte del connection string por seguridad
    logging.info("AzureWebJobsStorage connection string retrieved successfully.")
    response = {
        "message": "AzureWebJobsStorage is configured.",
        "connection_string_preview": connection_string[:50]
        + "...",  # Solo una parte visible
    }

    return func.HttpResponse(
        json.dumps(response),
        status_code=200,
        mimetype="application/json",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
    )
