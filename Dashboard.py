import streamlit as st
from PIL import Image
import pickle
import numpy as np
import pandas as pd
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
import altair_ally as aly
import altair as alt

## Set page icon
icon = Image.open("./resources/favicon.ico")

## Set page title and layout
st.set_page_config(
    page_title="Anode Cost Prediction - Carbon Consumption Analytics",
    page_icon=icon,
    layout='wide',
    initial_sidebar_state='collapsed'
)

# Display Inalum's logo
image = Image.open('resources/logo inalum.png')
st.image(image)

# Set title
st.title('Anode Cost Prediction')

# Load the data
data_prediksi = pd.read_csv("data/prediksi_material_nac.csv", sep=";")

def calculate_price(data):
    cpc_hs_percent = data["cpc_hs_percent"] * (1-data["butt_percent"]) * (1-data["ctp_percent"])
    cpc_ls_percent = data["cpc_ls_percent"] * (1 - data["butt_percent"]) * (1 - data["ctp_percent"])
    total_price = round(((cpc_hs_percent/100) * float(data["cpc_hs_price"]) + (cpc_ls_percent/100) * float(data["cpc_ls_price"]) + (data["ctp_percent"]/100) * float(data["ctp_price"]) + (data["butt_percent"]/100) * float(data["butt_price"]))/1000,2)

    return total_price

def get_carbon(data_prediksi, material_type):
    rro2 = data_prediksi.loc[data_prediksi["Lot"] == material_type, "RRO2"].iloc[0]
    rrco2 = data_prediksi.loc[data_prediksi["Lot"] == material_type, "RRCO2"].iloc[0]
    ap = data_prediksi.loc[data_prediksi["Lot"] == material_type, "AP"].iloc[0]
    tc = data_prediksi.loc[data_prediksi["Lot"] == material_type, "TC"].iloc[0]
    nac = data_prediksi.loc[data_prediksi["Lot"] == material_type, "NAC"].iloc[0]

    return rro2, rrco2, ap, tc, nac

# Create multiple tabs
single_pred_tab, batch_pred_tab = st.tabs(["Single Cost Prediction", "Multiple Cost Prediction"])

###### Tab 1: Single Prediction with Main Variables ######
with single_pred_tab:
    st.markdown("#### Material Source and Price")
    col1 = st.columns(3)

    # Input for the variables
    with col1[0]:
        cpc_hs_option = st.selectbox("Select CPC HS Source", ["A","F", "M", "W"], 3)


    with col1[1]:
        cpc_ls_option = st.selectbox("Select CPC LS Source", ["G", "J", "S"],)


    with col1[2]:
        ctp_option = st.selectbox("Select CTP Source", ["A", "E", "H", "Q"])


    col2 = st.columns(4)

    with col2[0]:
        cpc_hs_price = st.text_input("Input CPC HS price (USD/Ton)", 1000)

    with col2[1]:
        cpc_ls_price = st.text_input("Input CPC LS price (USD/Ton)", 1200)

    with col2[2]:
        ctp_price = st.text_input("Input CTP price (USD/Ton)", 1500)

    with col2[3]:
        butt_price = st.text_input("Input Butt price (USD/Ton)", 178.82)


    st.markdown("#### Material Percentage")
    col3 = st.columns(4)

    with col3[0]:
        cpc_hs_slider = st.slider(
            'CPC HS Percentage',
            0.0, 100.0, 70.0)

    with col3[1]:
        cpc_ls_slider = st.slider(
            'CPC LS Percentage',
            0.0, 100.0, 100.0-cpc_hs_slider)

    with col3[2]:
        ctp_slider = st.slider(
            'CTP Percentage',
            13.0, 16.0, 14.0)

    with col3[3]:
        butt_slider = st.slider(
            'Butt Percentage',
            25.0, 35.0, 30.0)

    material_type = cpc_hs_option+cpc_ls_option+ctp_option

    rro2, rrco2, ap, tc, nac = get_carbon(data_prediksi,material_type)
    st.markdown('#### Carbon Prediction')
    st.text('RRO2: ' + str(rro2) + ' %')
    st.text('RRCO2: ' + str(rrco2) + ' %')
    st.text('AP: ' + str(ap) + ' nPm')
    st.text('TC: ' + str(tc) + ' W/mk')
    st.text('NAC: ' + str(nac) + ' Kg/T.Al')

    # Create dataframe for the features input
    data = {
                'cpc_hs_percent': cpc_hs_slider,
                'cpc_ls_percent': cpc_ls_slider,
                'ctp_percent': ctp_slider,
                'butt_percent': butt_slider,
                'cpc_hs_price': cpc_hs_price,
                'cpc_ls_price': cpc_ls_price,
                'ctp_price': ctp_price,
                'butt_price': butt_price,
                }

    total_price = calculate_price(data)

    st.markdown('#### Calculated Price: '+ str(total_price) +" USD")


