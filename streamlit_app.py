import streamlit as st
from google_play_scraper import search
import time
import pandas as pd
from io import BytesIO

# Настройка страницы
st.set_page_config(page_title="GP Top 5 Parser", layout="wide")

st.title("📱 Google Play: Топ-5 по ключевым словам")
st.write("Скрипт собирает первые 5 приложений. Если Google делает автоисправление опечатки, может возникнуть ошибка.")

# --- Блок настроек ---
with st.sidebar:
    st.header("⚙️ Настройки")
    country = st.text_input("Код страны (uz, ae, ru, us)", value="uz")
    pause = st.number_input("Пауза безопасности (сек)", value=2.0, min_value=0.5, step=0.5)
    st.info("Увеличьте паузу, если часто лезут ошибки (Google блокирует IP).")

# --- Ввод данных ---
keys_area = st.text_area("Вставьте список ключей (каждый с новой строки):", height=200)
keywords = [k.strip() for k in keys_area.split('\n') if k.strip()]

# Список для накопления данных для Excel
all_results_for_excel = []

if st.button("🚀 Запустить парсинг"):
    if not keywords:
        st.warning("Сначала введите список ключевых слов.")
    else:
        for word in keywords:
            st.markdown(f"### Ключ: `{word}`")
            
            try:
                # Попытка парсинга
                results = search(word, country=country, n_hits=5)
                
                # Если библиотека вернула None (проблема автоисправления или бана)
                if results is None:
                    st.error(f"❌ Ошибка: Google вернул пустой результат. Скорее всего, сработал принудительный редирект на другое слово или временный бан IP.")
                    continue

                if not results:
                    st.warning(f"⚠️ По запросу '{word}' в магазине ничего не найдено.")
                    continue

                # Отображение результатов
                cols = st.columns(5)
                for idx, app in enumerate(results):
                    pos = idx + 1
                    title = app.get('title', 'N/A')
                    icon_url = app.get('icon', '')
                    
                    # Формируем формулу для Excel
                    image_formula = f'=IMAGE("{icon_url}")' if icon_url else ""

                    # Сохраняем в общий список
                    all_results_for_excel.append({
                        "Ключ": word,
                        "Позиция": pos,
                        "Название": title,
                        "Иконка (IMAGE)": image_formula,
                        "App ID": app.get('appId', '')
                    })

                    with cols[idx]:
                        if icon_url:
                            st.image(icon_url, width=100)
                        st.caption(f"**{pos}.** {title[:40]}...")
                
                st.divider()
                time.sleep(pause) # Пауза между ключами

            except Exception as e:
                # Выводим реальный текст ошибки для диагностики
                st.error(f"🔥 Ошибка на ключе '{word}': {str(e)}")
        
        # Финальная кнопка скачивания
        if all_results_for_excel:
            df = pd.DataFrame(all_results_for_excel)
            
            def to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='GP_Top_5')
                    
                    # Настройка колонок в Excel
                    worksheet = writer.sheets['GP_Top_5']
                    worksheet.set_column('A:A', 25) # Ключ
                    worksheet.set_column('C:C', 40) # Название
                    worksheet.set_column('D:D', 60) # Формула иконки
                    worksheet.set_column('E:E', 30) # App ID
                return output.getvalue()

            excel_data = to_excel(df)
            st.success("🎉 Все ключи обработаны!")
            st.download_button(
                label="📥 Скачать результат в Excel",
                data=excel_data,
                file_name=f"gp_top5_{country}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
