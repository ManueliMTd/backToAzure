import azure.functions as func
import json
from blob_utils import load_connections

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Manejo de solicitudes OPTIONS para CORS
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )

    try:
        # Cargar conexiones desde el blob
        connections = load_connections()
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
    except Exception as e:
        return func.HttpResponse(
            f"Error loading connections: {str(e)}",
            status_code=500,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
