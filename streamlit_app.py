import streamlit as st
from google_play_scraper import search
import time
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="GP Top 5 + IMAGE Formula", layout="wide")

st.title("📱 Google Play: Визуальный Топ-5")

col1, col2 = st.columns(2)
with col1:
    country = st.text_input("Код страны", value="uz")
with col2:
    pause = st.number_input("Пауза (сек)", value=1.5, min_value=0.5)

keys_area = st.text_area("Список ключей:", height=200)
keywords = [k.strip() for k in keys_area.split('\n') if k.strip()]

# Список для хранения данных
all_results_for_excel = []

if st.button("Собрать данные"):
    for word in keywords:
        st.markdown(f"### Ключ: `{word}`")
        
        try:
            results = search(word, country=country, n_hits=5)
            
            if results is None or not results:
                st.warning(f"Ничего не найдено по запросу '{word}'")
                continue

            cols = st.columns(5)
            for idx, app in enumerate(results):
                pos = idx + 1
                title = app.get('title', 'N/A')
                icon_url = app.get('icon', '')
                
                # Формируем ту самую формулу для Excel
                # Важно: используем двойные кавычки внутри формулы
                image_formula = f'=IMAGE("{icon_url}")' if icon_url else ""

                all_results_for_excel.append({
                    "Ключ": word,
                    "Позиция": pos,
                    "Название": title,
                    "Иконка (IMAGE)": image_formula
                })

                with cols[idx]:
                    if icon_url:
                        st.image(icon_url, width=100)
                    st.caption(f"**{pos}.** {title[:40]}")
            
            st.divider()
            time.sleep(pause)

        except Exception as e:
            st.error(f"Ошибка на ключе '{word}'")

    if all_results_for_excel:
        df = pd.DataFrame(all_results_for_excel)
        
        def to_excel(df):
            output = BytesIO()
            # Используем xlsxwriter, он лучше справляется с формулами в некоторых случаях
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='ASO_Top_5')
                
                # Немного расширим колонки, чтобы формулы влезли
                worksheet = writer.sheets['ASO_Top_5']
                worksheet.set_column('A:A', 25) # Ключ
                worksheet.set_column('C:C', 35) # Название
                worksheet.set_column('D:D', 50) # Формула иконки
                
            return output.getvalue()

        excel_data = to_excel(df)
        st.sidebar.success("Готово!")
        st.sidebar.download_button(
            label="📥 Скачать Excel с формулами",
            data=excel_data,
            file_name=f"gp_aso_{country}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
