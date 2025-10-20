import streamlit as st
import pandas as pd 
import requests
import datetime

@st.cache_data(ttl="1day")
def get_selic():
    url = "https://bcb.gov.br/api/servico/sitebcb/historicotaxasjuros"
    resp = requests.get(url)
    df = pd.DataFrame(resp.json()["conteudo"])
    df["DataInicioVigencia"] = pd.to_datetime(df["DataInicioVigencia"]).dt.date
    df["DataFimVigencia"] = pd.to_datetime(df["DataFimVigencia"]).dt.date
    df["DataFimVigencia"] = df["DataFimVigencia"].fillna(datetime.datetime.today().date())
    return df


def calc_general_stats(df):
    df_date = df.groupby(by="Date")[["Amount"]].sum()
    df_date["lag_1"] = df_date["Amount"].shift(1)
    df_date["Monthly_difference [$]"] = df_date["Amount"]-df_date["lag_1"]
    df_date["6M Moving Average Monthly Difference [$]"] = df_date["Monthly_difference [$]"].rolling(6).mean()
    df_date["12M Moving Average Monthly Difference [$]"] = df_date["Monthly_difference [$]"].rolling(12).mean()
    df_date["24M Moving Average Monthly Difference [$]"] = df_date["Monthly_difference [$]"].rolling(24).mean()
    df_date["Monthly_difference [%]"] = df_date["Amount"] / df_date["lag_1"] - 1 
    df_date["6M Total Growth [$]"] = df_date["Amount"].rolling(6).apply(lambda x: x[-1] - x[0])
    df_date["12M Total Growth [$]"] = df_date["Amount"].rolling(12).apply(lambda x: x[-1] - x[0])
    df_date["24M Total Growth [$]"] = df_date["Amount"].rolling(24).apply(lambda x: x[-1] - x[0])
    df_date["6M Total Growth [%]"] = df_date["Amount"].rolling(6).apply(lambda x: x[-1] / x[0] - 1)
    df_date["12M Total Growth [%]"] = df_date["Amount"].rolling(12).apply(lambda x: x[-1] / x[0]- 1)
    df_date["24M Total Growth [%]"] = df_date["Amount"].rolling(24).apply(lambda x: x[-1] / x[0]- 1)

    df_date = df_date.drop("lag_1", axis=1)

    return df_date


def main_goals():
    col1, col2 = st.columns(2)

    goal_start_date = col1.date_input("Goal start date", max_value=df_stats.index.max())
    data_filtrada = df_stats.index[df_stats.index <= goal_start_date][-1]

    custos_fixos = col1.number_input("Fixed costs", min_value=0., format="%.2f")
    salario_bruto = col2.number_input("Gross salary", min_value=0., format="%.2f")
    salario_liq = col2.number_input("Net salary", min_value=0., format="%.2f")

    start_value = df_stats.loc[data_filtrada]["Amount"]
    col1.markdown(f"**Net worth at the start of the goal**: $ {start_value:.2f}")

    selic_gov = get_selic()
    filter_selic_date = (selic_gov["DataInicioVigencia"] < goal_start_date) & (selic_gov["DataFimVigencia"] > goal_start_date)
    selic_default = selic_gov[filter_selic_date]["MetaSelic"].iloc[0]
                
    selic = st.number_input("Selic (Brazilian interest rates)", min_value=0., value=selic_default, format="%.2f")
    selic_ano = selic/100
    selic_mes = (selic_ano + 1) ** (1/12) - 1
                
    # st.text(f"Annual selic rate: {100*selic_ano:.2f}%")
    # st.text(f"Monthly selic rate: {100*selic_mes:.2f}%")
                
    annual_return = start_value * selic_ano
    monthly_return = start_value * selic_mes

    col1_pot, col2_pot = st.columns(2)
    month = (salario_liq - custos_fixos) + monthly_return
    year = 12 * (salario_liq - custos_fixos) + annual_return

    with col1_pot.container(border=True):
        st.markdown(f"""**Monthly potential revenue**: \n\n $ {month:.2f}""",
                    help = f"{salario_liq:.2f} + (-{custos_fixos:.2f}) + {monthly_return:.2f}")

    with col2_pot.container(border=True):
        st.markdown(f"""**Year potential revenue**: \n\n $ {year:.2f}""",
                    help = f"12*({salario_liq:.2f} + (-{custos_fixos:.2f})) + {annual_return:.2f}")

                
    with st.container(border=True):
        col1_goal, col2_goal = st.columns(2)
        with col1_goal:
            set_goal = st.number_input("Set goal", min_value=0., format="%.2f", value=year)

        with col2_goal: 
            finally_net = set_goal + start_value
            st.markdown(f"Estimated net worth after goal:\n\n $ {finally_net:.2f}")

    return goal_start_date, start_value, set_goal, finally_net    
                
st.set_page_config('MoneyDesk', page_icon=':moneybag:')


