import streamlit as st
import pandas as pd

# 1. Set up the App Title and Description
st.title("🎬 My Movie Collection Manager")
st.write("Upload your movie list and search to see if you own a title.")

# 2. Create the File Uploader
uploaded_file = st.file_uploader("Upload your list (CSV or TXT)", type=['csv', 'txt'])

if uploaded_file is not None:
    try:
        # Load the data based on file type
        if uploaded_file.name.endswith('.csv'):
            # Assumes the movies are in a column named 'Title' or the first column
            df = pd.read_csv(uploaded_file)
            # If 'Title' column exists use it, otherwise use the first column
            if 'Title' in df.columns:
                movie_list = df['Title'].astype(str).tolist()
            else:
                movie_list = df.iloc[:, 0].astype(str).tolist()
        else:
            # For TXT files, assumes one movie per line
            stringio = uploaded_file.getvalue().decode("utf-8")
            movie_list = stringio.splitlines()

        # Clean up the list (remove empty lines)
        movie_list = [movie.strip() for movie in movie_list if movie.strip()]
        
        st.success(f"Successfully loaded {len(movie_list)} movies!")

        # 3. Create the Search Interface
        st.markdown("---")
        search_query = st.text_input("Enter a movie title to search:", placeholder="e.g. Jurassic Park")

        if search_query:
            # Normalize to lowercase for better matching
            results = []
            for movie in movie_list:
                if search_query.lower() in movie.lower():
                    results.append(movie)

            # 4. Display Results
            if results:
                st.balloons() # Fun effect for a positive match
                st.success(f"✅ Yes! You own **{len(results)}** match(es):")
                for result in results:
                    st.write(f"- {result}")
            else:
                st.error(f"❌ No, '{search_query}' was not found in your collection.")

        # Optional: Show the full list
        with st.expander("View Full Collection"):
            st.dataframe(movie_list)

    except Exception as e:
        st.error(f"Error reading file: {e}")

else:
    st.info("Please upload a file to get started.")