###### Tab 2: Batch Prediction ######
with batch_pred_tab:
#@st.cache
    # Function to create an Excel file
    def to_excel(df):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        format1 = workbook.add_format({'num_format': '0.00'})
        worksheet.set_column('A:A', None, format1)
        writer.save()
        processed_data = output.getvalue()
        return processed_data

    # Reading data
    data_template = pd.read_csv("data/cost_prediction_template.csv", sep=";")

    # Upload the excel file
    st.markdown('#### Uploading the material price')
    st.write("Please make sure the uploaded file follows the right template for the material source and price.")

    # Create the template file
    template_file = to_excel(data_template)
    # Button to download the template file
    st.download_button(
        label='📥 Download template file',
        data=template_file,
        file_name='template_cost.xlsx',
    )

    # Input file uploader
    uploaded_file = st.file_uploader("Choose an Excel file")
    # Read the input file
    if uploaded_file is not None:
        df_input = pd.read_excel(uploaded_file)
        st.dataframe(df_input)

    st.markdown("#### Material Percentage")
    col4 = st.columns(4)

    with col4[0]:
        cpc_hs_slider_batch = st.slider(
            'CPC HS Percentage',
            0.0, 100.0, 70.0, key="batch_cpc_hs")

    with col4[1]:
        cpc_ls_slider_batch = st.slider(
            'CPC LS Percentage',
            0.0, 100.0, 100.0-cpc_hs_slider, key="batch_cpc_ls")

    with col4[2]:
        ctp_slider_batch = st.slider(
            'CTP Percentage',
            13.0, 16.0, 14.0, key="batch_ctp")

    with col4[3]:
        butt_slider_batch = st.slider(
            'Butt Percentage',
            25.0, 35.0, 30.0, key="batch_butt")

    # Make prediction when the button is clicked
    if st.button('Analyze'):
        df_cpc_ls = df_input.loc[df_input["Jenis"]=="CPC-LS",:]
        df_cpc_hs = df_input.loc[df_input["Jenis"]=="CPC-HS",:]
        df_ctp = df_input.loc[df_input["Jenis"]=="CTP",:]

        all_prediction = []

        for _, row_cpc_hs in df_cpc_hs.iterrows():
            for _, row_cpc_ls in df_cpc_ls.iterrows():
                for _, row_ctp in df_ctp.iterrows():
                    material_type = row_cpc_hs["Lot"] + row_cpc_ls["Lot"] + row_ctp["Lot"]

                    rro2, rrco2, ap, tc, nac = get_carbon(data_prediksi, material_type)
                    data_batch = {
                        'cpc_hs_percent': cpc_hs_slider_batch,
                        'cpc_ls_percent': cpc_ls_slider_batch,
                        'ctp_percent': ctp_slider_batch,
                        'butt_percent': butt_slider_batch,
                        'cpc_hs_price': row_cpc_hs["Price"],
                        'cpc_ls_price': row_cpc_ls["Price"],
                        'ctp_price': row_ctp["Price"],
                        'butt_price': 178.82,
                    }

                    if not pd.isnull(nac):
                        total_price_batch = calculate_price(data_batch)

                        cpc_hs_type = row_cpc_hs["Lot"] + " - " + row_cpc_hs["Source"]
                        cpc_ls_type = row_cpc_ls["Lot"] + " - " + row_cpc_ls["Source"]
                        ctp_type = row_ctp["Lot"] + " - " + row_cpc_ls["Source"]

                        info = {
                            "CPC HS Source": cpc_hs_type,
                            "CPC LS Source": cpc_ls_type,
                            "CTP Source": ctp_type,
                            "RRO2" : rro2,
                            "RRCO2" : rrco2,
                            "AP" : ap,
                            "TC" : tc,
                            "NAC" : nac,
                            "Predicted Cost" : round(total_price_batch,2),
                            "Ratio NAC/Cost" : round(float(nac)/float(total_price_batch),2),
                        }

                        all_prediction.append(info)

        data_analyzed = pd.DataFrame(all_prediction).sort_values('Ratio Cost/NAC',ascending=False)

        st.markdown("###### A combination of "+cpc_hs_type+", "+cpc_ls_type+", "+ctp_type+" is recommended for the current bidding. Full analysis for all combinations is given below:")
        st.dataframe(data_analyzed)

        # Create Excel file to download
        excel_file = to_excel(data_analyzed)

        # Button to download the prediction data
        st.download_button(
            label='📥 Download data as Excel',
            data=excel_file,
            file_name='Cost Analysis.xlsx',
        )