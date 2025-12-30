import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Plex Movie Collection", page_icon="🎬")
st.title("🎬 My Movie Collection Manager")

# Ensure there are NO spaces inside these quotes
SHEET_URL = "https://docs.google.com/spreadsheets/d/1-AtYz6Y6-wVls2EIuczq8g0RkEHnF0n8VAdjcpiK4dE/edit"

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # We use worksheet=0 to avoid the "Have Movies" space error
    # This automatically picks the FIRST tab in your Google Sheet
    df = conn.read(spreadsheet=SHEET_URL, ttl=1) 
    
    # Identify the column
    df.columns = df.columns.str.strip()
    col = "Movie" if "Movie" in df.columns else df.columns[0]
    movie_list = df[col].dropna().astype(str).tolist()
    
    st.success(f"✅ Connected! Loaded {len(movie_list)} movies.")

    search_query = st.text_input("Search your collection:")
    if search_query:
        results = [m for m in movie_list if search_query.lower() in m.lower()]
        if results:
            for r in results:
                st.info(f"🍿 {r}")
        else:
            st.error("Not found.")

except Exception as e:
    st.error("Connection Error")
    st.code(e) # This will show us if the space error persists
