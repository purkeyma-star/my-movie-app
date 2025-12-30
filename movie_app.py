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

# CSS Styling
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

# 1. Your Google Sheet URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1-AtYz6Y6-wVls2EIuczq8g0RkEHnF0n8VAdjcpiK4dE/edit"

st.title("🎬 Library Manager")

# Library Selector
library_type = st.radio("Select Library", ["Movies", "TV Shows"], horizontal=True)

# UPDATED: Matching your exact tab names
ws_name = "Movies" if library_type == "Movies" else "TV Shows"

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # 2. Fetch Data
    df = conn.read(spreadsheet=SHEET_URL, worksheet=ws_name, ttl=0) 
    
    if df is not None:
        df.columns = df.columns.str.strip()
        
        # Determine column names based on selection
        item_col = "Movie" if library_type == "Movies" else "Show"
        
        # Safety check: if the column name doesn't exist, use the first column
        if item_col not in df.columns:
            item_col = df.columns[0]
            
        format_col = "Format" if "Format" in df.columns else None
        status_col = "Status" if "Status" in df.columns else None
        
        # Drop rows where the title is empty
        full_df = df.dropna(subset=[item_col])
        items_list = full_df[item_col].astype(str).tolist()

        # --- HELPER DISPLAY ---
        def display_item(row):
            title = str(row[item_col])
            fmt = str(row[format_col]).upper().strip() if format_col and not pd.isna(row[format_col]) else "SD"
            status = str(row[status_col]) if status_col and not pd.isna(row[status_col]) else ""
            badge_class = "badge-hd" if "HD" in fmt else "badge-sd"
            search_term = urllib.parse.quote(title)
            url = f"https://www.imdb.com/find?q={search_term}"
            status_html = f"<span class='badge-status'>{status}</span>" if status else ""
            st.markdown(f"🎞️ <a href='{url}' target='_blank' class='movie-link'>{title}</a> <span class='{badge_class}'>{fmt}</span> {status_html}", unsafe_allow_html=True)

        # --- TOP HEADER ---
        with st.container():
            h_col1, h_col2, h_col3 = st.columns([1, 1, 1])
            with h_col1:
                st.metric(f"Total {library_type}", len(items_list))
            with h_col2:
                if st.button("🔄 Sync", key="sync_btn", use_container_width=True):
                    st.cache_data.clear()
                    st.rerun()
                local_now = datetime.now(USER_TZ).strftime("%I:%M %p")
                st.markdown(f"<p class='sync-text'>Updated: {local_now} CT</p>", unsafe_allow_html=True)
            with h_col3:
                if st.button("🎲 Roulette", key="roulette_btn", use_container_width=True):
                    st.session_state.random_pick = random.choice(items_list)
                    st.balloons()

        if 'random_pick' in st.session_state:
            st.info(f"✨ Suggested {library_type}: {st.session_state.random_pick}")

        st.markdown("---")

        # --- TABS ---
        t1, t2, t3 = st.tabs(["🔍 Search", "🆕 Newest", "📚 All"])

        with t1:
            search_query = st.text_input("Search", label_visibility="collapsed", placeholder=f"Search {library_type}...")
            if search_query:
                # Fuzzy Matching Logic
                results = full_df[full_df[item_col].str.contains(search_query, case=False, na=False)]
                if not results.empty:
                    for _, row in results.iterrows():
                        display_item(row)
                else:
                    st.warning("No matches found.")

        with t2:
            # Show last 10 items
            recent = full_df.tail(10).iloc[::-1]
            for _, row in recent.iterrows():
                display_item(row)

        with t3:
            # Sorted list
            sorted_df = full_df.sort_values(item_col)
            for _, row in sorted_df.iterrows():
                display_item(row)

except Exception as e:
    st.error("⚠️ Connection Error")
    st.write(f"The app is looking for a tab named **'{ws_name}'**.")
    st.write("Current Tab Name in Google Sheets must be exact.")
    st.code(e)
