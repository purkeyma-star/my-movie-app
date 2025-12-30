import streamlit as st
from streamlit_gsheets import GSheetsConnection

# 1. App setup
st.set_page_config(page_title="Plex Movie Collection", page_icon="🎬")
st.title("🎬 My Movie Collection Manager")
st.write("Search your live Google Sheet to see if you own a title.")

# 2. Connect to Google Sheets
# Replace the URL below with your actual Google Sheet URL
url = "https://docs.google.com/spreadsheets/d/1-AtYz6Y6-wVls2EIuczq8g0RkEHnF0n8VAdjcpiK4dE/"

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Specifically target the "Have Movies" sheet
    df = conn.read(spreadsheet=url, worksheet="Have Movies")
    
    # Identify the correct column for movie titles
    # Assumes your column is named "Movie" as seen in your sheet data
    column_name = "Movie" if "Movie" in df.columns else df.columns[0]
    movie_list = df[column_name].astype(str).tolist()
    
    st.success(f"Connected! Loaded {len(movie_list)} movies from 'Have Movies'.")

    # 3. Search Interface
    search_query = st.text_input("Enter a movie title to search:", placeholder="e.g. Aliens")

    if search_query:
        results = [movie for movie in movie_list if search_query.lower() in movie.lower()]

        if results:
            st.balloons()
            st.success(f"✅ Yes! You own **{len(results)}** match(es):")
            for result in results:
                st.write(f"- {result}")
        else:
            st.error(f"❌ No, '{search_query}' was not found in your collection.")

except Exception as e:
    st.error("Could not connect to the Google Sheet. Make sure the URL is correct and the sheet is shared.")
