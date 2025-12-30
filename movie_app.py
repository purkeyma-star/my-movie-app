import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
from thefuzz import process, fuzz
import urllib.parse
from datetime import datetime
import pytz 

st.set_page_config(page_title="Library Manager", page_icon="🎬", layout="wide")

# --- TIMEZONE ---
USER_TZ = pytz.timezone('US/Central') 

# CSS Styling (Badges for HD/SD and Status)
st.markdown("""
    <style>
    .badge-hd { background-color: #007BFF; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-left: 10px; }
    .badge-sd { background-color: #6C757D; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-left: 10px; }
    .badge-status { background-color: #28A745; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; margin-left: 5px; }
    .movie-link { text-decoration: none; color: #E0E0E0; font-weight: bold; }
    .movie-link:hover { color: #FF4B4B; }
    .sync-text { font-size: 11px; color: #888; text-align: center; margin-top: -10px; }
    </style>
    """, unsafe_allow_html=True)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1-AtYz6Y6-wVls2EIuczq8g0RkEHnF0n8VAdjcpiK4dE/edit"
conn = st.connection("gsheets", type=GSheetsConnection)

# --- NAVIGATION ---
st.title("🎬 Library Manager")
library_type = st.radio("Select Library", ["Movies", "TV Shows"], horizontal=True)

# Choose worksheet based on selection
worksheet_name = 0 if library_type == "Movies" else "TV Shows"

try:
    df = conn.read(spreadsheet=SHEET_URL, worksheet=worksheet_name, ttl=0) 
    df.columns = df.columns.str.strip()
    
    # Identify dynamic columns
    item_col = "Movie" if library_type == "Movies" else "Show"
    format_col = "Format" if "Format" in df.columns else None
    status_col = "Status" if "Status" in df.columns else None
    
    full_df = df.dropna(subset=[item_col])
    items_list = full_df[item_col].tolist()

    # --- HELPER DISPLAY ---
    def display_item(row):
        title = str(row[item_col])
        fmt = str(row[format_col]).upper().strip() if format_col else "SD"
        status = str(row[status_col]) if status_col else ""
        
        badge_class = "badge-hd" if "HD" in fmt else "badge-sd"
        search_term = urllib.parse.quote(title)
        site = "imdb" if library_type == "Movies" else "tvmaze"
        url = f"https://www.imdb.com/find?q={search_term}"
        
        status_html = f"<span class='badge-status'>{status}</span>" if status else ""
        st.markdown(f"🎞️ <a href='{url}' target='_blank' class='movie-link'>{title}</a> <span class='{badge_class}'>{fmt}</span> {status_html}", unsafe_allow_html=True)

    # --- TOP HEADER ---
    with st.container():
        h_col1, h_col2, h_col3 = st.columns([1, 1, 1])
        with h_col1:
            st.metric(f"Total {library_type}", len(items_list))
        with h_col2:
            if st.button("🔄 Sync", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
            local_now = datetime.now(USER_TZ).strftime("%I:%M %p")
            st.markdown(f"<p class='sync-text'>Updated: {local_now} CT</p>", unsafe_allow_html=True)
        with h_col3:
            if st.button("🎲 Roulette", use_container_width=True):
                st.session_state.random_pick = random.choice(items_list)
                st.balloons()

    if 'random_pick' in st.session_state:
        st.success(f"✨ Suggested {library_type}: {st.session_state.random_pick}")

    st.markdown("---")

    # --- TABS ---
    tab1, tab2, tab3 = st.tabs(["🔍 Search", "🆕 Newest", "📚 Filter & Browse"])

    with tab1:
        search_query = st.text_input("Search", label_visibility="collapsed", placeholder=f"Search {library_type}...")
        if search_query:
            results = full_df[full_df[item_col].str.contains(search_query, case=False, na=False)]
            for _, row in results.iterrows():
                display_item(row)

    with tab2:
        recent = full_df.tail(10).iloc[::-1]
        for _, row in recent.iterrows():
            display_item(row)

    with tab3:
        st.write("### Filter by Quality")
        f_col1, f_col2, f_col3 = st.columns(3)
        if 'f' not in st.session_state: st.session_state.f = "All"
        if f_col1.button("All"): st.session_state.f = "All"
        if f_col2.button("HD"): st.session_state.f = "HD"
        if f_col3.button("SD"): st.session_state.f = "SD"
        
        filtered_df = full_df
        if st.session_state.f == "HD":
            filtered_df = full_df[full_df[format_col].str.contains("HD", na=False)]
        elif st.session_state.f == "SD":
            filtered_df = full_df[~full_df[format_col].str.contains("HD", na=False)]
            
        for _, row in filtered_df.sort_values(item_col).iterrows():
            display_item(row)

except Exception as e:
    st.error(f"Error loading {library_type} worksheet.")
    st.info("Ensure you added a second tab named 'TV Shows' to your Google Sheet.")
