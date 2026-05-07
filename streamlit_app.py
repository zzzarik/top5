import streamlit as st
from google_play_scraper import search
import time

st.set_page_config(page_title="GP Top 5 Parser", layout="wide")

st.title("📱 Google Play: Top 5 по ключам")

# --- Настройки ---
col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
with col_cfg1:
    country = st.text_input("Страна (код)", value="uz")
with col_cfg2:
    lang = st.text_input("Язык (код)", value="ru")
with col_cfg3:
    pause = st.number_input("Пауза (сек)", value=1.5)

# --- Ввод ключей ---
keys_area = st.text_area("Вставь список ключей:")
keywords = [k.strip() for k in keys_area.split('\n') if k.strip()]

if st.button("Собрать Топ-5"):
    for word in keywords:
        st.subheader(f"Ключ: {word}")

        try:
            # Ищем топ-5
            results = search(word, lang=lang, country=country, n_hits=5)

            if not results:
                st.write("Ничего не найдено")
                continue

            # Выводим в ряд
            cols = st.columns(5)
            for idx, app in enumerate(results):
                with cols[idx]:
                    # Выводим иконку
                    st.image(app['icon'], width=100)
                    # Выводим название (обрезаем, чтобы было красиво)
                    name = app['title'][:30] + "..." if len(app['title']) > 30 else app['title']
                    st.caption(f"**{idx+1}. {name}**")

            st.divider()
            time.sleep(pause) # Пауза безопасности

        except Exception as e:
            st.error(f"Ошибка на ключе '{word}': {e}")