import streamlit as st
import pandas as pd 

st.set_page_config('Personal Finance', page_icon=':moneybag:')


st.markdown("""
    # WELCOME!

    ## YOUR FINANCIAL APP!
    I hope you enjoy our financial organization solution.
""")


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



        