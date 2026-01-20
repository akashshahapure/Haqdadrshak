import streamlit as st, os, pandas as pd
from tools.rem_space import rem_space
import warnings
warnings.filterwarnings('ignore')

def csvORexcel(fileObject, file_Name,sheetname=0):
    '''
    This function is defined to read excel or csv file
    based on the file extension
    '''
    
    try:
        if file_Name.split('.')[-1].startswith('c'):
            df = pd.read_csv(fileObject)
        elif file_Name.split('.')[-1].startswith('x'):
            try:
                df = pd.read_excel(fileObject, sheet_name=sheetname, engine='openpyxl',)
            except Exception:
                df = pd.read_excel(fileObject, sheet_name=sheetname, engine='xlrd')
            
        # Cleaning extra spaces from text columns
        df = rem_space(df)
        return df
    
    except FileNotFoundError:
        st.warning("The file name {0} has not found".format(file_Name), icon="⚠️")

def readEmpDB(emp_DB):
    active = [sn for sn in pd.ExcelFile(emp_DB).sheet_names if 'exit' not in sn.lower()][0] # Getting Active employees data sheet name from excel
    Exit = [sn for sn in pd.ExcelFile(emp_DB).sheet_names if 'exit' in sn.lower()][0] # Getting Exit employees data sheet name from excel
    active_emp_data = csvORexcel(emp_DB, emp_DB.name, sheetname=active)
    st.success(":primary-background[Active employee Database loaded successfully!]", icon="✅")
    exit_emp_DB = csvORexcel(emp_DB, emp_DB.name, sheetname=Exit)
    st.success(":primary-background[Exit employee Database loaded successfully!]", icon="✅")

    active_emp_DB = active_emp_data[~(active_emp_data['Full Name'].str.contains(' NGO', case=False, na=False, regex=False))].copy()

    return active_emp_DB, exit_emp_DB