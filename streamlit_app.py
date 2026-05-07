import streamlit as st
from google_play_scraper import search
import time

st.set_page_config(page_title="GP Top 5", layout="wide")

st.title("📱 Google Play: Визуальный Топ-5")

# Только страна и пауза
col1, col2 = st.columns(2)
with col1:
    country = st.text_input("Код страны (например: uz или ae)", value="uz")
with col2:
    pause = st.number_input("Пауза безопасности (сек)", value=1.5, min_value=0.5)

# Ввод ключей
keys_area = st.text_area("Список ключей (каждый с новой строки):", height=200)
keywords = [k.strip() for k in keys_area.split('\n') if k.strip()]

if st.button("Парсить Топ-5"):
    for word in keywords:
        st.markdown(f"### Ключ: `{word}`")
        
        try:
            # Ищем топ-5. Параметр lang ставим 'en' или 'ru' по умолчанию, 
            # на саму выдачу (позиции) это почти не влияет.
            results = search(word, country=country, n_hits=5)
            
            if not results:
                st.write("Ничего не найдено")
            else:
                cols = st.columns(5)
                for idx, app in enumerate(results):
                    with cols[idx]:
                        st.image(app['icon'], width=100)
                        # Выводим название под иконкой
                        st.caption(f"**{idx+1}.** {app['title'][:40]}")
            
            st.divider()
            time.sleep(pause) 

        except Exception as e:
            st.error(f"Ошибка на ключе '{word}': {e}")
