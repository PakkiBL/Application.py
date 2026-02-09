import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Page Config
st.set_page_config(page_title="Smart Shopping Deal Comparator", page_icon="🛍", layout="wide")

# Get API Key Securely
API_KEY = st.secrets["SERPAPI_KEY"]

st.title("🛍 Smart Shopping Deal Comparator")
st.markdown("Compare prices across stores and get AI-based buying suggestions.")

# Sidebar Filters
st.sidebar.header("⚙ Filters")
num_results = st.sidebar.slider("Number of stores to compare", 3, 10, 5)

product_name = st.text_input("🔎 Enter product name")

if st.button("Compare Prices"):

    if product_name.strip() == "":
        st.warning("Please enter a product name.")
        st.stop()

    with st.spinner("Fetching latest prices..."):

        url = "https://serpapi.com/search.json"

        params = {
            "engine": "google_shopping",
            "q": product_name,
            "api_key": API_KEY,
            "gl": "in",   # India location
            "hl": "en"
        }

        response = requests.get(url, params=params)
        data = response.json()

        results = data.get("shopping_results", [])

        if not results:
            st.error("No results found. Try another product.")
            st.stop()

        products = []

        for item in results[:num_results]:
            try:
                price_text = item.get("price", "0")
                price_clean = (
                    price_text.replace("₹", "")
                    .replace(",", "")
                    .strip()
                )
                price_value = float(price_clean)

                products.append({
                    "Store": item.get("source", "Unknown"),
                    "Price (₹)": price_value,
                    "Rating": item.get("rating", "N/A"),
                    "Product Link": item.get("link", "")
                })
            except:
                continue

        df = pd.DataFrame(products)

        if df.empty:
            st.error("Could not extract price data.")
            st.stop()

        # Show Table
        st.subheader("📊 Price Comparison Table")
        st.dataframe(df, use_container_width=True)

        # Lowest Price
        lowest = df.loc[df["Price (₹)"].idxmin()]
        st.success(f"🏆 Lowest Price: ₹{lowest['Price (₹)']} at {lowest['Store']}")

        # Price Chart
        st.subheader("📈 Price Comparison Chart")

        plt.figure()
        plt.bar(df["Store"], df["Price (₹)"])
        plt.xticks(rotation=45)
        plt.ylabel("Price (₹)")
        plt.title("Store vs Price")
        st.pyplot(plt)

        # AI Recommendation Logic
        avg_price = df["Price (₹)"].mean()
        lowest_price = lowest["Price (₹)"]

        price_difference_percent = ((avg_price - lowest_price) / avg_price) * 100

        st.subheader("🤖 AI Recommendation")

        if price_difference_percent > 10:
            st.info("🔥 BUY NOW! This price is significantly lower than average.")
        elif 5 < price_difference_percent <= 10:
            st.info("👍 Good Deal. You can consider buying.")
        else:
            st.warning("⏳ WAIT. Price is close to market average.")

        # Extra Insights
        st.markdown("---")
        st.markdown(f"📅 Last Updated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}")

        # Download Option
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Download Comparison CSV",
            csv,
            file_name="price_comparison.csv",
            mime="text/csv"
        )
