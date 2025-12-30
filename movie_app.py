import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
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
    .movie-link { text-decoration: none; color: #E0E0E0; font-weight: bold; }
    .movie-link:hover { color: #FF4B4B; }
    .sync-text { font-size: 11px; color: #888; text-align: center; margin-top: -10px; }
    .not-found { padding: 20px; background-color: #1E1E1E; border-left: 5px solid #FF4B4B; border-radius: 5px; color: #E0E0E0; margin-top: 10px; }
    
    /* Season Grid Styles */
    .season-container { display: flex; flex-wrap: wrap; gap: 4px; margin: 5px 0 15px 30px; }
    .s-box { width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 10px; border-radius: 3px; font-weight: bold; }
    .s-owned { background-color: #28A745; color: white; border: 1px solid #1e7e34; }
    .s-missing { background-color: transparent; color: #888; border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1-AtYz6Y6-wVls2EIuczq8g0RkEHnF0n8VAdjcpiK4dE/edit"
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🎬 Library Manager")
library_type = st.radio("Select Library", ["Movies", "TV Shows"], horizontal=True)

# YOUR LOCKED GIDs
if library_type == "Movies":
    target_gid = 793352327  
else:
    target_gid = 446778614 

try:
    df = conn.read(spreadsheet=SHEET_URL, worksheet=target_gid, ttl=0)
    df.columns = df.columns.str.strip()
    
    item_col = "Movie" if library_type == "Movies" else "Show"
    if item_col not in df.columns: item_col = df.columns[0]
    
    format_col = "Format" if "Format" in df.columns else None
    owned_col = "Seasons Owned" if "Seasons Owned" in df.columns else None
    total_col = "Total Seasons" if "Total Seasons" in df.columns else None
    
    full_df = df.dropna(subset=[item_col])

    def display_item(row):
        title = str(row[item_col])
        fmt = str(row[format_col]).upper().strip() if format_col and not pd.isna(row[format_col]) else "SD"
        badge_class = "badge-hd" if "HD" in fmt else "badge-sd"
        url = f"https://www.imdb.com/find?q={urllib.parse.quote(title)}"
        
        st.markdown(f"🎞️ <a href='{url}' target='_blank' class='movie-link'>{title}</a> <span class='{badge_class}'>{fmt}</span>", unsafe_allow_html=True)
        
        if library_type == "TV Shows" and owned_col and total_col:
            owned_raw = str(row[owned_col]) if not pd.isna(row[owned_col]) else ""
            total_val = row[total_col]
            if not pd.isna(total_val) and total_val != "":
                try:
                    total_seasons = int(float(total_val))
                    owned_list = [int(s.strip()) for s in str(owned_raw).split(',') if s.strip().isdigit()]
                    grid_html = '<div class="season-container">'
                    for s in range(1, total_seasons + 1):
                        cl = "s-owned" if s in owned_list else "s-missing"
                        grid_html += f'<div class="s-box {cl}">{s}</div>'
                    grid_html += '</div>'
                    st.markdown(grid_html, unsafe_allow_html=True)
                except: pass

    # --- TOP HEADER ---
    with st.container():
        h_col1, h_col2, h_col3 = st.columns([1, 1, 1])
        with h_col1: st.metric(f"Total {library_type}", len(full_df))
        with h_col2:
            if st.button("🔄 Sync", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
            local_now = datetime.now(USER_TZ).strftime("%I:%M %p")
            st.markdown(f"<p class='sync-text'>Updated: {local_now} CT</p>", unsafe_allow_html=True)
        with h_col3:
            if st.button("🎲 Roulette", use_container_width=True):
                st.session_state.random_pick = random.choice(full_df[item_col].tolist())
                st.balloons()

    st.markdown("---")
    t1, t2, t3 = st.tabs(["🔍 Search", "🆕 Newest", "📚 All"])
    
    with t1:
        search_query = st.text_input("Search", placeholder=f"Search for a {library_type[:-1].lower()}...")
        if search_query:
            results = full_df[full_df[item_col].str.contains(search_query, case=False, na=False)]
            
            # THE FIX: Check if we have results
            if not results.empty:
                for _, row in results.iterrows(): 
                    display_item(row)
            else:
                # Stylish "Not Found" UI
                st.markdown(f"""
                    <div class="not-found">
                        <h4>🚫 Not in Collection</h4>
                        <p>I couldn't find <b>"{search_query}"</b> in your {library_type.lower()} list.</p>
                        <hr style="border: 0.5px solid #444;">
                        <small>Check for typos or add this title to your Google Sheet and tap <b>Sync</b>.</small>
                    </div>
                """, unsafe_allow_html=True)

    with t2:
        for _, row in full_df.tail(10).iloc[::-1].iterrows(): display_item(row)
    with t3:
        for _, row in full_df.sort_values(item_col).iterrows(): display_item(row)

except Exception as e:
    st.error("⚠️ Connection Error")
    st.code(e)
