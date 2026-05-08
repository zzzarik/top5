import streamlit as st
from google_play_scraper import search
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from io import BytesIO
import re

st.set_page_config(page_title="GP ASO Horizontal", layout="wide")

st.title("📱 GP: Топ-5 в одну строку")

with st.sidebar:
    country = st.text_input("Страна (код)", value="uz")
    pause = st.number_input("Пауза (сек)", value=2.0, min_value=1.0)

keys_area = st.text_area("Список ключей:")
keywords = [k.strip() for k in keys_area.split('\n') if k.strip()]

all_data_for_excel = []

def get_via_soup(word, gl):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}
    url = f"https://play.google.com/store/search?q={word}&c=apps&gl={gl}"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200: return []
        soup = BeautifulSoup(resp.text, 'html.parser')
        items = soup.find_all('div', {'class': re.compile('ULeU3b')})[:5]
        results = []
        for item in items:
            title = item.find('span', {'class': re.compile('Dd9n3b')}).text
            img = item.find('img')
            icon = img['src'] if img else ""
            if icon.startswith('//'): icon = 'https:' + icon
            results.append({"title": title, "icon": icon})
        return results
    except: return []

if st.button("🚀 Начать сбор"):
    for word in keywords:
        st.markdown(f"### Ключ: `{word}`")
        results = []
        
        try:
            # Пробуем API
            raw = search(word, country=country, n_hits=5)
            if raw:
                for r in raw:
                    results.append({"title": r.get('title'), "icon": r.get('icon')})
            else:
                # Если API пусто (автоисправление), берем Soup
                results = get_via_soup(word, country)

            if results:
                # Показываем в интерфейсе
                cols = st.columns(5)
                
                # Подготавливаем строку для Excel
                row = {"Ключевое слово": word}
                
                for idx, app in enumerate(results):
                    name = app['title']
                    icon = app['icon']
                    
                    # Заполняем колонки для Excel (1-5)
                    row[f"Топ {idx+1} (Иконка)"] = f'=IMAGE("{icon}")'
                    row[f"Топ {idx+1} (Название)"] = name
                    
                    with cols[idx]:
                        if icon: st.image(icon, width=100)
                        st.caption(f"**{idx+1}.** {name[:40]}")
                
                all_data_for_excel.append(row)
            else:
                st.warning(f"Данные по `{word}` не найдены")
            
            st.divider()
            time.sleep(pause)

        except Exception as e:
            st.error(f"Ошибка: {e}")

    if all_data_for_excel:
        df = pd.DataFrame(all_data_for_excel)
        
        # Переставляем колонки, чтобы было красиво: Ключ, Иконка1, Название1, Иконка2...
        cols_order = ["Ключевое слово"]
        for i in range(1, 6):
            cols_order.append(f"Топ {i} (Иконка)")
            cols_order.append(f"Топ {i} (Название)")
        
        df = df[cols_order]

        def to_excel(df_in):
            out = BytesIO()
            with pd.ExcelWriter(out, engine='xlsxwriter') as writer:
                df_in.to_excel(writer, index=False)
                # Делаем колонки с формулами пошире
                ws = writer.sheets['Sheet1']
                ws.set_column('A:A', 20)
                for col_idx in range(1, 11): # Остальные колонки
                    ws.set_column(col_idx, col_idx, 30)
            return out.getvalue()
            
        st.download_button("📥 Скачать Excel (Строчный)", to_excel(df), "gp_aso_horizontal.xlsx")
