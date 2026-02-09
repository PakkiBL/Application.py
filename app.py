import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Smart Shopping Deal Comparator", page_icon="🛍", layout="wide")

# Get API key safely
API_KEY = st.secrets["SERPAPI_KEY"]

st.title("🛍 Smart Shopping Deal Comparator")
st.markdown("Compare product prices across stores and get smart buy recommendations.")

st.sidebar.header("⚙ Filters")
num_results = st.sidebar.slider("Number of stores", 3, 10, 5)

product_name = st.text_input("🔎 Enter Product Name")

if st.button("Compare Prices"):

    if not product_name:
        st.warning("Please enter a product name.")
        st.stop()

    with st.spinner("Fetching latest prices..."):

        url = "https://serpapi.com/search.json"

        params = {
            "engine": "google_shopping",
            "q": product_name,
            "api_key": API_KEY,
            "gl": "in",
            "hl": "en"
        }

        response = requests.get(url, params=params)
        data = response.json()

        results = data.get("shopping_results", [])

        if not results:
            st.error("No results found.")
            st.stop()

        products = []

        for item in results[:num_results]:
            try:
                price_text = item.get("price", "0")
                price_clean = price_text.replace("₹", "").replace(",", "").strip()
                price_value = float(price_clean)

                products.append({
                    "Store": item.get("source", "Unknown"),
                    "Price": price_value,
                    "Rating": item.get("rating", "N/A"),
                    "Link": item.get("link", "")
                })
            except:
                continue

        df = pd.DataFrame(products)

        if df.empty:
            st.error("Could not extract price data.")
            st.stop()

        st.subheader("📊 Price Comparison Table")
        st.dataframe(df, use_container_width=True)

        # Lowest price
        lowest = df.loc[df["Price"].idxmin()]
        st.success(f"🏆 Lowest Price: ₹{lowest['Price']} at {lowest['Store']}")

        # Built-in Streamlit chart (no matplotlib)
        st.subheader("📈 Price Comparison Chart")
        st.bar_chart(df.set_index("Store")["Price"])

        # Recommendation logic
        avg_price = df["Price"].mean()
        lowest_price = lowest["Price"]

        percent_diff = ((avg_price - lowest_price) / avg_price) * 100

        st.subheader("🤖 AI Recommendation")

        if percent_diff > 10:
            st.success("🔥 BUY NOW! This is a great deal.")
        elif 5 < percent_diff <= 10:
            st.info("👍 Good deal. You can consider buying.")
        else:
            st.warning("⏳ WAIT. Price is close to market average.")

        st.markdown("---")
        st.caption(f"Last Updated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}")

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Download Comparison CSV",
            csv,
            "price_comparison.csv",
            "text/csv"
        )
