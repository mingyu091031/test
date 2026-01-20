from iris import ChatContext, Bot
from iris.bot.models import ErrorContext
from bots.gemini import get_gemini
from bots.pyeval import python_eval, real_eval
from bots.stock import create_stock_image
from bots.imagen import get_imagen
from bots.lyrics import get_lyrics, find_lyrics
from bots.replyphoto import reply_photo
from bots.text2image import draw_text
from bots.coin import get_coin_info

from iris.decorators import *
from helper.BanControl import ban_user, unban_user
from iris.kakaolink import IrisLink

from bots.detect_nickname_change import detect_nickname_change
import sys, threading

from bots.mentions import mention_user, mention_new_member, mention_self_and_bot, mention_room_master
from bots.notification import share_notice_command, share_current_notice

iris_url = sys.argv[1]
bot = Bot(iris_url)

@bot.on_event("message")
@is_not_banned
def on_message(chat: ChatContext):
    try:
        match chat.message.command:

            case "!멘션":
                mention_user(chat)
            
            #case "!멘션1":
            #    mention_self_and_bot(chat)
            
            case "!방장":
                mention_room_master(chat)
            
            case "!공지":
                share_notice_command(chat)
            
            case "!현재공지":
                share_current_notice(chat)

    except Exception as e :
        print(e)

@bot.on_event("message")
def on_message(chat: ChatContext):
    if chat.message.command == "!test":
        print("테스트 시작...")
        try:
            #chat.reply("동영상 전송 테스트")
            # 간단한 이미지 테스트
            #chat.reply_video("1.mp4")
            #chat.reply_media(["sample3.m4a"])
            chat.reply_media(["test.mp3"])
        except Exception as e:
            print(f"오류: {e}")
            import traceback
            traceback.print_exc()

# 입장 멘션을 보낼 방 리스트
WELCOME_ROOMS = [18472312239224835,18469145050793422]

#입장감지
@bot.on_event("new_member")
def on_newmem(chat: ChatContext):
    if chat.room.id in WELCOME_ROOMS:
        mention_new_member(chat)
    #chat.reply(f"Hello {chat.sender.name}")

#퇴장감지
@bot.on_event("del_member")
def on_delmem(chat: ChatContext):
    if chat.room.id in WELCOME_ROOMS:
        mention_new_member(chat)
    #chat.reply(f"Bye {chat.sender.name}")


@bot.on_event("error")
def on_error(err: ErrorContext):
    print(err.event, "이벤트에서 오류가 발생했습니다", err.exception)
    #sys.stdout.flush()

if __name__ == "__main__":
    #닉네임감지를 사용하지 않는 경우 주석처리
    nickname_detect_thread = threading.Thread(target=detect_nickname_change, args=(bot.iris_url,))
    nickname_detect_thread.start()
    #카카오링크를 사용하지 않는 경우 주석처리
    kl = IrisLink(bot.iris_url)
    bot.run()
