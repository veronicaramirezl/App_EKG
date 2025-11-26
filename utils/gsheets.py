import os
from PIL import Image
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

def get_sheet(sheet_name):
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
    client = gspread.authorize(creds)
    return client.open(sheet_name).sheet1

def append_user_result(sheet_name, user_data):
    try:
        sh = get_sheet(sheet_name)

        row_data = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_data.get("name"),
            user_data.get("dni"),
            user_data.get("sex"),
            user_data.get("country"),
            user_data.get("level"),
            user_data.get("term"),
            user_data.get("university"),
            user_data.get("experience"),
            user_data.get("formal_training"),
            user_data.get("clinical_frequency"),
            user_data.get("score"),         # <--- agregado
            user_data.get("module"),        # <--- agregado
            user_data.get("num_questions")  # <--- agregado
        ]

        sh.append_row(row_data)
        return True

    except Exception as e:
        st.error(f"Error al guardar en Google Sheets: {e}")
        return False

