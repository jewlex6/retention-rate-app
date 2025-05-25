
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Retention Rate по месяцам")
st.title("📈 Расчёт Retention Rate по месяцам")

uploaded_file = st.file_uploader("Загрузите выгрузку .xlsx", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name=0)

    # Приводим колонку с датой к формату datetime
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date'])

    # Добавляем колонку с годом и месяцем
    df['YearMonth'] = df['Date'].dt.to_period('M')

    # Группируем по клиентам и месяцам
    monthly_visits = df.groupby(['Name', 'YearMonth']).size().reset_index(name='Visits')

    # Создаем сводную таблицу: строки - клиенты, столбцы - месяцы
    pivot = monthly_visits.pivot(index='Name', columns='YearMonth', values='Visits')

    # Сортируем столбцы по времени
    pivot = pivot.sort_index(axis=1)

    # Рассчёт retention rate по каждому месяцу
    retention = {}
    months = pivot.columns
    for i in range(len(months) - 1):
        this_month = pivot[months[i]].notna()
        next_month = pivot[months[i+1]].notna()
        retained = (this_month & next_month).sum()
        total = this_month.sum()
        if total > 0:
            retention[str(months[i])] = round((retained / total) * 100, 1)
        else:
            retention[str(months[i])] = None

    st.subheader("📊 Retention Rate по месяцам")
    retention_df = pd.DataFrame(retention.items(), columns=["Месяц", "Retention Rate (%)"])
    st.dataframe(retention_df)

    st.download_button("📥 Скачать результат в CSV", retention_df.to_csv(index=False).encode('utf-8'), file_name="retention_rate.csv", mime="text/csv")
