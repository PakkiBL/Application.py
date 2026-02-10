'''import streamlit as st
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
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Price Intelligence System", page_icon="🛍", layout="wide")

API_KEY = st.secrets["SERPAPI_KEY"]

st.title("🛍 QuickCart AI – Smart Grocery Deal Finder")
st.markdown("Real-time price comparison with smart buying insights.")

# Sidebar
st.sidebar.header("⚙ Filters")
num_results = st.sidebar.slider("Number of Stores", 3, 10, 5)
min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 0.0)

product_name = st.text_input("🔎 Enter Product Name")

if st.button("Analyze Market"):

    if not product_name:
        st.warning("Please enter a product name.")
        st.stop()

    with st.spinner("Analyzing real-time market data..."):

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

                rating = item.get("rating", 0)
                rating = float(rating) if rating else 0

                if rating >= min_rating:
                    products.append({
                        "Store": item.get("source", "Unknown"),
                        "Price": price_value,
                        "Rating": rating,
                        "Link": item.get("link", ""),
                        "Image": item.get("thumbnail", "")
                    })
            except:
                continue

        df = pd.DataFrame(products)

        if df.empty:
            st.error("No products match your filter criteria.")
            st.stop()

        # Sort by Price
        df = df.sort_values(by="Price")

        # Display first product image
        st.subheader("🖼 Product Preview")
        if df.iloc[0]["Image"]:
            st.image(df.iloc[0]["Image"], width=250)

        st.subheader("📊 Market Price Table")
        st.dataframe(df, use_container_width=True)

        # Metrics Section
        lowest_price = df["Price"].min()
        highest_price = df["Price"].max()
        avg_price = df["Price"].mean()

        col1, col2, col3 = st.columns(3)
        col1.metric("Lowest Price", f"₹{lowest_price}")
        col2.metric("Average Market Price", f"₹{round(avg_price,2)}")
        col3.metric("Highest Price", f"₹{highest_price}")

        # Chart
        st.subheader("📈 Price Distribution")
        st.bar_chart(df.set_index("Store")["Price"])

        # Price difference %
        best_store = df.iloc[0]["Store"]
        percent_saving = ((avg_price - lowest_price) / avg_price) * 100

        st.subheader("🤖 AI Buying Recommendation")

        if percent_saving > 15:
            st.success(f"🔥 STRONG BUY at {best_store}! You save {round(percent_saving,2)}% compared to market average.")
        elif 8 < percent_saving <= 15:
            st.info("👍 Good Deal. Buying now is reasonable.")
        else:
            st.warning("⏳ WAIT. Prices are close to market average.")

        # Business Insight
        st.subheader("📌 Business Insight")
        st.write("""
        - Price variance indicates market competition level.
        - Higher variance = opportunity for smart purchasing.
        - Low variance = stable pricing market.
        """)

        st.caption(f"Last Updated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}")

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Download Market Data", csv, "market_analysis.csv", "text/csv")

'''

import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="QuickCart AI",
    page_icon="🛍",
    layout="wide"
)

API_KEY = st.secrets.get("SERPAPI_KEY")

if not API_KEY:
    st.error("SERPAPI_KEY not found. Please add it in Streamlit Cloud → Manage App → Secrets.")
    st.stop()


st.title("🛍 QuickCart AI – Smart Grocery Deal Finder")
st.markdown("Real-time price comparison with smart buying insights.")

st.sidebar.header("⚙ Filters")
num_results = st.sidebar.slider("Number of Stores", 3, 10, 5)
min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 0.0)

product_name = st.text_input("🔎 Enter Product Name")

if st.button("Analyze Market"):

    if not product_name:
        st.warning("Please enter a product name.")
        st.stop()

    with st.spinner("Analyzing real-time market data..."):

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

                
                rating = item.get("rating", 0)
                rating = float(rating) if rating else 0

                if rating >= min_rating:

                   
                    product_link = item.get("product_link") or item.get("link") or ""

                    products.append({
                        "Store": item.get("source", "Unknown"),
                        "Price (₹)": price_value,
                        "Rating": rating,
                        "Product Link": product_link,
                        "Image": item.get("thumbnail", "")
                    })

            except:
                continue

        df = pd.DataFrame(products)

        if df.empty:
            st.error("No products match your filter criteria.")
            st.stop()

        # Remove duplicate stores
        df = df.drop_duplicates(subset=["Store"])
        df = df.sort_values(by="Price (₹)").reset_index(drop=True)

        df.insert(0, "Rank", df.index + 1)

        st.subheader("🖼 Product Preview")
        if df.iloc[0]["Image"]:
            st.image(df.iloc[0]["Image"], width=250)

        st.subheader("📊 Market Price Table")

        display_df = df.drop(columns=["Image"])

        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                "Product Link": st.column_config.LinkColumn(
                    "Product Link",
                    display_text="Open Product"
                )
            }
        )

        lowest_price = df["Price (₹)"].min()
        highest_price = df["Price (₹)"].max()
        avg_price = df["Price (₹)"].mean()

        col1, col2, col3 = st.columns(3)
        col1.metric("Lowest Price", f"₹{lowest_price}")
        col2.metric("Average Market Price", f"₹{round(avg_price, 2)}")
        col3.metric("Highest Price", f"₹{highest_price}")

        st.subheader("📈 Price Distribution")
        st.bar_chart(df.set_index("Store")["Price (₹)"])

        best_store = df.iloc[0]["Store"]
        percent_saving = ((avg_price - lowest_price) / avg_price) * 100

        st.subheader("🤖 AI Buying Recommendation")

        if percent_saving > 15:
            st.success(
                f"🔥 STRONG BUY at {best_store}! "
                f"You save {round(percent_saving, 2)}% compared to market average."
            )
        elif 8 < percent_saving <= 15:
            st.info("👍 Good Deal. Buying now is reasonable.")
        else:
            st.warning("⏳ WAIT. Prices are close to market average.")

        st.subheader("📌 Business Insight")
        st.write("""
        - Price variance indicates market competition level.
        - Higher variance = opportunity for smart purchasing.
        - Low variance = stable pricing market.
        """)

        st.caption(
            f"Last Updated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}"
        )

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇ Download Market Data",
            csv,
            "market_analysis.csv",
            "text/csv"
        )
