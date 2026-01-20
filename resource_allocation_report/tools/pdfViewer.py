import streamlit as st
import base64

# Increase the width to 800 pixels (adjust as needed)
st.markdown(
"""
<style>
[data-testid="stSidebar"] {
    min-width: 500px;
    max-width: 800px;
}
</style>
""",
unsafe_allow_html=True,)

def display_pdf_in_sidebar(file_path):
    # 1. Open the file
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    # 2. Embed the PDF using an HTML iframe
    # Note: We set width to 100% so it fits the sidebar
    pdf_display = f'''
        <iframe src="data:application/pdf;base64,{base64_pdf}" 
        width="100%" height="700px" type="application/pdf">
        </iframe>
    '''
    
    # 3. Render in Sidebar
    st.sidebar.markdown("<h1 style='text-align: center; color: #007BFF;'>User Manual</h1>", unsafe_allow_html=True)
    st.sidebar.markdown(pdf_display, unsafe_allow_html=True)