import os
import requests
import re

# --- 사장님 정보 수정 구간 ---
KEYWORD = "송도아이폰수리"      # 검색할 키워드 (원하는 것으로 바꾸세요)
TARGET_NAME = "인천송도아이폰수리24시"     # 네이버 지도에 등록된 정확한 내 업체명
# ---------------------------

def get_place_rank():
    # 네이버 플레이스 모바일 검색 (순위 데이터를 가져오기 위한 주소)
    url = f"https://m.map.naver.com/search2/search.naver?query={KEYWORD}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/0.4',
        'Referer': 'https://m.map.naver.com/'
    }
    
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        
        # 네이버 지도 데이터에서 업체명들을 추출 (정규표현식 사용)
        # 실제 데이터는 자바스크립트 안에 숨어있어 텍스트로 추출합니다.
        store_names = re.findall(r'"name":"([^"]+)"', res.text)
        
        # 중복 제거 및 업체명만 필터링
        unique_stores = []
        for name in store_names:
            if name not in unique_stores:
                unique_stores.append(name)

        # 내 업체가 몇 번째에 있는지 확인
        if TARGET_NAME in unique_stores:
            rank = unique_stores.index(TARGET_NAME) + 1
            return f"📍 [{KEYWORD}] 검색 결과\n'{TARGET_NAME}' 업체는 현재 {rank}위에 있습니다! ✅"
        else:
            return f"📍 [{KEYWORD}] 검색 결과\n'{TARGET_NAME}' 업체를 1페이지(약 20~40위) 내에서 찾을 수 없습니다. 😭"

    except Exception as e:
        return f"❌ 순위 확인 중 오류 발생: {str(e)}"

def send_telegram(message):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={'chat_id': chat_id, 'text': message})

if __name__ == "__main__":
    result = get_place_rank()
    send_telegram(result)
