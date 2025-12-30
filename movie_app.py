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
    .season-text { font-size: 13px; color: #BBBBBB; margin-left: 30px; display: block; margin-top: -5px; margin-bottom: 10px; }
    .missing-text { color: #FF4B4B; font-weight: bold; }
    .movie-link { text-decoration: none; color: #E0E0E0; font-weight: bold; }
    .movie-link:hover { color: #FF4B4B; }
    .sync-text { font-size: 11px; color: #888; text-align: center; margin-top: -10px; }
    </style>
    """, unsafe_allow_html=True)

# 1. YOUR GOOGLE SHEET URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1-AtYz6Y6-wVls2EIuczq8g0RkEHnF0n8VAdjcpiK4dE/edit"

st.title("🎬 Library Manager")

# Library Selector
library_type = st.radio("Select Library", ["Movies", "TV Shows"], horizontal=True)

# --- LOCKED GID VALUES ---
if library_type == "Movies":
    target_gid = 793352327  
else:
    target_gid = 446778614 

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Fetch Data using specific GIDs
    df = conn.read(spreadsheet=SHEET_URL, worksheet=target_gid, ttl=0)
    
    if df is not None:
        df.columns = df.columns.str.strip()
        
        # Identify Columns
        item_col = "Movie" if library_type == "Movies" else "Show"
        if item_col not in df.columns:
            item_col = df.columns[0]
            
        format_col = "Format" if "Format" in df.columns else None
        status_col = "Status" if "Status" in df.columns else None
        owned_col = "Seasons Owned" if "Seasons Owned" in df.columns else None
        total_col = "Total Seasons" if "Total Seasons" in df.columns else None
        
        full_df = df.dropna(subset=[item_col])
        items_list = full_df[item_col].astype(str).tolist()

        def display_item(row):
            title = str(row[item_col])
            fmt = str(row[format_col]).upper().strip() if format_col and not pd.isna(row[format_col]) else "SD"
            status = str(row[status_col]) if status_col and not pd.isna(row[status_col]) else ""
            badge_class = "badge-hd" if "HD" in fmt else "badge-sd"
            url = f"https://www.imdb.com/find?q={urllib.parse.quote(title)}"
            status_html = f"<span class='badge-status'>{status}</span>" if status else ""
            
            # Show Title & Format
            st.markdown(f"🎞️ <a href='{url}' target='_blank' class='movie-link'>{title}</a> <span class='{badge_class}'>{fmt}</span> {status_html}", unsafe_allow_html=True)
            
            # Show Season Info for TV Shows
            if library_type == "TV Shows" and owned_col and total_col:
                owned_raw = str(row[owned_col]) if not pd.isna(row[owned_col]) else ""
                total_val = row[total_col]
                
                if owned_raw and not pd.isna(total_val):
                    try:
                        total_seasons = int(total_val)
                        owned_list = [int(s.strip()) for s in str(owned_raw).split(',') if s.strip().isdigit()]
                        all_seasons = set(range(1, total_seasons + 1))
                        missing_seasons = sorted(list(all_seasons - set(owned_list)))
                        
                        missing_str = ", ".join(map(str, missing_seasons)) if missing_seasons else "None (Complete!)"
                        st.markdown(f"<span class='season-text'>Owned: {owned_raw} | <span class='missing-text'>Missing: {missing_str}</span></span>", unsafe_allow_html=True)
                    except:
                        pass

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
            st.info(f"✨ Suggested {library_type}:")
            # Pull the full row for the random pick to show season info if applicable
            random_row = full_df[full_df[item_col] == st.session_state.random_pick].iloc[0]
            display_item(random_row)

        st.markdown("---")
        t1, t2, t3 = st.tabs(["🔍 Search", "🆕 Newest", "📚 All"])

        with t1:
            search_query = st.text_input("Search", label_visibility="collapsed", placeholder=f"Search {library_type}...")
            if search_query:
                results = full_df[full_df[item_col].str.contains(search_query, case=False, na=False)]
                for _, row in results.iterrows(): display_item(row)

        with t2:
            for _, row in full_df.tail(10).iloc[::-1].iterrows(): display_item(row)

        with t3:
            for _, row in full_df.sort_values(item_col).iterrows(): display_item(row)

except Exception as e:
    st.error("⚠️ Connection Error")
    st.write("The app is using GID 793352327 for Movies and 446778614 for TV Shows.")
    st.code(e)
