
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Retention / Churn Rate Анализ")
st.title("📈 Анализ Retention и Churn Rate")

# Выбор типа метрики
metric_type = st.selectbox("Что вы хотите проанализировать?", ["Retention Rate", "Churn Rate"])

# Загрузка файла
uploaded_file = st.file_uploader("Загрузите выгрузку .xlsx", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name=0)

    # Поиск подходящих колонок с датой и именем клиента
    date_col = next((col for col in df.columns if "date" in col.lower()), None)
    name_col = next((col for col in df.columns if "name" in col.lower()), None)

    if date_col is None or name_col is None:
        st.error("Файл должен содержать столбцы с датой (Date) и именем клиента (Name)")
    else:
        df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, errors='coerce')
        df = df.dropna(subset=[date_col])
        df['YearMonth'] = df[date_col].dt.to_period('M')

        # Фильтрация по периоду
        min_date = df[date_col].min()
        max_date = df[date_col].max()
        start_date = st.date_input("Начальная дата", min_value=min_date.date(), value=min_date.date())
        end_date = st.date_input("Конечная дата", min_value=min_date.date(), max_value=max_date.date(), value=max_date.date())

        filtered_df = df[(df[date_col] >= pd.to_datetime(start_date)) & (df[date_col] <= pd.to_datetime(end_date))]

        # Группируем по клиентам и месяцам
        monthly_visits = filtered_df.groupby([name_col, 'YearMonth']).size().reset_index(name='Visits')
        pivot = monthly_visits.pivot(index=name_col, columns='YearMonth', values='Visits')
        pivot = pivot.sort_index(axis=1)

        result = {}
        months = pivot.columns

        for i in range(len(months) - 1):
            this_month = pivot[months[i]].notna()
            next_month = pivot[months[i+1]].notna()
            total = this_month.sum()
            if total == 0:
                continue

            if metric_type == "Retention Rate":
                retained = (this_month & next_month).sum()
                value = round((retained / total) * 100, 1)
            else:
                churned = (this_month & ~next_month).sum()
                value = round((churned / total) * 100, 1)

            result[str(months[i])] = value

        result_df = pd.DataFrame(result.items(), columns=["Месяц", f"{metric_type} (%)"])

        # Сортировка
        if st.checkbox("Сортировать от большего к меньшему"):
            result_df = result_df.sort_values(by=result_df.columns[1], ascending=False)

        st.subheader(f"📊 {metric_type} по месяцам")
        st.dataframe(result_df)

        st.download_button("📥 Скачать результат в CSV", result_df.to_csv(index=False).encode('utf-8'), file_name="rate_result.csv", mime="text/csv")
