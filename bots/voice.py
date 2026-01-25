import requests
import json
from iris import ChatContext
from iris.decorators import *
import os

TALK_API_URL = os.getenv("TALK_API_URL") or "https://talk-api.naijun.dev/api/v1/send"

def get_auth_from_iris(iris_endpoint: str):
    """Iris에서 AOT 토큰 정보를 가져옵니다."""
    try:
        print(f"[DEBUG] Iris endpoint: {iris_endpoint}")
        aot_url = f"{iris_endpoint}/aot"
        print(f"[DEBUG] Requesting AOT from: {aot_url}")
        
        response = requests.get(aot_url)
        print(f"[DEBUG] AOT response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[DEBUG] AOT data received: {data}")
            
            if data.get("success"):
                aot_data = data.get("aot", {})
                access_token = aot_data.get("access_token")
                device_uuid = aot_data.get("d_id")
                
                if not access_token or not device_uuid:
                    print(f"[ERROR] Missing access_token or d_id")
                    return None
                
                auth = f"{access_token}-{device_uuid}"
                print(f"[DEBUG] Auth header created: {auth[:30]}...{auth[-20:]}")
                return auth
        return None
    except Exception as e:
        print(f"[ERROR] Error getting auth from Iris: {e}")
        import traceback
        traceback.print_exc()
        return None

def send_voice_message(chat: ChatContext):
    """음성 메시지를 전송합니다."""
    try:
        print(f"[DEBUG] send_voice_message called")
        
        if not TALK_API_URL:
            print("[ERROR] TALK_API_URL is not set")
            chat.reply("TALK_API_URL이 설정되지 않았습니다.")
            return False
        
        # Iris에서 인증 정보 가져오기
        auth_header = get_auth_from_iris(chat.api.iris_endpoint)
        
        if not auth_header:
            print("[ERROR] Failed to get auth header")
            chat.reply("인증 정보를 가져올 수 없습니다.")
            return False
        
        # 음성 메시지 attachment 구성
        attachment_obj = {
            "url": "https://talk.kakaocdn.net/dna/c8YtY0/hEGMGiqsDM/CJxEQJK4HIVp63EvKtlmJf/talka_aac.m4a?credential=zf3biCPbmWRjbqf40YGePFLewdou7TIK&expires=1770207014&signature=OIj6bxJAMcAtNCJfJPxXK7uIROs%3D",
            "d": 1000,
            "k": "c8YtY0/hEGMGiqsDM/Jh1HzVQdu1NQhApB7fySDK/talka_aac.m4a",
            "s": 3633,
            "expire": 1770207014187
        }
        
        # TalkApi로 메시지 전송
        payload = {
            "chatId": chat.room.id,
            "type": 18,  # 음성 메시지 타입
            "message": "",
            "attachment": attachment_obj
        }
        
        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/json"
        }
        
        print(f"[DEBUG] Payload: {json.dumps(payload, ensure_ascii=False)}")
        
        response = requests.post(TALK_API_URL, json=payload, headers=headers)
        
        print(f"[DEBUG] Response status: {response.status_code}")
        print(f"[DEBUG] Response body: {response.text}")
        
        if response.status_code == 200:
            print("[SUCCESS] Voice message sent successfully")
            chat.reply("✅ 음성 메시지 전송 완료")
            return True
        else:
            print(f"[ERROR] Failed to send message: {response.status_code}")
            chat.reply(f"❌ 음성 메시지 전송 실패: {response.status_code}")
            return False
            
    except Exception as e:
        import traceback
        print(f"[ERROR] Exception in send_voice_message: {e}")
        traceback.print_exc()
        chat.reply("음성 메시지 전송 중 오류가 발생했습니다.")
        return False

def test_voice(chat: ChatContext):
    """!음성 명령어 - 테스트 음성 메시지를 전송합니다."""
    send_voice_message(chat)