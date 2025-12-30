import streamlit as st
from streamlit_gsheets import GSheetsConnection
import random
from thefuzz import process, fuzz

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
    
    # Clean data
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
            <p style="margin:0; color:#AAAAAA; font-size:14px; text-transform:uppercase;">Tonight's Suggestion</p>
            <h2 style="margin:0; color:#FFFFFF;">{random_choice}</h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- TABS ---
    tab1, tab2, tab3 = st.tabs(["🔍 Search", "🆕 Recently Added", "📚 Browse All"])

    with tab1:
        search_query = st.text_input("Find a movie:", placeholder="Search by title (typos are okay!)...")
        
        if search_query:
            # 1. Check for Exact/Substring matches first
            exact_matches = [m for m in movie_list if search_query.lower() in m.lower()]
            
            # 2. Use Fuzzy Matching to find things that "sound" or "look" like the query
            # We look for matches with a score of 80 or higher (out of 100)
            fuzzy_results = process.extract(search_query, movie_list, limit=5, scorer=fuzz.token_sort_ratio)
            fuzzy_matches = [match[0] for match in fuzzy_results if match[1] >= 80 and match[0] not in exact_matches]

            if exact_matches:
                st.success(f"✅ Found in your collection:")
                for m in sorted(exact_matches):
                    st.write(f"🎞️ **{m}**")
                
                if fuzzy_matches:
                    with st.expander("Similar sounding titles:"):
                        for m in fuzzy_matches:
                            st.write(f"❓ {m}")
            
            elif fuzzy_matches:
                st.warning(f"⚠️ Not found exactly, but did you mean one of these?")
                for m in fuzzy_matches:
                    st.info(f"🍿 {m}")
            
            else:
                st.error(f"❌ '{search_query}' not found in your collection.")

    with tab2:
        # Show last 5 movies added (bottom of sheet)
        recent_movies = movie_list[-5:][::-1]
        for i, m in enumerate(recent_movies):
            st.write(f"{i+1}. **{m}**")

    with tab3:
        # Full alphabetical list
        sorted_list = sorted(movie_list)
        st.dataframe(sorted_list, use_container_width=True, hide_index=True)

except Exception as e:
    st.error("Connection Error")
    st.code(e)
