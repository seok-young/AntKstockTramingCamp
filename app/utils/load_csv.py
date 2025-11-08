import pandas as pd
from sqlalchemy import create_engine
import os

from app.core.config import settings

def load_csv_to_dataframe(file_path):
    try:
        df = pd.read_csv(file_path,encoding='cp949')
        return df
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return None