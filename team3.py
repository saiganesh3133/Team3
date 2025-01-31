import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import io

# Title and Description
st.title("Dynamic Data visualization Dash Baord ")
st.write("This dashboard provides insights into The Data You Provided, including pricing trends, availability patterns, and customer preferences.")

# File Upload Section
st.header("Upload Data")
uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # Load the data based on file type
        if uploaded_file.name.endswith('.csv'):
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)
        
        # Convert last_review to datetime if the column exists
        if 'last_review' in data.columns:
            data['last_review'] = pd.to_datetime(data['last_review'])
        
        st.success("Data loaded successfully!")

        # Sidebar for Filtering
        st.sidebar.header("Filter Options")
        city_filter = st.sidebar.multiselect("Select Cities:", options=data['city'].unique(), default=data['city'].unique())
        price_range = st.sidebar.slider("Select Price Range:", 
                                      float(data['price'].min()), 
                                      float(data['price'].max()), 
                                      (float(data['price'].min()), float(data['price'].max())))
        
        filtered_data = data[(data['city'].isin(city_filter)) & 
                           (data['price'].between(price_range[0], price_range[1]))]

        # Visualization 1: Pricing Trends
        st.header("Pricing Trends")
        fig1 = px.histogram(filtered_data, x="price", nbins=50, 
                           title="Price Distribution", 
                           labels={"price": "Price ($)"})
        st.plotly_chart(fig1)

        # Visualization 2: Availability by City
        st.header("Availability Trends")
        if 'availability_365' in filtered_data.columns:
            availability = filtered_data.groupby("city")["availability_365"].mean().reset_index()
            fig2 = px.bar(availability, x="city", y="availability_365", 
                         title="Average Availability by City", 
                         labels={"availability_365": "Days Available"})
            st.plotly_chart(fig2)
        else:
            st.warning("Availability data not found in the dataset")

        # Visualization 3: Geospatial Mapping
        st.header("Geospatial Mapping")
        if all(col in filtered_data.columns for col in ['latitude', 'longitude']):
            map_center = [filtered_data['latitude'].mean(), filtered_data['longitude'].mean()]
            m = folium.Map(location=map_center, zoom_start=10)
            marker_cluster = MarkerCluster().add_to(m)
            
            for idx, row in filtered_data.iterrows():
                folium.Marker(
                    [row['latitude'], row['longitude']], 
                    popup=f"Price: ${row['price']}<br>City: {row['city']}"
                ).add_to(marker_cluster)
            
            st_folium(m, width=800, height=600)
        else:
            st.warning("Geospatial data (latitude/longitude) not found in the dataset")

        # Visualization 4: Customer Preferences
        st.header("Customer Preferences")
        if 'reviews_per_month' in filtered_data.columns:
            fig3 = px.box(filtered_data, x="city", y="reviews_per_month", 
                         title="Customer Reviews by City", 
                         labels={"reviews_per_month": "Reviews per Month"})
            st.plotly_chart(fig3)
        else:
            st.warning("Reviews data not found in the dataset")

        # Download Filtered Data
        st.header("Download Filtered Data")
        csv = filtered_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download Filtered Data",
            data=csv,
            file_name="filtered_airbnb_data.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.error("Please make sure your file has the required columns: city, price, and optionally availability_365, latitude, longitude, reviews_per_month")

else:
    st.info("Please upload a data file to begin analysis.")

# Footer
st.write("Dashboard powered by Streamlit. Used for understanding your data more Acuurately ")
st.write ("Uppload Your Daat and sit Tight, Your dash board is on the way")

