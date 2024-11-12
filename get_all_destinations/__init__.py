import azure.functions as func
import json
from blob_utils import load_destinations
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Received request to get all destinations.")
    
    # Manejo de solicitudes OPTIONS para CORS
    if req.method == "OPTIONS":
        logging.info("Received OPTIONS request for CORS preflight.")
        return func.HttpResponse(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )

    try:
        logging.info("Attempting to load destinations from blob storage.")
        
        # Cargar destinos desde el blob
        destinations = load_destinations()
        
        if destinations:
            logging.info(f"Loaded destinations successfully: {len(destinations)} items found.")
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
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )

    except ValueError as ve:
        logging.error(f"ValueError encountered: {str(ve)}")
        return func.HttpResponse(
            "Invalid JSON format or data in blob.",
            status_code=400,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )

    except Exception as e:
        logging.error(f"Unexpected error while loading destinations: {str(e)}")
        return func.HttpResponse(
            f"Error loading destinations: {str(e)}",
            status_code=500,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
