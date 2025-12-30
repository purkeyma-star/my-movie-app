import streamlit as st
from streamlit_gsheets import GSheetsConnection
import random

st.set_page_config(page_title="Plex Movie Collection", page_icon="🎬", layout="wide")

# 1. Your URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1-AtYz6Y6-wVls2EIuczq8g0RkEHnF0n8VAdjcpiK4dE/edit"

st.title("🎬 Plex Movie Manager Pro")

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Fetch data
    df = conn.read(spreadsheet=SHEET_URL, worksheet=0, ttl=0) 
    df.columns = df.columns.str.strip()
    col = "Movie" if "Movie" in df.columns else df.columns[0]
    
    # Remove empty rows and convert to list
    full_df = df.dropna(subset=[col])
    movie_list = full_df[col].astype(str).tolist()
    
    # --- TOP METRICS & ACTIONS ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Library", len(movie_list))
    with col2:
        if st.button("🔄 Sync Library", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with col3:
        random_btn = st.button("🎲 Movie Roulette", use_container_width=True)

    # --- RANDOM PICKER ---
    if random_btn:
        random_choice = random.choice(movie_list)
        st.balloons()
        st.markdown(f"""
        <div style="background-color:#1E1E1E; padding:20px; border-radius:10px; border: 2px solid #FF4B4B; text-align:center;">
            <p style="margin:0; color:#AAAAAA; font-size:14px;">SUGGESTION</p>
            <h2 style="margin:0; color:#FFFFFF;">{random_choice}</h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- SEARCH & RECENT TABS ---
    tab1, tab2 = st.tabs(["🔍 Search Collection", "🆕 Recently Added"])

    with tab1:
        search_query = st.text_input("Find a movie:", placeholder="Search by title...")
        if search_query:
            results = [m for m in movie_list if search_query.lower() in m.lower()]
            if results:
                st.write(f"Matches found: {len(results)}")
                for r in sorted(results):
                    st.success(f"✅ {r}")
            else:
                st.error(f"❌ '{search_query}' is not in your collection.")

    with tab2:
        # Assumes the newest movies are at the bottom of your sheet
        recent_movies = movie_list[-5:][::-1] # Gets last 5 and reverses to show newest first
        for i, m in enumerate(recent_movies):
            st.write(f"{i+1}. **{m}**")

    # --- FULL ALPHABETICAL BROWSER ---
    with st.expander("📚 Browse Full Alphabetical List"):
        sorted_list = sorted(movie_list)
        for m in sorted_list:
            st.text(m)

except Exception as e:
    st.error("Connection Error")
    st.code(e)
