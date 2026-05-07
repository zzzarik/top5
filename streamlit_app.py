import streamlit as st
from google_play_scraper import search
import time
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="GP ASO Dual Mode", layout="wide")

st.title("📱 GP: Сравнение автоисправления")

with st.sidebar:
    country = st.text_input("Страна", value="uz")
    pause = st.number_input("Пауза (сек)", value=2.0, min_value=1.0)

keys_area = st.text_area("Ключи:")
keywords = [k.strip() for k in keys_area.split('\n') if k.strip()]

all_data = []

if st.button("🚀 Парсить"):
    for word in keywords:
        # 1. Запрос "Как есть" (Google скорее всего исправит опечатку)
        st.subheader(f"🔍 Ключ: {word}")
        
        try:
            # Первый проход: обычный поиск
            res_default = search(word, country=country, n_hits=5)
            
            # Второй проход: точный поиск (в кавычках), чтобы попытаться обойти автозамену
            res_exact = search(f'"{word}"', country=country, n_hits=5)

            # Отрисовка в две строки для сравнения
            for label, results in [("Выдача Google (автоисправление)", res_default), ("Точная выдача (попытка)", res_exact)]:
                st.write(f"**{label}:**")
                if results:
                    cols = st.columns(5)
                    for idx, app in enumerate(results):
                        title = app.get('title', 'N/A')
                        icon = app.get('icon', '')
                        with cols[idx]:
                            if icon: st.image(icon, width=80)
                            st.caption(f"{idx+1}. {title[:30]}")
                        
                        all_data.append({
                            "Ввод": word,
                            "Тип поиска": label,
                            "Позиция": idx + 1,
                            "Название": title,
                            "Иконка": f'=IMAGE("{icon}")'
                        })
                else:
                    st.write("Нет данных")
            
            st.divider()
            time.sleep(pause)

        except Exception as e:
            st.error(f"Ошибка на '{word}': {e}")

    if all_data:
        df = pd.DataFrame(all_data)
        def to_excel(df_in):
            out = BytesIO()
            with pd.ExcelWriter(out, engine='xlsxwriter') as writer:
                df_in.to_excel(writer, index=False)
            return out.getvalue()
        
        st.download_button("📥 Скачать Excel", to_excel(df), "aso_dual_report.xlsx")
