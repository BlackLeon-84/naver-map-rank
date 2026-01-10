import os
import requests
import re
from datetime import datetime
import pytz

# --- 사장님 정보 수정 구간 (여기를 수정하세요) ---
# [ ["키워드", "찾을매장명"], ["키워드", "찾을매장명"] ] 형식입니다.
CHECK_LIST = [
    ["송도아이폰수리", "인천송도아이폰수리24시"], 
    ["마곡아이폰수리", "마곡 아이폰수리 24시 센터"]
]
# -------------------------------------------

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
        
        # 특정 매장 이름이 목록에 있는지 확인
        if target_name in unique_stores:
            return unique_stores.index(target_name) + 1
        return 999
    except:
        return None

def send_telegram(message):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={'chat_id': chat_id, 'text': message})

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
                    k, v = line.strip().split(":")
                    history_data[k] = int(v)

    final_messages = []
    new_history = []

    # 설정한 리스트를 하나씩 돌면서 체크합니다.
    for keyword, target_name in CHECK_LIST:
        current_rank = get_place_rank(keyword, target_name)
        
        # 이전 기록을 찾을 때 키워드를 기준으로 찾습니다.
        last_rank = history_data.get(keyword, 999)
        
        if current_rank is None: continue
        
        is_changed = current_rank != last_rank
        # 10시, 20시는 무조건 / 그 외 시간은 변동 시에만 알림
        need_alert = (current_hour == 14 or current_hour == 20) or is_changed

        if need_alert:
            rank_text = f"{current_rank}위" if current_rank != 999 else "권외"
            if is_changed:
                icon = "📈" if current_rank < last_rank else "📉"
                msg = f"📍 [{keyword}]\n업체: {target_name}\n순위: {last_rank}위 -> {rank_text} {icon}"
            else:
                msg = f"📍 [{keyword}]\n업체: {target_name}\n순위: {rank_text} (변동없음)"
            final_messages.append(msg)
        
        new_history.append(f"{keyword}:{current_rank}")

    if final_messages:
        header = f"⏰ {current_hour}시 순위 리포트\n"
        send_telegram(header + "\n\n".join(final_messages))

    with open(history_file, "w", encoding="utf-8") as f:
        f.write("\n".join(new_history))
