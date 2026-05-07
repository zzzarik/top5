import streamlit as st
from google_play_scraper import search
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from io import BytesIO
import re

st.set_page_config(page_title="GP ASO Hybrid", layout="wide")

st.title("📱 Google Play: Умный Топ-5")
st.caption("Использует API, а при автоисправлении переключается на прямой парсинг.")

with st.sidebar:
    country = st.text_input("Страна (код)", value="uz")
    pause = st.number_input("Пауза (сек)", value=2.0, min_value=1.0)

keys_area = st.text_area("Список ключей:")
keywords = [k.strip() for k in keys_area.split('\n') if k.strip()]

all_data = []

def get_via_soup(word, gl):
    """Запасной метод: парсинг HTML страницы"""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}
    url = f"https://play.google.com/store/search?q={word}&c=apps&gl={gl}"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200: return []
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Находим блоки приложений по характерному классу иконки/контейнера
        items = soup.find_all('div', {'class': re.compile('ULeU3b')})[:5]
        results = []
        for item in items:
            title = item.find('span', {'class': re.compile('Dd9n3b')}).text
            img = item.find('img')
            icon = img['src'] if img else ""
            if icon.startswith('//'): icon = 'https:' + icon
            results.append({"title": title, "icon": icon})
        return results
    except:
        return []

if st.button("🚀 Начать сбор"):
    for word in keywords:
        st.markdown(f"### Ключ: `{word}`")
        results = []
        method_used = "API"

        try:
            # Шаг 1: Пробуем через быструю библиотеку
            results_raw = search(word, country=country, n_hits=5)
            
            if results_raw is not None and len(results_raw) > 0:
                for r in results_raw:
                    results.append({"title": r.get('title'), "icon": r.get('icon')})
            else:
                # Шаг 2: Если API вернул None (автоисправление), включаем Soup
                method_used = "Soup (Автоисправление)"
                results = get_via_soup(word, country)

            if results:
                st.info(f"Метод: {method_used}")
                cols = st.columns(5)
                for idx, app in enumerate(results):
                    name = app['title']
                    icon = app['icon']
                    all_data.append({
                        "Ключ": word,
                        "Метод": method_used,
                        "Позиция": idx + 1,
                        "Название": name,
                        "Иконка": f'=IMAGE("{icon}")'
                    })
                    with cols[idx]:
                        if icon: st.image(icon, width=100)
                        st.caption(f"**{idx+1}.** {name[:40]}")
            else:
                st.warning(f"Не удалось получить данные по `{word}` даже через парсинг.")

            st.divider()
            time.sleep(pause)

        except Exception as e:
            st.error(f"Ошибка на ключе {word}: {e}")

    if all_data:
        df = pd.DataFrame(all_data)
        def to_excel(df_in):
            out = BytesIO()
            with pd.ExcelWriter(out, engine='xlsxwriter') as writer:
                df_in.to_excel(writer, index=False)
            return out.getvalue()
        st.download_button("📥 Скачать Excel", to_excel(df), "gp_hybrid_report.xlsx")
