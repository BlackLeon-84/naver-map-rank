import os
import requests

# --- 사장님 정보 수정 구간 ---
KEYWORD = "송도아이폰수리"      # 검색할 키워드
TARGET_NAME = "인천송도아이폰수리24시"     # 네이버 지도상의 정확한 업체명
# ---------------------------

def get_rank():
    # 이 코드는 연결 확인용 샘플입니다.
    return f"🚀 순위 체크기 정상 작동 중!\n키워드: {KEYWORD}\n대상: {TARGET_NAME}"

def send_telegram(message):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={'chat_id': chat_id, 'text': message})

if __name__ == "__main__":
    send_telegram(get_rank())
