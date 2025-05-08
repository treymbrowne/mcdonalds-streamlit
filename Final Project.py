import streamlit as st
# ✅ MUST BE IMMEDIATELY AFTER streamlit import
st.set_page_config(page_title="McDonald's Store Reviews", layout="wide")

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import st_folium

# [DA1] Clean or manipulate data
def load_data():
    try:
        df = pd.read_csv('CS 230/McDonald_s_Reviews.csv', encoding='ISO-8859-1')
        df.columns = df.columns.str.strip()

        # Convert "4 stars" → 4.0
        df['rating'] = df['rating'].str.extract(r'(\d)').astype(float)

        # Drop rows with missing important values
        df.dropna(subset=['rating', 'latitude', 'longitude', 'store_name', 'review'], inplace=True)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# [PY1] Function with default parameter
def filter_reviews(df, min_rating=3):
    return df[df['rating'] >= min_rating]

# [PY2] Rating summary
def rating_summary(df):
    avg_rating = df['rating'].mean()
    median_rating = df['rating'].median()
    return avg_rating, median_rating

# Load and clean data
df = load_data()

# Streamlit UI customization
st.sidebar.image("https://1000logos.net/wp-content/uploads/2017/03/McDonalds-Logo.png", width=150)
st.title("🍔 McDonald's Store Reviews Dashboard")

# Sidebar filters
min_rating = st.sidebar.slider("Minimum Rating", 1, 5, 3)
keyword_filter = st.sidebar.text_input("Search Review Text")

# Apply filters
df_filtered = filter_reviews(df, min_rating=min_rating)
if keyword_filter:
    df_filtered = df_filtered[df_filtered['review'].str.contains(keyword_filter, case=False)]

# Store dropdown — only if options exist
store_options = df_filtered['store_name'].unique()
if len(store_options) > 0:
    selected_store = st.sidebar.selectbox("Select a Store", store_options)
else:
    selected_store = None

# Sidebar debug info
st.sidebar.markdown("### 📊 Debug Info")
st.sidebar.write(f"Total Reviews: {len(df)}")
st.sidebar.write(f"After Rating Filter: {len(filter_reviews(df, min_rating))}")
st.sidebar.write(f"After Keyword Filter: {len(df_filtered)}")
st.sidebar.write(f"Available Stores: {len(store_options)}")

# If store selected, show results
if selected_store:
    df_store = df_filtered[df_filtered['store_name'] == selected_store]
    df_store = df_store.dropna(subset=['latitude', 'longitude'])

    st.subheader(f"Top Rated Reviews for {selected_store}...")
    col1, col2 = st.columns(2)

    # [VIZ1] Bar Chart: Top 10 stores by average rating
    with col1:
        top_stores = df_filtered.groupby('store_name')['rating'].mean().sort_values(ascending=False).head(10)
        plt.figure(figsize=(10, 6))
        sns.barplot(x=top_stores.values, y=top_stores.index, palette='YlOrRd')
        plt.xlabel('Average Rating')
        plt.title("Top 10 Stores by Avg Rating")
        st.pyplot(plt)

    # [VIZ2] Histogram: Distribution of all ratings
    with col2:
        plt.figure(figsize=(10, 6))
        sns.histplot(df_filtered['rating'], bins=5, kde=True, color='orange')
        plt.title("Rating Distribution")
        plt.xlabel("Rating")
        plt.ylabel("Count")
        st.pyplot(plt)

    st.dataframe(df_store.sort_values(by='rating', ascending=False).head(10))

    # Map section
    st.markdown("### 📍 Store Locations Map")
    if not df_store.empty:
        m = folium.Map(location=[df_store['latitude'].mean(), df_store['longitude'].mean()], zoom_start=12)
        for row in df_store.itertuples():
            folium.Marker(
                location=[row.latitude, row.longitude],
                tooltip=row.store_name,
                icon=folium.Icon(color="red", icon="cutlery", prefix='fa')
            ).add_to(m)
        st_folium(m, width=700, height=500)
    else:
        st.warning("No valid location data available for the selected store.")
        default_map = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
        st_folium(default_map, width=700, height=500)
else:
    st.warning("No store data available to select.")
    default_map = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
    st_folium(default_map, width=700, height=500)

# [PY5] Efficient store count summary
store_counts = df_filtered['store_name'].value_counts().to_dict()
st.sidebar.markdown("### Review Count by Store")
st.sidebar.write(store_counts)
