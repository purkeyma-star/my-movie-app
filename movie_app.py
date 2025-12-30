import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
from thefuzz import process, fuzz
import urllib.parse

st.set_page_config(page_title="Plex Library", page_icon="🎬", layout="wide")

# CSS Styling for Quality Badges and Link Colors
st.markdown("""
    <style>
    .badge-hd {
        background-color: #007BFF;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        margin-left: 10px;
    }
    .badge-sd {
        background-color: #6C757D;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        margin-left: 10px;
    }
    .movie-link {
        text-decoration: none;
        color: #E0E0E0;
        font-weight: bold;
    }
    .movie-link:hover {
        color: #FF4B4B;
    }
    </style>
    """, unsafe_allow_html=True)

# 1. Your URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1-AtYz6Y6-wVls2EIuczq8g0RkEHnF0n8VAdjcpiK4dE/edit"

st.title("🎬 Movie Manager Pro")

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # 2. Load Data
    df = conn.read(spreadsheet=SHEET_URL, worksheet=0, ttl=0) 
    df.columns = df.columns.str.strip()
    
    movie_col = "Movie" if "Movie" in df.columns else df.columns[0]
    format_col = "Format" if "Format" in df.columns else None
    
    full_df = df.dropna(subset=[movie_col])
    
    if format_col:
        movie_dict = pd.Series(full_df[format_col].values, index=full_df[movie_col]).to_dict()
    else:
        movie_dict = {m: "SD" for m in full_df[movie_col]}
        
    movie_list = list(movie_dict.keys())

    # --- HELPER FUNCTION TO DISPLAY MOVIES WITH LINKS ---
    def display_movie(title):
        fmt = str(movie_dict.get(title, "SD")).upper().strip()
        badge_class = "badge-hd" if "HD" in fmt else "badge-sd"
        
        # Create a URL-safe search link for IMDb
        search_term = urllib.parse.quote(title)
        imdb_url = f"https://www.imdb.com/find?q={search_term}"
        
        # Display as a clickable title + badge
        st.markdown(
            f"🎞️ <a href='{imdb_url}' target='_blank' class='movie-link'>{title}</a> "
            f"<span class='{badge_class}'>{fmt}</span>", 
            unsafe_allow_html=True
        )

    # --- TOP METRICS & QUICK ACTIONS ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Library", len(movie_list))
    with col2:
        if st.button("🔄 Sync", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with col3:
        if st.button("🎲 Roulette", use_container_width=True):
            st.session_state.random_pick = random.choice(movie_list)
            st.balloons()

    if 'random_pick' in st.session_state:
        st.info(f"✨ Suggested Selection (Tap title for info):")
        display_movie(st.session_state.random_pick)

    st.markdown("---")

    # --- TABS ---
    tab1, tab2, tab3 = st.tabs(["🔍 Search", "🆕 Newest", "📚 Filter & Browse"])

    with tab1:
        search_query = st.text_input("Search box", label_visibility="collapsed", placeholder="Search title or speak...")
        if search_query:
            exact_matches = [m for m in movie_list if search_query.lower() in m.lower()]
            fuzzy_results = process.extract(search_query, movie_list, limit=3, scorer=fuzz.token_sort_ratio)
            fuzzy_matches = [match[0] for match in fuzzy_results if match[1] >= 75 and match[0] not in exact_matches]

            if exact_matches:
                for m in sorted(exact_matches):
                    display_movie(m)
            elif fuzzy_matches:
                st.write("Maybe you meant...")
                for m in fuzzy_matches:
                    display_movie(m)
            else:
                st.error("Not found.")

    with tab2:
        st.write("Recent additions:")
        for m in movie_list[-10:][::-1]:
            display_movie(m)

    with tab3:
        # --- FILTER BUTTONS ---
        st.write("### Filter by Quality")
        f_col1, f_col2, f_col3 = st.columns(3)
        
        if 'filter' not in st.session_state:
            st.session_state.filter = "All"

        if f_col1.button("Show All", use_container_width=True):
            st.session_state.filter = "All"
        if f_col2.button("Only HD", use_container_width=True):
            st.session_state.filter = "HD"
        if f_col3.button("Only SD", use_container_width=True):
            st.session_state.filter = "SD"

        st.markdown(f"**Viewing: {st.session_state.filter}**")

        if st.session_state.filter == "HD":
            filtered_list = [m for m in movie_list if "HD" in str(movie_dict.get(m, "")).upper()]
        elif st.session_state.filter == "SD":
            filtered_list = [m for m in movie_list if "HD" not in str(movie_dict.get(m, "")).upper()]
        else:
            filtered_list = movie_list

        for m in sorted(filtered_list):
            display_movie(m)

except Exception as e:
    st.error("Setup Error")
    st.code(e)
