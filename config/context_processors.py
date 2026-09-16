import json
from pathlib import Path

from django.conf import settings

from apps.login.services import get_data_user, get_user_image

def datos_encabezado(request):
  
    # request debe ser un HttpRequest de Django
    erp_session = request.session.get("erp_session")

    if not erp_session:
        return {}

    if hasattr(request, "_cached_hdr_data"):
        return request._cached_hdr_data

    try:
        resp = get_data_user(request)

        if resp.status_code == 200:
            data = resp.json().get("data", {})

            if isinstance(data, dict):
                result_data = data
            elif isinstance(data, list) and data:
                result_data = data[0]
            else:
                result_data = {}

            contexto = {
                "hdr_nombre": result_data.get("full_name", "No disponible"),
                "hdr_tipo_usuario": result_data.get(
                    "user_type", "No disponible"
                ),
                "hdr_email": result_data.get("email", "No disponible"),
                "hdr_rol": result_data.get("role", "None"),
                "hdr_idioma": result_data.get("language", "No disponible"),
                "hdr_imagen": get_user_image(resp, request),
            }
        else:
            contexto = {
                "hdr_nombre": "No disponible",
                "hdr_email": "No disponible",
                "hdr_tipo_usuario": "System User",
            }

    except Exception:
        contexto = {
            "hdr_nombre": "Error de conexión",
            "hdr_email": "No disponible",
        }

    request._cached_hdr_data = contexto
    return contexto

def menu_context(request):
    json_path = Path(__file__).resolve().parent / "../static/data/menu.json"
    with open(json_path, "r", encoding="utf-8") as f:
        menu_data = json.load(f)
    menu = {"menu_items": menu_data["nav"]["items"]}
    return menu