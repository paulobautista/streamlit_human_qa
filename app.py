import streamlit as st
import pandas as pd
import mysql.connector
import json
import uuid
from mysql.connector import Error as MySQLError

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

# Navigation bar - show current index and add qualification check
col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 8])
with col1:
    if st.button("← Prev") and st.session_state.idx > 0:
        st.session_state.idx -= 1
with col2:
    if st.button("Next →") and st.session_state.idx < len(df) - 1:
        st.session_state.idx += 1
with col3:
    new_index = st.text_input("Jump to", value=str(st.session_state.idx), max_chars=3)
with col4:
    if st.button("Go") and new_index.isdigit():
        i = int(new_index)
        if 0 <= i < len(df):
            st.session_state.idx = i

# Show current row with only brand_name, no index and header
row_data = df.iloc[st.session_state.idx]
brand_name = row_data['brand_name']

# Apply custom styling to make the text bigger and add label styling
st.markdown("""
    <style>
        .brand-label {
            font-size: 14px;
            color: #666666;
            padding: 0 20px;
            margin-bottom: -15px;
        }
        .brand-name {
            font-size: 64px;
            text-align: left;
            padding: 20px;
            margin: 10px 0;
        }
    </style>
    """, unsafe_allow_html=True)

# Show brand name with label above
st.markdown('<div class="brand-label">Brand Name</div>', unsafe_allow_html=True)
st.markdown(f'<div class="brand-name">{brand_name}</div>', unsafe_allow_html=True)

# Create Google and Instagram search URLs
google_search_url = f"https://www.google.com/search?q={brand_name.replace(' ', '+')}"
instagram_search_url = f"https://www.google.com/search?q={brand_name.replace(' ', '+')}+Instagram"

# Create two buttons side by side
search_col1, search_col2, _ = st.columns([1, 1, 10])
with search_col1:
    st.link_button("🔍 Google Search", google_search_url, type="secondary", help="Open Google search in new tab")
with search_col2:
    st.link_button("📸 Instagram Search", instagram_search_url, type="secondary", help="Open Instagram search in new tab")

# Create three columns for form layout
left_col, middle_col, right_col = st.columns([2, 8, 2])

with left_col:
    # Website section
    website_col1, website_col2 = st.columns([3, 1])
    with website_col1:
        website = st.text_input("Website", value=st.session_state.website, max_chars=100, key="website_input")
    with website_col2:
        website_none = st.checkbox("None", value=st.session_state.website_none, key="website_none")
    if website_none:
        website = "None"

    # Instagram section
    insta_col1, insta_col2 = st.columns([3, 1])
    with insta_col1:
        instagram = st.text_input("Instagram", value=st.session_state.instagram, max_chars=100, key="instagram_input")
    with insta_col2:
        insta_none = st.checkbox("None", value=st.session_state.insta_none, key="insta_none")
    if insta_none:
        instagram = "None"

    # Qualification radio button
    qualification = st.radio(
        "",
        ["Qualified", "Not Qualified"],
        key="qualification",
        horizontal=True,
        index=None  # This makes it start with no selection
    )

    # Brand of Brands checkbox and comment
    bob_col1, bob_col2 = st.columns([2.5, 1.5])
    with bob_col1:
        brand_of_brands = st.checkbox("Brand of Brands", key="bob")
    with bob_col2:
        show_comment = st.button("Comment 💭", help="Add comment")

    # Collapsible comment section
    if show_comment:
        st.session_state.show_comment = not st.session_state.show_comment

    if st.session_state.show_comment:
        comment = st.text_area("Comment", key="bob_comment", height=150)

    # Submit button
    def create_connection():
        return mysql.connector.connect(
            host='database-streamlit.czq8ik4asj60.ap-southeast-1.rds.amazonaws.com',
            user='admin',
            password='f*_anVhnyYFRK8veG',
            database='streamlit_ecliptor'
        )

    def save_to_database(reviewer_name: str, answer_data: dict):
        conn = None
        cursor = None
        try:
            conn = create_connection()
            cursor = conn.cursor()

            # Create review_id using brand_name
            brand_name_slug = brand_name.lower().replace(' ', '_')
            review_id = f"{brand_name_slug}_{str(uuid.uuid4())}"
            answer_json = json.dumps(answer_data)

            query = """
                INSERT INTO jupiter_qa (review_id, reviewer_name, answer)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (review_id, reviewer_name, answer_json))
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

    def handle_submit():
        # Check if reviewer name is provided
        if not reviewer_name or reviewer_name.strip() == "":
            st.error("Please enter your name before submitting.")
            return

        # Check if qualification is selected
        if qualification is None:
            st.error("Please select Qualified or Not Qualified before submitting.")
            return

        # Create the JSON structure
        answer_data = {
            "website": website,
            "website_is_none": website_none,
            "instagram": instagram,
            "instagram_is_none": insta_none,
            "qualified": qualification == "Qualified",
            "brand_of_brands": brand_of_brands,
            "comment": comment if st.session_state.show_comment else ""
        }

        # Save to database
        save_success = save_to_database(reviewer_name, answer_data)

        # Reset ALL form fields
        st.session_state.website = ""
        st.session_state.instagram = ""
        st.session_state.website_none = False
        st.session_state.insta_none = False
        st.session_state.show_comment = False
        if "qualification" in st.session_state:
            del st.session_state.qualification
        if "bob" in st.session_state:
            del st.session_state.bob
        if "bob_comment" in st.session_state:
            del st.session_state.bob_comment

        # Reset the input widget values directly
        st.session_state.website_input = ""
        st.session_state.instagram_input = ""

        # Move to next item
        st.session_state.idx = min(st.session_state.idx + 1, len(df) - 1)

        # Show save status
        if save_success:
            st.success("Successfully saved!")
        else:
            st.error("Failed to save to database, but moved to next item.")

    st.button("Submit", use_container_width=True, key="submit_button",
        on_click=handle_submit)
