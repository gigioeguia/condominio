import base64
import json
import os, requests
from dotenv import load_dotenv

load_dotenv()

ERP_BASE_URL = os.getenv("ERP_BASE_URL")
ERP_API_KEY = os.getenv("ERP_API_KEY")
ERP_APISECRET = os.getenv("ERP_APISECRET")
LOGIN_URL = f"{ERP_BASE_URL}/api/method/login"

HEADERS = {
    "Authorization": f"token {ERP_API_KEY}:{ERP_APISECRET}",
    "Content-Type": "application/json",
    "Cookie": f"sid={os.getenv('ERP_SESSION_ID')}"
}

def get_logged_user(response):
    url = f"{ERP_BASE_URL}/api/method/frappe.auth.get_logged_user"
    try:
        response_user = requests.get(
            url,
            cookies=response.cookies,
            timeout=10,
        )
    except requests.RequestException as exc:
        return None

    try:
        data = response_user.json()
    except ValueError:
        return None

    if response_user.status_code == 403:
        return None

    if response_user.status_code != 200:
        return None

    user_name = data.get("message")

    return user_name or None

def login_user(username,password):
    return requests.post(LOGIN_URL, data={"usr": username, "pwd": password})

def get_user_roles(username, sid):
    url = f"{ERP_BASE_URL}/api/resource/User/{username}"
    cookies = {"sid": sid}
    resp = requests.get(url, cookies=cookies)
    if resp.status_code == 200:
        data = resp.json()
        return [r["role"] for r in data["data"]["roles"]]
    return []

def get_data_user(request):
    fields=["name","full_name","email","language","user_type","roles","user_image"]
    url = f"{ERP_BASE_URL}/api/resource/User/{request.session.get("username")}?fields={json.dumps(fields)}"
    return requests.get(url, headers=HEADERS)

def get_user_image(resp, request):
    if resp.status_code != 200:
        return None

    data = resp.json().get("data", {})
    if isinstance(data, dict):
        image_path = data.get("user_image") or data.get("data", {}).get("user_image")

    elif isinstance(data, list) and len(data) > 0:
        image_path = data[0].get("user_image")

    else:
        image_path = None
        
    if image_path is not None:
        image_url = f"{ERP_BASE_URL}{image_path}"
        img_resp = requests.get(image_url, headers=HEADERS)
        if img_resp.status_code != 200:
            return None
        
        b64_img = base64.b64encode(img_resp.content).decode("utf-8")
        return f"data:image/jpeg;base64,{b64_img}"

def get_logout(sid):
    logout_url = f"{ERP_BASE_URL}/api/method/logout"
    headers = {
        "Authorization": f"token {ERP_API_KEY}:{ERP_APISECRET}",
        "Content-Type": "application/json",
        "Cookie": f"sid={sid}"
    }
    requests.post(logout_url, headers=headers)
