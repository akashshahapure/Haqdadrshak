import streamlit as st, pandas as pd, numpy as np, xlsxwriter, io, time
from datetime import datetime as dt
import datetime
from tools.read_file import csvORexcel
from tools.read_file import readEmpDB
from tools.transform_data import dataXform
from tools.check_pv import check_pv
from tools.openProjects import open_projects
import warnings
warnings.filterwarnings('ignore')

# Setting page configuration
st.set_page_config(
    page_title="Resource Allocation Report",
    page_icon="https://framerusercontent.com/images/gVBdWe1mOwPpV6Z7x9I2kLuIWs.jpg",
    layout="centered",
)

# Setting up the title of the app
st.markdown("<h1 style='text-align: center;'>Resource Allocation Report Generator</h1>", unsafe_allow_html=True)

# Creating a form structure so that elements would not reload on every interaction.
with st.form(key='file_upload_form'):
    col1, col2, col3, col4 = st.columns([7,8,7,8])
    # Asking user to upload Employee Database file
    emp_DB = col1.file_uploader("**Upload Employee Database (Excel/CSV):**", type=['xlsx','xls','csv'])
    if emp_DB is None:
        col1.warning(":red[Please upload the Employee Database file to proceed.]", icon="⚠️")
    else:
        col1.success(":primary-background[Employee Database file uploaded successfully!]", icon="✅")
    # Asking user to upload Delivery Hierarchy Report
    delivery_hierarchy = col2.file_uploader("**Upload Delivery Hierarchy Report (Excel/CSV):**", type=['xlsx','xls','csv'])
    if delivery_hierarchy is None:
        col2.warning(":red[Please upload the Delivery Hierarchy Report to proceed.]", icon="⚠️")
    else:
        col2.success(":primary-background[Delivery Hierarchy Report uploaded successfully!]", icon="✅")
    # Asking user to upload Project Master Report
    project_master = col3.file_uploader("**Upload Project Master Report (Excel/CSV):**", type=['xlsx','xls','csv'])
    if project_master is None:
        col3.warning(":red[Please upload the Project Master Report to proceed.]", icon="⚠️")
    else:
        col3.success(":primary-background[Project Master Report uploaded successfully!]", icon="✅")
    # Asking user to upload User Allocation History Report
    user_allocation_history = col4.file_uploader("**Upload User Allocation History Report (Excel/CSV):**", type=['xlsx','xls','csv'])
    if user_allocation_history is None:
        col4.warning(":red[Please upload the User Allocation History Report to proceed.]", icon="⚠️")
    else:
        col4.success(":primary-background[User Allocation History Report uploaded successfully!]", icon="✅")

    submitted = st.form_submit_button(label='Generate Resource Allocation Report')

# Logic for submit button.
if submitted:
    # Checking if all files are uploaded
    with st.spinner('Checking if all files are uploaded!'):
        if (emp_DB is None) & (delivery_hierarchy is None) & (project_master is None) & (user_allocation_history is None):
            st.warning(":red[Please upload all the required files to proceed.]", icon="⚠️")
            st.stop()
        else:
            st.success(":primary-background[All files uploaded successfully!]", icon="✅")
    with st.spinner('**Loading Employee Database in "Active" and "Exit" files...**'):
        active_emp_DB, exit_emp_DB = readEmpDB(emp_DB)
    with st.spinner('**Loading Delivery Hierarchy Report...**'):
        del_hie_rep = csvORexcel(delivery_hierarchy, delivery_hierarchy.name)
        st.success(":primary-background[Delivery Hierarchy Report loaded successfully!]", icon="✅")
    with st.spinner('**Loading Project Master Report into Active projects records...**'):
        project_master = csvORexcel(project_master, project_master.name)
        activeProjectMaster = project_master[(project_master['Project Status'] == 'Open') | (project_master['Project Status'] == 'In Progress')].copy()
        st.success(":primary-background[Project Master Report loaded successfully!]", icon="✅")
    with st.spinner('**Loading User Allocation History Report...**'):
        user_allocation_history = csvORexcel(user_allocation_history, user_allocation_history.name)
        st.success(":primary-background[User Allocation History Report loaded successfully!]", icon="✅")

    # Transforming data
    with st.spinner('**Generating Resource Allocation Report...**'):
        interim_report, final_report = dataXform(del_hie_rep, exitEmpDB=exit_emp_DB, active_emp_DB=active_emp_DB)
        open_projects_df = open_projects(final_report, project_master)
        Allocated, Unallocated = check_pv(activeProjectMaster, pivot2 = interim_report, empDB = active_emp_DB)
        user_allocation_history['End Date'] = user_allocation_history['End Date'].apply(lambda x: x.strftime('%d-%m-%Y') if isinstance(x, (datetime.date, datetime.datetime)) else
                                                                                        pd.to_datetime(x).strftime('%d-%m-%Y') if x[0].isnumeric() else x) # Converting date format to DD-MM-YYYY.

        # Saving data in virtual memory buffer.
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            Allocated.to_excel(writer, sheet_name='Allocated', index=False)
            Unallocated.to_excel(writer, sheet_name='Unallocated', index=False)
            open_projects_df.to_excel(writer, sheet_name='Open Projects', index=False)
            final_report.to_excel(writer, index=False, sheet_name='Resource Allocation Report')
            user_allocation_history.to_excel(writer, sheet_name='User Allocation History Report', index=False)
            buffer.seek(0)
        time.sleep(5) # Simulating a delay for better UX

    # Showing resources who are available on Zoho but not in Employee Database.
    if not interim_report[interim_report['Role'].isna()].empty:
        st.subheader("Employees available in Zoho but not in Employee Database")
        data=interim_report[interim_report['Role'].isna()]
        styled_df = data.style.set_table_styles(
            [
                {'selector': 'th', 'props': [('white-space', 'nowrap')]},  # Prevent wrapping in Headers
                {'selector': 'td', 'props': [('white-space', 'nowrap')]}   # Prevent wrapping in Data cells
            ]
        )
        st.table(data=styled_df)

    st.success(":primary-background[Resource Allocation Report is ready to download!]", icon="✅")

    # Instering a button to download the report.
    st.download_button(data=buffer,
                        file_name="Resource_Allocation_Report "+str(dt.today().day)+"_"+dt.today().strftime('%b')+"'"+dt.today().strftime('%y')+".xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        label="Download Resource Allocation Report",)
    st.stop()





