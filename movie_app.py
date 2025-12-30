import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Plex Movie Collection on DS224+", page_icon="🎬")

# 1. Your URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1-AtYz6Y6-wVls2EIuczq8g0RkEHnF0n8VAdjcpiK4dE/edit"

# 2. Sidebar/Top Header for Stats
st.title("🎬 Plex Movie Manager")

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # ttl=0 ensures it doesn't cache old data for too long
    df = conn.read(spreadsheet=SHEET_URL, worksheet=0, ttl=0) 
    
    df.columns = df.columns.str.strip()
    col = "Movie" if "Movie" in df.columns else df.columns[0]
    movie_list = df[col].dropna().astype(str).tolist()
    
    # --- NEW FEATURE: STATS BOX ---
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Movies", len(movie_list))
    with col2:
        if st.button("🔄 Sync List"):
            st.cache_data.clear()
            st.rerun()
    # ------------------------------

    st.markdown("---")

    search_query = st.text_input("Search your collection:", placeholder="e.g. Inception")

    if search_query:
        # Improved search to handle multiple words
        results = [m for m in movie_list if search_query.lower() in m.lower()]
        
        if results:
            st.success(f"Found {len(results)} match(es):")
            for r in results:
                st.info(f"🍿 {r}")
        else:
            st.error(f"❌ You don't seem to own '{search_query}' yet.")

except Exception as e:
    st.error("Connection Error")
    st.code(e)
