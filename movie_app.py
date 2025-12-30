import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Plex Movie Collection", page_icon="🎬")

# 1. THE URL - Paste your link between the quotes below
# Make sure it ends in /edit or /view
SHEET_URL = "https://docs.google.com/spreadsheets/d/1-AtYz6Y6-wVls2EIuczq8g0RkEHnF0n8VAdjcpiK4dE/edit?gid=793352327#gid=793352327"

st.title("🎬 My Movie Collection Manager")

# 2. Connection Logic
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # We are using the URL directly here to bypass Secret issues for now
    df = conn.read(spreadsheet=SHEET_URL, worksheet="Have Movies")
    
    # Clean up column names (removes hidden spaces)
    df.columns = df.columns.str.strip()
    
    # Look for the movie column
    if "Movie" in df.columns:
        movie_list = df["Movie"].dropna().astype(str).tolist()
    else:
        # If "Movie" isn't found, use the very first column
        movie_list = df.iloc[:, 0].dropna().astype(str).tolist()
    
    st.success(f"✅ Connected! Found {len(movie_list)} movies.")

    # 3. Search Interface
    search_query = st.text_input("Search your collection:", placeholder="Enter movie title...")

    if search_query:
        # This finds matches even if they are partial
        results = [m for m in movie_list if search_query.lower() in m.lower()]

        if results:
            st.balloons()
            st.write(f"You own **{len(results)}** match(es):")
            for r in results:
                st.info(f"🍿 {r}")
        else:
            st.error(f"❌ '{search_query}' not found.")

except Exception as e:
    st.error("🔌 Connection Error")
    st.info("Try these 3 things:")
    st.write("1. **Sharing:** Click 'Share' in Google Sheets and set to 'Anyone with link'.")
    st.write("2. **Tab Name:** Ensure the tab at the bottom is named exactly **Have Movies**.")
    st.write("3. **URL:** Ensure the link in the code is your browser's address bar link.")
    
    # This shows the REAL technical error to help us fix it
    with st.expander("See technical error details"):
        st.code(e)
