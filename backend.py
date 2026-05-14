import requests
import os
import mimetypes

# ----------------- 核心设置 -----------------
# 确保 URL 末尾没有斜杠
PB_URL = "https://nonperversive-maggie-bibliological.ngrok-free.dev"
# --------------------------------------------

auth_store = {
    "token": None,
    "user_id": None,
    "user_email": None
}

def login(email, password):
    """
    用户登录 - 修复 Invalid Email/Password 问题
    """
    endpoint = f"{PB_URL}/api/collections/users/auth-with-password"
    # 使用 strip() 防止输入框中意外的空格导致验证失败
    payload = {
        "identity": email.strip(),
        "password": password.strip()
    }
    
    try:
        # 必须使用 json=payload 确保发送的是 application/json 格式
        response = requests.post(endpoint, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            auth_store["token"] = data["token"]
            auth_store["user_id"] = data["record"]["id"]
            auth_store["user_email"] = data["record"]["email"]
            print(f"Login Success: {auth_store['user_email']}")
            return True, "Login Successful"
        else:
            print(f"Login Failed Debug: {response.status_code} - {response.text}")
            return False, "Invalid Email or Password"
    except Exception as e:
        print(f"Login Error: {e}")
        return False, "Connection Error"

def get_history():
    """
    获取历史记录 - 解决 404 问题
    """
    endpoint = f"{PB_URL}/api/collections/reports/records"
    
    # PocketBase 的 Token 验证有时需要明确的格式
    headers = {}
    if auth_store["token"]:
        # 注意：如果之前直接传 token 不行，请尝试添加 "Bearer " 前缀
        headers["Authorization"] = auth_store["token"]

    try:
        # sort=-created 确保最新举报排在最前面
        response = requests.get(endpoint, params={"sort": "-created"}, headers=headers, timeout=10)
        
        print(f"DEBUG History Request: {response.status_code}")
        if response.status_code == 200:
            return response.json().get("items", [])
        else:
            print(f"History Error Details: {response.text}")
            return None
    except Exception as e:
        print(f"History Fetch Error: {e}")
        return None

def register(email, password, password_confirm):
    if password != password_confirm:
        return False, "Passwords do not match"
    endpoint = f"{PB_URL}/api/collections/users/records"
    payload = {
        "email": email, "password": password, 
        "passwordConfirm": password_confirm, "emailVisibility": True
    }
    try:
        response = requests.post(endpoint, json=payload, timeout=10)
        return (True, "Registered!") if response.status_code == 200 else (False, response.text)
    except:
        return False, "Connection Error"

def submit_report(location_text, desc_text, photo_path=None):
    endpoint = f"{PB_URL}/api/collections/reports/records"
    headers = {"Authorization": auth_store["token"]} if auth_store["token"] else {}
    data = {"location": location_text, "description": desc_text, "user_id": auth_store["user_id"] or ""}
    files = None
    file_obj = None
    if photo_path and os.path.exists(photo_path):
        filename = os.path.basename(photo_path)
        mime_type, _ = mimetypes.guess_type(photo_path)
        file_obj = open(photo_path, 'rb')
        files = {'site_photo': (filename, file_obj, mime_type or 'image/jpeg')}
    try:
        response = requests.post(endpoint, data=data, files=files, headers=headers, timeout=20)
        return response.status_code == 200
    finally:
        if file_obj: file_obj.close()