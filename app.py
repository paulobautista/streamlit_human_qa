import streamlit as st
import pandas as pd
import mysql.connector
import json
import uuid
from mysql.connector import Error as MySQLError

def create_connection():
    return mysql.connector.connect(
        host='database-streamlit.czq8ik4asj60.ap-southeast-1.rds.amazonaws.com',
        user='admin',
        password='f*_anVhnyYFRK8veG',
        database='streamlit_ecliptor'
    )

def save_to_database(reviewer_name: str, answer_data: dict, brand_id: str):
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # Generate a new UUID for review_id
        review_id = str(uuid.uuid4())

        answer_json = json.dumps(answer_data)
        query = """
            INSERT INTO jupiter_qa (review_id, brand_id, reviewer_name, answer)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (review_id, brand_id, reviewer_name, answer_json))
        conn.commit()
        return True
    except MySQLError as e:
        st.error(f"Error saving to database: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Set wide mode at the start
st.set_page_config(layout="wide")

# Initialize session states at the start of the app
if "idx" not in st.session_state:
    st.session_state.idx = 0
if "reviewer_name" not in st.session_state:
    st.session_state.reviewer_name = ""
if "website" not in st.session_state:
    st.session_state.website = ""
if "instagram" not in st.session_state:
    st.session_state.instagram = ""
if "website_none" not in st.session_state:
    st.session_state.website_none = False
if "insta_none" not in st.session_state:
    st.session_state.insta_none = False
if "show_comment" not in st.session_state:
    st.session_state.show_comment = False

# Add reviewer name field at the top
reviewer_name = st.text_input(
    "Reviewer Name",
    value=st.session_state.reviewer_name,
    key="reviewer_name_input"
)
# Update session state when name changes
st.session_state.reviewer_name = reviewer_name

# Load your CSV
df = pd.read_csv("data.csv")  # replace with your CSV

# Navigation bar - adjusted column widths
col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 8])
with col1:
    if st.button("← Prev") and st.session_state.idx > 0:
        st.session_state.idx -= 1
with col2:
    if st.button("Next →") and st.session_state.idx < len(df) - 1:
        st.session_state.idx += 1
with col3:
    new_index = st.text_input("Jump to", value=str(st.session_state.idx), max_chars=4)
with col4:
    if st.button("Go") and new_index.isdigit():
        i = int(new_index)
        if 0 <= i < len(df):
            st.session_state.idx = i

# Show current row with all columns in a table
row_data = df.iloc[st.session_state.idx]
df_display = pd.DataFrame([row_data])
df_display = df_display.drop(columns=['brand_id'])

# Function to convert URLs to clickable links
def make_clickable(val):
    if pd.isna(val):
        return val
    if val.startswith('http'):
        return f'<a href="{val}" target="_blank">{val}</a>'
    return val

# Convert URLs to clickable links
df_html = df_display.copy()
for col in ['brand_website', 'brand_instagram_link']:
    df_html[col] = df_html[col].apply(make_clickable)

# Apply custom styling to make the table text bigger and handle links
st.markdown("""
    <style>
        .stTable td, .stTable th {
            font-size: 18px !important;
            padding: 10px !important;
            white-space: pre-wrap !important;
        }
        .stTable th {
            font-weight: bold !important;
            color: #666666 !important;
        }
        .stTable a {
            color: #0068c9 !important;
            text-decoration: underline !important;
        }
        .stTable a:hover {
            color: #004075 !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Display the table with clickable links
st.write(df_html.to_html(escape=False, index=False), unsafe_allow_html=True)

# Create Google and Instagram search URLs
google_search_url = f"https://www.google.com/search?q={row_data['brand_name'].replace(' ', '+')}"
instagram_search_url = f"https://www.google.com/search?q={row_data['brand_name'].replace(' ', '+')}+Instagram"

# Create two buttons side by side
search_col1, search_col2, _ = st.columns([1, 1, 10])
with search_col1:
    st.link_button("🔍 Google Search", google_search_url, type="secondary", help="Open Google search in new tab")
with search_col2:
    st.link_button("📸 Instagram Search", instagram_search_url, type="secondary", help="Open Instagram search in new tab")

# Custom styling for headers, text, and checkbox
st.markdown("""
    <style>
        .big-font {
            font-size: 24px !important;
            margin-bottom: 10px !important;
        }
        .instruction-text {
            font-size: 18px !important;
            margin-bottom: 20px !important;
        }
        .question-text {
            font-size: 16px !important;
            margin-bottom: 10px !important;
        }
        .stCheckbox {
            font-size: 16px !important;
            padding-left: 0 !important;
            background: none !important;
            border: none !important;
            box-shadow: none !important;
        }
        .stCheckbox > label {
            display: flex !important;
            align-items: center !important;
            padding: 5px !important;
            background: none !important;
        }
        .stCheckbox > label > div {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            flex-direction: row !important;
            gap: 10px !important;
        }
        .stCheckbox > label > div > p {
            margin: 0 !important;
            white-space: nowrap !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Instructions section
st.markdown('<p class="big-font">Instructions</p>', unsafe_allow_html=True)
st.markdown('<p class="instruction-text">Read instructions for v1.0 on this <a href="https://docs.google.com/document/d/1DVhJAO9qUVcTShwosys9sDghNpGnRjHDCQDFMejMTYE/edit?tab=t.0" target="_blank">google doc</a></p>', unsafe_allow_html=True)

st.write("")  # Add spacing

# Questions header
st.markdown('<p class="big-font">Questions</p>', unsafe_allow_html=True)

# Qualification section with smaller question text
st.markdown('<p class="question-text">Read the brand description, and skim through the website. Given that information, is the brand qualified?</p>', unsafe_allow_html=True)
qualification = st.radio(
    "",
    ["Qualified", "Not Qualified"],
    key="qualification",
    horizontal=True,
    index=None
)

st.write("")  # Add spacing

# Instagram section with smaller question text
st.markdown('<p class="question-text">What is the official Instagram of the account? (No Change Needed if Unqualified)</p>', unsafe_allow_html=True)
instagram_status = st.radio(
    "Instagram Status",
    ["No change needed",
     "Model is wrong, answer is None",
     "Model is wrong, this is answer"],
    key="instagram_status",
    horizontal=False,
    label_visibility="collapsed"
)
instagram = st.text_input("Instagram", max_chars=100, key="instagram_input")  # Just a blank field

# Brand of Brands section with small checkbox
st.markdown('<p class="question-text">Is this brand a brand of brands?</p>', unsafe_allow_html=True)
brand_of_brands = st.checkbox("This brand is a brand of brands", key="bob")

# Comment field
comment = st.text_area("Comment", key="bob_comment", height=100)

# Collect needed data before calling 'save_to_database'
if st.button("Submit", use_container_width=True, key="submit_button"):
    if qualification is None:
        st.error("Please select either 'Qualified' or 'Not Qualified' before submitting.")
    else:
        # Gather your data in a dictionary
        answer_data = {
            "qualification": qualification,
            "instagram_status": instagram_status,
            "instagram": instagram,  # Always store the instagram field value
            "brand_of_brands": brand_of_brands,
            "comment": comment
        }

        brand_id = row_data['brand_id']
        success = save_to_database(st.session_state.reviewer_name, answer_data, brand_id)
        if success:
            st.success("Data saved successfully!")
            if st.session_state.idx < len(df) - 1:
                st.session_state.idx += 1
                st.rerun()
        else:
            st.error("Failed to save data. Please check the logs for errors.")

# Add custom CSS for button-like checkboxes
st.markdown("""
    <style>
        /* Style for button-like checkboxes */
        .stCheckbox {
            padding: 10px !important;
            margin-bottom: 20px !important;  /* Added vertical spacing */
        }
        .stCheckbox > label {
            background-color: #f0f2f6;
            padding: 10px 25px !important;
            border-radius: 4px;
            cursor: pointer;
            width: 100%;
            display: inline-block;
            text-align: center;
            min-width: 150px !important;
            white-space: nowrap !important;
        }
        .stCheckbox > label:hover {
            background-color: #e0e2e6;
        }
        .stCheckbox > label > div {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            flex-direction: row !important;
            gap: 10px !important;
        }
        .stCheckbox > label > div > p {
            margin: 0 !important;
            white-space: nowrap !important;
        }

        /* Add spacing between sections */
        .row-widget {
            margin-bottom: 30px !important;
        }

        /* Add spacing for text inputs */
        .stTextInput {
            margin-bottom: 30px !important;
        }
    </style>
""", unsafe_allow_html=True)
