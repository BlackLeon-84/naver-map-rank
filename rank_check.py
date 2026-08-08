import os
import requests
import re
from datetime import datetime
import pytz

# --- 설정 구간 ---
# MY_ID는 기존 TELEGRAM_CHAT_ID를 가져오고, FRIEND_ID는 새로 만드신 FRIEND_CHAT_ID를 가져옵니다.
MY_ID = os.environ.get('TELEGRAM_CHAT_ID')
FRIEND_ID = os.environ.get('FRIEND_CHAT_ID')

CHECK_LIST = [
    ["송도아이폰수리", "인천송도아이폰수리24시", MY_ID, [9, 19]],
    ["마곡아이폰수리", "마곡 아이폰수리 24시 센터", MY_ID, [9, 19]],
    ["강남아이폰수리", "강남아이폰수리24시", FRIEND_ID, [17]]
]
# ----------------

def should_alert(current_rank, last_rank, current_hour, fixed_hours):
    return current_hour in fixed_hours or current_rank != last_rank

def get_place_rank(keyword, target_name):
    url = f"https://m.map.naver.com/search2/search.naver?query={keyword}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/0.4',
        'Referer': 'https://m.map.naver.com/'
    }
    try:
        res = requests.get(url, headers=headers)
        store_names = re.findall(r'"name":"([^"]+)"', res.text)
        unique_stores = []
        for name in store_names:
            if name not in unique_stores: unique_stores.append(name)
        
        if target_name in unique_stores:
            return unique_stores.index(target_name) + 1
        return 999
    except:
        return None

def send_telegram(message, target_chat_id):
    # ID가 설정되지 않았거나 친구 ID를 못 불러올 경우를 대비한 안전장치
    if not target_chat_id:
        print("알림을 보낼 대상의 Chat ID가 없습니다.")
        return
    token = os.environ.get('TELEGRAM_TOKEN')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={'chat_id': target_chat_id, 'text': message})

if __name__ == "__main__":
    korea_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(korea_tz)
    current_hour = now.hour

    history_file = "last_rank.txt"
    history_data = {}
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    parts = line.strip().split(":")
                    if len(parts) == 2:
                        k, v = parts
                        history_data[k] = int(v)

    user_messages = {} 
    new_history = []

    for keyword, target_name, target_chat_id, fixed_hours in CHECK_LIST:
        current_rank = get_place_rank(keyword, target_name)
        last_rank = history_data.get(keyword, 999)
        
        if current_rank is None: continue
        
        is_changed = current_rank != last_rank
        # 설정한 고정 시간이거나, 순위가 변동되었을 때만 알림 발생
        need_alert = should_alert(current_rank, last_rank, current_hour, fixed_hours)

        if need_alert:
            rank_text = f"{current_rank}위" if current_rank != 999 else "권외"
            if is_changed:
                icon = "📈" if current_rank < last_rank else "📉"
                msg = f"📍 [{keyword}]\n업체: {target_name}\n순위: {last_rank}위 -> {rank_text} {icon}"
            else:
                msg = f"📍 [{keyword}]\n업체: {target_name}\n순위: {rank_text} (변동없음)"
            
            # 보낼 사람별로 메시지 분류
            if target_chat_id not in user_messages:
                user_messages[target_chat_id] = []
            user_messages[target_chat_id].append(msg)
        
        new_history.append(f"{keyword}:{current_rank}")

    # 분류된 메시지들을 각각의 주인에게 전송
    for chat_id, msgs in user_messages.items():
        header = f"⏰ {now.strftime('%H:%M')} 순위 리포트\n"
        send_telegram(header + "\n\n".join(msgs), chat_id)

    # 전체 순위 기록 업데이트
    with open(history_file, "w", encoding="utf-8") as f:
        f.write("\n".join(new_history))
