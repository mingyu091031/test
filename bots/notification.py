import requests
import json
from iris import ChatContext
from iris.decorators import *

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
                
                session_info = f"{access_token}-{device_uuid}"
                print(f"[DEBUG] Session info created: {session_info[:30]}...{session_info[-20:]}")
                return session_info
        return None
    except Exception as e:
        print(f"[ERROR] Error getting auth from Iris: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_post_id_from_room(chat: ChatContext):
    """채팅방의 moim_meta에서 post_id를 가져옵니다."""
    try:
        result = chat.api.query(
            query="SELECT moim_meta FROM chat_rooms WHERE id = ?",
            bind=[str(chat.room.id)]
        )

        if result and result[0].get("moim_meta"):
            raw_meta = result[0].get("moim_meta")
            moim_meta = json.loads(raw_meta)

            if isinstance(moim_meta, list) and moim_meta:
                ct_raw = moim_meta[0].get("ct")
                if ct_raw:
                    ct_data = json.loads(ct_raw)
                    post_id = ct_data.get("id")
                    print(f"[DEBUG] Found post_id: {post_id}")
                    return post_id
        
        print(f"[DEBUG] No post_id found in moim_meta")
        return None
    except Exception as e:
        print(f"[ERROR] Error getting post_id from room: {e}")
        import traceback
        traceback.print_exc()
        return None

def share_notice(chat: ChatContext, post_id: str, session_info: str):
    """공지를 공유합니다."""
    try:
        url = f"https://talkmoim-api.kakao.com/posts/{post_id}/share"
        
        headers = {
            "Authorization": session_info,
            "A": "android/25.11.2/ko"
        }
        
        print(f"[DEBUG] Sharing notice - URL: {url}")
        print(f"[DEBUG] Headers: A={headers['A']}")
        
        response = requests.post(url, headers=headers)
        
        print(f"[DEBUG] Share response status: {response.status_code}")
        print(f"[DEBUG] Share response body: {response.text}")
        
        # HTTP 상태 코드 체크
        if response.status_code != 200:
            print(f"[ERROR] HTTP error: {response.status_code}")
            return False, f"HTTP 오류: {response.status_code}"
        
        # 응답 본문의 status 필드 체크
        try:
            result = response.json()
            status = result.get("status")
            
            if status is not None and status < 0:
                error_messages = {
                    -4046: "공지 공유 권한이 없거나 이미 공유된 공지입니다",
                    -401: "인증 오류",
                    -403: "권한 없음",
                    -404: "공지를 찾을 수 없음"
                }
                error_msg = error_messages.get(status, f"알 수 없는 오류 (status: {status})")
                print(f"[ERROR] API error: {error_msg}")
                return False, error_msg
            
            print("[SUCCESS] Notice shared successfully")
            return True, "성공"
            
        except json.JSONDecodeError:
            # JSON 파싱 실패 시에도 HTTP 200이면 성공으로 간주
            print("[SUCCESS] Notice shared (non-JSON response)")
            return True, "성공"
            
    except Exception as e:
        print(f"[ERROR] Exception in share_notice: {e}")
        import traceback
        traceback.print_exc()
        return False, f"예외 발생: {str(e)}"

@has_param
def share_notice_command(chat: ChatContext):
    """!공지 명령어 - post_id를 받아 공지를 공유합니다."""
    try:
        print(f"[DEBUG] share_notice_command called")
        
        # 파라미터로 post_id 받기
        post_id = chat.message.param.strip()
        
        if not post_id:
            chat.reply("사용법: !공지 <post_id>")
            return
        
        print(f"[DEBUG] Post ID from param: {post_id}")
        
        # Iris에서 인증 정보 가져오기
        session_info = get_auth_from_iris(chat.api.iris_endpoint)
        
        if not session_info:
            chat.reply("인증 정보를 가져올 수 없습니다.")
            return
        
        # 공지 공유
        success, message = share_notice(chat, post_id, session_info)
        
        if success:
            chat.reply(f"✅ 공지 공유 완료\npost_id: {post_id}")
        else:
            chat.reply(f"❌ 공지 공유 실패\n사유: {message}")
            
    except Exception as e:
        import traceback
        print(f"[ERROR] Exception in share_notice_command: {e}")
        traceback.print_exc()
        chat.reply("공지 공유 중 오류가 발생했습니다.")

def share_current_notice(chat: ChatContext):
    """!현재공지 명령어 - 현재 방의 공지를 공유합니다."""
    try:
        print(f"[DEBUG] share_current_notice called")
        
        # moim_meta에서 post_id 가져오기
        post_id = get_post_id_from_room(chat)
        
        if not post_id:
            chat.reply("현재 방에 공지가 없거나 post_id를 찾을 수 없습니다.")
            return
        
        print(f"[DEBUG] Current room post_id: {post_id}")
        
        # Iris에서 인증 정보 가져오기
        session_info = get_auth_from_iris(chat.api.iris_endpoint)
        
        if not session_info:
            chat.reply("인증 정보를 가져올 수 없습니다.")
            return
        
        # 공지 공유
        success, message = share_notice(chat, post_id, session_info)
        
        if success:
            chat.reply(f"✅ 현재 방의 공지를 공유했습니다\npost_id: {post_id}")
        else:
            chat.reply(f"❌ 공지 공유 실패\n사유: {message}\npost_id: {post_id}")
            
    except Exception as e:
        import traceback
        print(f"[ERROR] Exception in share_current_notice: {e}")
        traceback.print_exc()
        chat.reply("공지 공유 중 오류가 발생했습니다.")