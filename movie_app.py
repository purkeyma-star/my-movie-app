import streamlit as st
from streamlit_gsheets import GSheetsConnection
import random

st.set_page_config(page_title="Plex Movie Collection", page_icon="🎬")

# 1. Your URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1-AtYz6Y6-wVls2EIuczq8g0RkEHnF0n8VAdjcpiK4dE/edit"

st.title("🎬 Plex Movie Manager on DS224+")

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Fetch data
    df = conn.read(spreadsheet=SHEET_URL, worksheet=0, ttl=0) 
    df.columns = df.columns.str.strip()
    col = "Movie" if "Movie" in df.columns else df.columns[0]
    movie_list = df[col].dropna().astype(str).tolist()
    
    # --- STATS & ACTIONS ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total", len(movie_list))
    with col2:
        sync_btn = st.button("🔄 Sync")
    with col3:
        random_btn = st.button("🎲 Pick")

    if sync_btn:
        st.cache_data.clear()
        st.rerun()

    # --- NEW FEATURE: RANDOM MOVIE PICKER ---
    if random_btn:
        random_choice = random.choice(movie_list)
        st.balloons()
        st.markdown(f"""
        <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; border-left: 5px solid #ff4b4b; text-align:center;">
            <p style="margin:0; color:#555; font-size:14px; text-transform:uppercase;">Tonight's Selection:</p>
            <h2 style="margin:0; color:#31333F;">🍿 {random_choice}</h2>
        </div>
        """, unsafe_content_allowed=True)

    st.markdown("---")

    # --- SEARCH INTERFACE ---
    search_query = st.text_input("Search your collection:", placeholder="Search title...")

    if search_query:
        results = [m for m in movie_list if search_query.lower() in m.lower()]
        
        if results:
            st.success(f"Found {len(results)} match(es):")
            for r in results:
                st.info(f"🎞️ {r}")
        else:
            st.error(f"❌ You don't own '{search_query}'.")

except Exception as e:
    st.error("Connection Error")
    st.code(e)
