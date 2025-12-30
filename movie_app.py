import streamlit as st
from streamlit_gsheets import GSheetsConnection
import random
from thefuzz import process, fuzz
from streamlit_mic_recorder import mic_recorder

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
    movie_list = df[col].dropna().astype(str).tolist()
    
    # --- TOP METRICS & ACTIONS ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Library", len(movie_list))
    with col2:
        if st.button("🔄 Sync Library", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with col3:
        if st.button("🎲 Roulette", use_container_width=True):
            st.session_state.random_pick = random.choice(movie_list)
            st.balloons()

    if 'random_pick' in st.session_state:
        st.markdown(f"""
        <div style="background-color:#1E1E1E; padding:20px; border-radius:10px; border: 2px solid #FF4B4B; text-align:center; margin-bottom:20px;">
            <p style="margin:0; color:#AAAAAA; font-size:14px; text-transform:uppercase;">Tonight's Suggestion</p>
            <h2 style="margin:0; color:#FFFFFF;">{st.session_state.random_pick}</h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- TABS ---
    tab1, tab2, tab3 = st.tabs(["🔍 Search", "🆕 Recently Added", "📚 Browse All"])

    with tab1:
        st.write("Search by typing or tapping the mic below:")
        
        # --- VOICE SEARCH COMPONENT ---
        audio_prompt = mic_recorder(
            start_prompt="🎙️ Start Voice Search",
            stop_prompt="🛑 Stop & Search",
            key='recorder'
        )
        
        # Capture text from typing
        typed_query = st.text_input("Type title here:", placeholder="Search...")
        
        # Determine the final query (Voice text or Typed text)
        final_query = ""
        if audio_prompt and audio_prompt.get('text'):
            final_query = audio_prompt['text']
            st.info(f"Searching for: **{final_query}**")
        elif typed_query:
            final_query = typed_query

        if final_query:
            # Fuzzy Matching Logic
            exact_matches = [m for m in movie_list if final_query.lower() in m.lower()]
            fuzzy_results = process.extract(final_query, movie_list, limit=5, scorer=fuzz.token_sort_ratio)
            fuzzy_matches = [match[0] for match in fuzzy_results if match[1] >= 75 and match[0] not in exact_matches]

            if exact_matches:
                st.success(f"✅ Found in your collection:")
                for m in sorted(exact_matches):
                    st.write(f"🍿 **{m}**")
            elif fuzzy_matches:
                st.warning(f"⚠️ Did you mean one of these?")
                for m in fuzzy_matches:
                    st.info(f"🍿 {m}")
            else:
                st.error(f"❌ '{final_query}' not found.")

    with tab2:
        recent_movies = movie_list[-5:][::-1]
        for i, m in enumerate(recent_movies):
            st.write(f"{i+1}. **{m}**")

    with tab3:
        sorted_list = sorted(movie_list)
        st.dataframe(sorted_list, use_container_width=True, hide_index=True)

except Exception as e:
    st.error("Connection Error")
    st.code(e)