st.markdown(
    """
    <div style="text-align:center; padding: 40px 20px;">
        <h1 style="color:#1E90FF; font-size:42px; margin-bottom:10px;">
            💰 Welcome to <span style="color:#2E8B57;">MoneyDesk</span>
        </h1>
        <h3 style="color:#555; font-weight:400; margin-bottom:25px;">
            Take control of your money with clarity, confidence, and data-driven insights.
        </h3>
        <p style="color:#666; font-size:17px; max-width:700px; margin:auto;">
            Track your income and expenses, monitor your goals, and visualize how your wealth evolves over time. 
            MoneyDesk helps you make smarter financial decisions - so your money starts working for you.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


file_upload = st.file_uploader(label="Upload your data", type=['csv'])
if file_upload:
    df = pd.read_csv(file_upload)
    df["Date"] = pd.to_datetime(df["Date"],format="%d/%m/%Y").dt.date

    exp1 = st.expander("Raw Data")
    columns_fmt = {"Amount":st.column_config.NumberColumn("Amount", format="$ %f")}
    exp1.dataframe(df, hide_index=True, column_config=columns_fmt)

    exp2 = st.expander("Institutions")
    df_institution = df.pivot_table(index = 'Date', columns='Institution', values='Amount')

    tab_data, tab_history, tab_share = exp2.tabs(["Data", "History", "Distribution"])

    tab_data.dataframe(df_institution)

    with tab_history:
        st.line_chart(df_institution)

    with tab_share:

        date = st.selectbox("Date Filter", options=df_institution.index)

        st.bar_chart(df_institution.loc[date])

    exp3 = st.expander("General Statistics")
    df_stats = calc_general_stats(df)

    columns_config = {
        "Amount": st.column_config.NumberColumn("Amount", format="$ %.2f"),
        "Monthly_difference [$]": st.column_config.NumberColumn("Monthly_difference [$]", format="$ %.2f"),
        "6M Moving Average Monthly Difference [$]": st.column_config.NumberColumn("6M Moving Average Monthly Difference [$]", format="$ %.2f"),
        "12M Moving Average Monthly Difference [$]": st.column_config.NumberColumn("12M Moving Average Monthly Difference [$]", format="$ %.2f"),
        "24M Moving Average Monthly Difference [$]": st.column_config.NumberColumn("24M Moving Average Monthly Difference [$]", format="$ %.2f"),
        "Monthly_difference [%]": st.column_config.NumberColumn("Monthly_difference [%]", format="percent"),
        "6M Total Growth [$]": st.column_config.NumberColumn("6M Total Growth [$]", format="$ %.2f"),
        "12M Total Growth [$]": st.column_config.NumberColumn("12M Total Growth [$]", format="$ %.2f"),
        "24M Total Growth [$]": st.column_config.NumberColumn("24M Total Growth [$]", format="$ %.2f"),
        "6M Total Growth [%]": st.column_config.NumberColumn("6M Total Growth [%]", format="percent"),
        "12M Total Growth [%]": st.column_config.NumberColumn("12M Total Growth [%]", format="percent"),
        "24M Total Growth [%]": st.column_config.NumberColumn("24M Total Growth [%]", format="percent"),
    }

    tab_stats, tab_abs, tab_rel = exp3.tabs(tabs=["Data", "Evolution History", "Relative Growth"])

    with tab_stats:
        exp3.dataframe(df_stats, column_config=columns_config)

    with tab_abs:
        abs_cols = [
            "Monthly_difference [$]", 
            "6M Moving Average Monthly Difference [$]",
            "12M Moving Average Monthly Difference [$]", 
            "24M Moving Average Monthly Difference [$]" ,
        ]
        st.line_chart(df_stats[abs_cols])

    with tab_rel:
        rel_cols = [
            "Monthly_difference [%]",
            "6M Total Growth [%]",
            "12M Total Growth [%]",
            "24M Total Growth [%]",
        ]
        st.line_chart(data=df_stats[rel_cols])

    with st.expander("Goals"):

        tab_main, tab_data_goal, tab_graph = st.tabs(tabs=["Settings", "Data", "Charts"])

        with tab_main:
            goal_start_date, start_value, set_goal, finally_net = main_goals()
        
        with tab_data_goal:
            meses = pd.DataFrame({
                "Reference date":[(goal_start_date + pd.DateOffset(months=i)) for i in range(1,13)],
                "Monthly Goal": [start_value + round(set_goal/12,2) * i for i in range(1,13)],
                #"Expected achievement": [start_value + round(set_goal/12,2) * i for i in range(1,13)],           
                })
        
        meses["Reference date"] = meses["Reference date"].dt.strftime("%Y-%m")
        df_patrimonio = df_stats.reset_index()[["Date","Amount"]]
        df_patrimonio["Reference date"] = pd.to_datetime(df_patrimonio["Date"]).dt.strftime("%Y-%m")
        meses = meses.merge(df_patrimonio, how="left", on="Reference date")

        meses = meses[["Reference date", "Monthly Goal", "Amount"]]
        meses["Monthly goal achievement [%]"] = meses["Amount"] / meses["Monthly Goal"]
        meses["Year goal achievement [%]"] = meses["Amount"] / finally_net
        meses["Expected achievement"] = meses["Monthly Goal"] / finally_net
        meses = meses.set_index("Reference date")

        columns_config_meses = {
        "Monthly Goal": st.column_config.NumberColumn("Monthly Goal", format="$ %.2f"),
        "Amount": st.column_config.NumberColumn("Achieved amount", format="$ %.2f"),
        "Monthly goal achievement [%]": st.column_config.NumberColumn("Monthly goal achievement [%]", format="percent"),
        "Year goal achievement [%]": st.column_config.NumberColumn("Year goal achievement [%]", format="percent"),
        "Expected achievement": st.column_config.NumberColumn("Expected achievement", format="percent"),
    }

        st.dataframe(meses, column_config=columns_config_meses)

    with tab_graph:
        st.line_chart(meses[["Year goal achievement [%]", "Expected achievement"]])