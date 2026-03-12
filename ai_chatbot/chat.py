import os
import json
import requests
from dotenv import load_dotenv
from ai_chatbot.models import ChatHistory
from celery import shared_task # type: ignore
from django.contrib.auth import get_user_model # type: ignore
User = get_user_model() # type: ignore

load_dotenv()

@shared_task
def let_chat(request_data, user_id):
    user = User.objects.get(id=user_id)

    url = os.getenv("BASE_URL_CHAT") + "/chat"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {
        "message": request_data
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=1200)
        response.raise_for_status()

        response_json = response.json()
        payload = response_json.get("data", {})
        recipe = payload.get("recipe")

        if payload.get("flag"):
            flag = payload["flag"]
        elif recipe:
            flag = "list_generated"
        else:
            flag = "normal_response"

        response_payload = recipe if recipe is not None else payload

        chat = ChatHistory.objects.create(
            user=user,
            request_data=request_data,
            response_data=response_payload,
            flag=flag,
        )

        return {"flag": flag, "response": response_payload, "chat_id": chat.id}

    except requests.exceptions.RequestException as e:
        chat = ChatHistory.objects.create(
            user=user,
            request_data=request_data,
            response_data={"error": str(e)},
            flag="error",
        )
        return {"error": str(e), "flag": "error", "chat_id": chat.id}







