import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Кредитный калькулятор", layout="centered")

st.title("💰 Кредитный калькулятор")

# ---- Ввод данных ----
with st.form("credit_form"):
    loan_amount = st.number_input("Сумма кредита", min_value=0.0, value=100000.0)
    interest_rate = st.number_input("Годовая процентная ставка (%)", min_value=0.0, value=10.0)
    loan_term = st.number_input("Срок кредита (месяцы)", min_value=1, value=12)

    payment_type = st.selectbox(
        "Тип платежа",
        ["Аннуитетный", "Дифференциальный"]
    )

    start_date = st.date_input("Дата первого платежа", value=datetime.today())

    submitted = st.form_submit_button("Рассчитать")

# ---- Проверка ввода ----
if submitted:
    if loan_amount <= 0 or interest_rate < 0 or loan_term <= 0:
        st.error("Проверьте корректность введённых данных!")
        st.stop()

    monthly_rate = interest_rate / 100 / 12

    schedule = []

    balance = loan_amount

    # ---- Аннуитетный платеж ----
    if payment_type == "Аннуитетный":
        if monthly_rate == 0:
            monthly_payment = loan_amount / loan_term
        else:
            monthly_payment = loan_amount * (
                monthly_rate * (1 + monthly_rate) ** loan_term
            ) / ((1 + monthly_rate) ** loan_term - 1)

        for i in range(loan_term):
            interest_payment = balance * monthly_rate
            principal_payment = monthly_payment - interest_payment
            end_balance = balance - principal_payment

            payment_date = start_date + relativedelta(months=i)

            schedule.append({
                "Дата": payment_date,
                "Остаток на начало": round(balance, 2),
                "Платёж": round(monthly_payment, 2),
                "Проценты": round(interest_payment, 2),
                "Тело кредита": round(principal_payment, 2),
                "Остаток на конец": round(end_balance, 2)
            })

            balance = end_balance

    # ---- Дифференциальный платеж ----
    else:
        principal_payment = loan_amount / loan_term

        for i in range(loan_term):
            interest_payment = balance * monthly_rate
            monthly_payment = principal_payment + interest_payment
            end_balance = balance - principal_payment

            payment_date = start_date + relativedelta(months=i)

            schedule.append({
                "Дата": payment_date,
                "Остаток на начало": round(balance, 2),
                "Платёж": round(monthly_payment, 2),
                "Проценты": round(interest_payment, 2),
                "Тело кредита": round(principal_payment, 2),
                "Остаток на конец": round(end_balance, 2)
            })

            balance = end_balance

    df = pd.DataFrame(schedule)

    # ---- Вывод ----
    st.subheader("📊 График платежей")

    with st.expander("Показать таблицу"):
        st.dataframe(df)

    st.subheader("📈 Итоги")

    total_payment = df["Платёж"].sum()
    total_interest = df["Проценты"].sum()

    st.write(f"Общая сумма выплат: **{round(total_payment, 2)}**")
    st.write(f"Переплата по процентам: **{round(total_interest, 2)}**")
