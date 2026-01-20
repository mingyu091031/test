import requests
import json
from iris import ChatContext
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

def send_national_weather(chat: ChatContext):
    """전국 날씨 샵검색 메시지를 전송합니다."""
    try:
        print(f"[DEBUG] send_national_weather called")
        
        if not TALK_API_URL:
            print("[ERROR] TALK_API_URL is not set")
            chat.reply("API URL이 설정되지 않았습니다.")
            return False
        
        # Iris에서 인증 정보 가져오기
        auth_header = get_auth_from_iris(chat.api.iris_endpoint)
        
        if not auth_header:
            print("[ERROR] Failed to get auth header")
            chat.reply("인증 정보를 가져올 수 없습니다.")
            return False
        
        # 샵검색 attachment 구성
        attachment_obj = {
            "P": {
                "TP": "Feed",
                "ME": "샵검색: #전국 오늘 날씨",
                "SID": "sharp",
                "DID": "https://m.search.daum.net/kakao?w=tot&DA=SH1&q=%EC%A0%84%EA%B5%AD%20%EC%98%A4%EB%8A%98%20%EB%82%A0%EC%94%A8&rtmaxcoll=Z8T",
                "L": {
                    "LCA": "",
                    "LCI": "",
                    "LPC": "https://search.daum.net/search?w=tot&DA=SH1&q=%EC%A0%84%EA%B5%AD%20%EC%98%A4%EB%8A%98%20%EB%82%A0%EC%94%A8&rtmaxcoll=Z8T",
                    "LMO": "https://m.search.daum.net/kakao?w=tot&DA=SH1&q=%EC%A0%84%EA%B5%AD%20%EC%98%A4%EB%8A%98%20%EB%82%A0%EC%94%A8&rtmaxcoll=Z8T",
                    "LA": "",
                    "LI": ""
                },
                "VA": "9.5.0",
                "VI": "9.5.0",
                "VM": "2.6.9",
                "VW": "3.0.8",
                "FW": True,
                "RF": "sharp_search",
                "BT": False,
                "PC": True,
                "A": {
                    "version": 2,
                    "code": "JCswX9mNk0SPeeZJrwDvxROTi0+C8RrULxB3Zle8xgM=",
                    "createdAt": 1768944648973
                }
            },
            "C": {
                "THC": 1,
                "THL": [{
                    "TH": {
                        "THU": "https://search1.daumcdn.net/content_search/data/capturemon/spider/z8t/20260121/overall-20260121-f1qLI-kHC3",
                        "W": 800,
                        "H": 800,
                        "LI": False,
                        "PT": 0,
                        "SC": 0
                    },
                    "L": {
                        "LCA": "",
                        "LCI": "",
                        "LPC": "https://search.daum.net/search?w=tot&DA=SH1&q=%EC%A0%84%EA%B5%AD%20%EC%98%A4%EB%8A%98%20%EB%82%A0%EC%94%A8&rtmaxcoll=Z8T",
                        "LMO": "https://m.search.daum.net/kakao?w=tot&DA=SH1&q=%EC%A0%84%EA%B5%AD%20%EC%98%A4%EB%8A%98%20%EB%82%A0%EC%94%A8&rtmaxcoll=Z8T",
                        "LA": "",
                        "LI": ""
                    }
                }],
                "HD": {
                    "TD": {
                        "T": "전국 오늘 날씨",
                        "D": ""
                    },
                    "L": {
                        "LCA": "",
                        "LCI": "",
                        "LPC": "https://search.daum.net/search?w=tot&DA=SH1&q=%EC%A0%84%EA%B5%AD%20%EC%98%A4%EB%8A%98%20%EB%82%A0%EC%94%A8&rtmaxcoll=Z8T",
                        "LMO": "https://m.search.daum.net/kakao?w=tot&DA=SH1&q=%EC%A0%84%EA%B5%AD%20%EC%98%A4%EB%8A%98%20%EB%82%A0%EC%94%A8&rtmaxcoll=Z8T",
                        "LA": "",
                        "LI": ""
                    },
                    "ICO": "https://search1.daumcdn.net/search/statics/img/ki/ico_sharp_search_15x15.png",
                    "TOP": True
                },
                "TI": {
                    "FT": False,
                    "TD": {
                        "T": "전국 오늘 날씨",
                        "D": ""
                    },
                    "L": {
                        "LCA": "",
                        "LCI": "",
                        "LPC": "https://search.daum.net/search?w=tot&DA=SH1&q=%EC%A0%84%EA%B5%AD%20%EC%98%A4%EB%8A%98%20%EB%82%A0%EC%94%A8&rtmaxcoll=Z8T",
                        "LMO": "https://m.search.daum.net/kakao?w=tot&DA=SH1&q=%EC%A0%84%EA%B5%AD%20%EC%98%A4%EB%8A%98%20%EB%82%A0%EC%94%A8&rtmaxcoll=Z8T",
                        "LA": "",
                        "LI": ""
                    },
                    "ST": {}
                },
                "BUL": [{
                    "BU": {
                        "T": "검색 결과 더보기",
                        "TP": "more"
                    },
                    "L": {
                        "LCA": "",
                        "LCI": "",
                        "LPC": "https://search.daum.net/search?w=tot&DA=SH1&q=%EC%A0%84%EA%B5%AD%20%EC%98%A4%EB%8A%98%20%EB%82%A0%EC%94%A8&rtmaxcoll=Z8T",
                        "LMO": "https://m.search.daum.net/kakao?w=tot&DA=SH1&q=%EC%A0%84%EA%B5%AD%20%EC%98%A4%EB%8A%98%20%EB%82%A0%EC%94%A8&rtmaxcoll=Z8T",
                        "LA": "",
                        "LI": ""
                    }
                }]
            }
        }
        
        # TalkApi로 메시지 전송
        # attachment는 JSON 문자열로 전송해야 함
        payload = {
            "chat_id": str(chat.room.id),  # 필드명은 chat_id (스네이크 케이스)
            "type": "71",  # 샵검색 타입 (문자열로 전송)
            "message": "샵검색: #전국 오늘 날씨",
            "attachment": json.dumps(attachment_obj, ensure_ascii=False)
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
            print("[SUCCESS] National weather message sent successfully")
            return True
        else:
            print(f"[ERROR] Failed to send message: {response.status_code}")
            chat.reply(f"날씨 정보 전송 실패: {response.status_code}")
            return False
            
    except Exception as e:
        import traceback
        print(f"[ERROR] Exception in send_national_weather: {e}")
        traceback.print_exc()
        chat.reply("날씨 정보 전송 중 오류가 발생했습니다.")
        return False