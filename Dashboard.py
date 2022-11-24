import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import streamlit as st
import datetime
import calendar
import altair as alt

icon = Image.open("resources/favicon.ico")

st.set_page_config(
    page_title="Dashboard - Carbon Consumption Analytics",
    page_icon=icon,
)

st.markdown("""
<style>
div[data-testid="metric-container"] {
    background-color: #0094d9;
    margin: auto;
    border-radius: 5px;
    padding: 20px;
}
label[data-testid="stMetricLabel"] > div {
    font-size: 100%;
    justify-content: center;
}
div[data-testid="stMetricValue"] > div {
    font-size: 125%;
    justify-content: center;
}

</style>
""", unsafe_allow_html=True)

#### MAIN ####
image = Image.open('resources/logo inalum.png')
st.image(image)

st.title('Carbon Consumption Analytics')
today = datetime.datetime.now()
df = pd.read_excel("data/input2.xlsx")
df.rename(columns={'Date(Monthly)': 'Date'}, inplace=True)

st.markdown("📆 %s, %s %s, %s" % (calendar.day_name[today.weekday()], today.strftime("%b"), today.day, today.year))
st.markdown("## Dashboard ")
metric_col = st.columns(3)

with metric_col[0]:
    st.metric('Latest Anoda', df[df["Date"]==df["Date"].max()].iloc[0]["LotAnoda"])
with metric_col[1]:
    st.metric('Number of Anoda This Year', df[pd.DatetimeIndex(df["Date"]).year==today.year].shape[0])
with metric_col[2]:
    st.metric('Latest Actual NAC', round(df[df["Date"]==df["Date"].max()].iloc[0]["NAC Actual"],2))
st.markdown("###### Select Data Period ")

col1= st.columns(2)

with col1[0]:
    start_date = st.date_input(
        "Start date",
        df["Date"].min().to_pydatetime(),
        min_value=df["Date"].min().to_pydatetime(),
        max_value=today,
    )

with col1[1]:
    end_date = st.date_input(
        "End date",
        today,
        min_value=df["Date"].min().to_pydatetime(),
        max_value=today,
    )

## AVERAGE NAC PLOT ##
st.subheader("Average NAC Trend by Time")
col2 = st.columns(3)
with col2[0]:
    nac_option = st.selectbox("Select NAC data type", ("Actual and Calculation", "Actual", "Calculation"))
filter = (df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)
selected_data = df.loc[filter]

if nac_option == "Actual and Calculation":
    selected_data_nac = selected_data.loc[:, ['Date', 'NAC Actual', 'NAC Calc']]
    selected_data_nac = selected_data_nac.melt('Date', var_name='Type', value_name='NAC')
    ch = alt.Chart(selected_data_nac).mark_line().encode(
        x='Date',
        #y=column_name,
        y=alt.Y('NAC', scale=alt.Scale(domain=[350, 550])),
        color='Type',
        tooltip=[alt.Tooltip('NAC', format=",.2f"), 'Date'],
    ).interactive()
else:
    if nac_option == "Actual":
        column_name = "NAC Actual"
    elif nac_option == "Calculation":
        column_name = "NAC Calc"
    ch = alt.Chart(selected_data).mark_line().encode(
        x='Date',
        # y=column_name,
        y=alt.Y(column_name, scale=alt.Scale(domain=[350, 550])),
        tooltip=[alt.Tooltip(column_name, format=",.2f"), 'Date'],
        ).interactive()

st.altair_chart(ch,use_container_width=True,)


## ANODA TYPE PLOT ##
st.subheader("Anoda Type by Time")

selected_data['Anoda Type'] = selected_data['LotAnoda'].apply(lambda x: x[:3])

options = st.multiselect(
    'Select Anoda Type',
    selected_data['Anoda Type'].unique(),
    ['MGE', 'WGE'])

selected_data_anoda = selected_data[selected_data['Anoda Type'].isin(options)]


st.altair_chart(
    alt.Chart(selected_data_anoda).mark_bar().encode(
        x='Date',
        y='count(Anoda Type)',
        color='Anoda Type',
        tooltip=['Anoda Type', 'Date', 'count(Anoda Type)']
    ).interactive(),use_container_width=True,)


col3 = st.columns(3)

# ## CPC HS Pie Chart
# st.markdown("###### CPC High Sulfur Distribution")
# cpc_hs = selected_data['CPC HS'].value_counts().rename_axis('CPC HS').reset_index(name='Counts')
# start_row = 6
# cpc_hs.iloc[start_row] = cpc_hs.iloc[start_row:].sum()
# cpc_hs = cpc_hs.iloc[:start_row + 1]
# # cpc_hs.iloc[-1,0] = "Others"
# sum_cpc_hs=cpc_hs["Counts"].sum()
# cpc_hs["Percentage"] = cpc_hs["Counts"].apply(lambda x: round((x/sum_cpc_hs)*100,2))

# st.altair_chart(
#     alt.Chart(cpc_hs).mark_arc().encode(
#     theta=alt.Theta(field="Percentage", type="quantitative"),
#     color=alt.Color(field="CPC HS", type="nominal"),
#     tooltip=['CPC HS', 'Counts', 'Percentage']
# ), use_container_width=True, )


# ## CPC LS Pie Chart
# st.markdown("###### CPC Low Sulfur Distribution")
# cpc_ls = selected_data['CPC LS'].value_counts().rename_axis('CPC LS').reset_index(name='Counts')
# start_row = 2
# cpc_ls.iloc[start_row] = cpc_ls.iloc[start_row:].sum()
# cpc_ls = cpc_ls.iloc[:start_row + 1]
# # cpc_ls.iloc[-1,0] = "Others"
# sum_cpc_ls = cpc_ls["Counts"].sum()
# cpc_ls["Percentage"] = cpc_ls["Counts"].apply(lambda x: round((x/sum_cpc_ls)*100,2))

# st.altair_chart(
#     alt.Chart(cpc_ls).mark_arc().encode(
#     theta=alt.Theta(field="Percentage", type="quantitative"),
#     color=alt.Color(field="CPC LS", type="nominal"),
#     tooltip=['CPC LS', 'Counts', 'Percentage']
# ), use_container_width=True, )

# ## CTP Pie Chart

# st.markdown("###### CTP Distribution")
# ctp = selected_data['CTP'].value_counts().rename_axis('CTP').reset_index(name='Counts')
# start_row = 6
# ctp.iloc[start_row] = ctp.iloc[start_row:].sum()
# ctp = ctp.iloc[:start_row + 1]
# # ctp.iloc[-1,0] = "Others"
# sum_ctp = ctp["Counts"].sum()
# ctp["Percentage"] = ctp["Counts"].apply(lambda x: round((x/sum_ctp)*100,2))

# st.altair_chart(
#     alt.Chart(ctp).mark_arc().encode(
#     theta=alt.Theta(field="Percentage", type="quantitative"),
#     color=alt.Color(field="CTP", type="nominal"),
#     tooltip=['CTP', 'Counts', 'Percentage']
# ), use_container_width=True, )