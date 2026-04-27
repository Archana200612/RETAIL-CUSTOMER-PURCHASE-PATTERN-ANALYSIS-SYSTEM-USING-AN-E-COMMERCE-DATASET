import streamlit as st
import pandas as pd
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

from data_handler import load_and_clean_data
from analytics import get_summary_statistics, get_top_products, get_top_categories, plot_top_products, get_correlation_matrix, plot_correlation_heatmap
from mba import perform_mba, plot_rules_bubble, get_recommendations

st.set_page_config(page_title="Retail Purchase Pattern Analyzer", layout="wide", page_icon="🛒")

st.title("🛒 Retail Customer Purchase Pattern Analysis System")
st.markdown("Analyze e-commerce transactions to identify popular products, understand purchase correlations, and uncover market basket association rules.")

# Sidebar - File Upload and Settings
st.sidebar.header("📁 Data Input")
uploaded_file = st.sidebar.file_uploader("Upload Transaction Dataset (CSV)", type="csv")

if not uploaded_file:
    st.info("Please upload a dataset from the sidebar to begin analysis. If you don't have one, run `python generate_dataset.py` locally to create a test dataset (ecommerce_dataset.csv) and upload it.")
    st.stop()

# --- 1. DATA HANDLING ---
with st.spinner("Loading and Cleaning Data..."):
    df, stats = load_and_clean_data(uploaded_file)

if 'error' in stats:
    st.error(stats['error'])
    st.info("The file appears to be empty or corrupted. Please try uploading a different CSV or run `python generate_dataset.py` to create a new one.")
    st.stop()
    
st.success("Data successfully loaded and cleaned!")

# Validate Columns
required_columns = ['Item', 'Quantity']
missing_cols = [col for col in required_columns if col not in df.columns]
if missing_cols:
    st.error(f"The uploaded dataset is missing the following required columns: **{', '.join(missing_cols)}**")
    st.write("### 🔍 Debug: Detected Columns")
    st.write(list(df.columns))
    st.info("Please ensure your CSV has headers like: ProductID/Item and SalesVolume/Quantity")
    st.stop()

# Handle missing Transaction_ID gracefully
is_dummy_data = False
if 'Transaction_ID' not in df.columns:
    st.warning("⚠️ **Note:** Your dataset is missing a **Transaction_ID**. I have generated dummy IDs so you can see the Descriptive Analytics, but **Market Basket Analysis** (identifying items bought together) will not be meaningful.")
    df['Transaction_ID'] = [f"DUMMY_{i}" for i in range(len(df))]
    is_dummy_data = True

with st.expander("Show Data Cleaning Statistics"):
    st.write(f"- Original Rows: **{stats['original_rows']}**")
    st.write(f"- Missing Values Removed: **{stats['missing_removed']}**")
    st.write(f"- Duplicates Removed: **{stats['duplicates_removed']}**")
    st.write(f"- Final Usable Rows: **{stats['final_rows']}**")

st.markdown("### 📋 Sample Data")
st.dataframe(df.head())

# --- 2. DESCRIPTIVE ANALYTICS ---
st.markdown("---")
st.header("📊 Descriptive Analytics")

col1, col2, col3, col4 = st.columns(4)
summary = get_summary_statistics(df)
col1.metric("Total Transactions", summary["Total Transactions"])
col2.metric("Unique Customers", summary["Unique Customers"])
col3.metric("Total Items Sold", summary["Total Items Sold"])
if "Total Revenue ($)" in summary and summary["Total Revenue ($)"] > 0:
    col4.metric("Total Revenue", f"${summary['Total Revenue ($)']:.2f}")

st.markdown("#### Frequency Tables")
col_t1, col_t2 = st.columns(2)
with col_t1:
    st.write("**Top 10 Most Purchased Products**")
    st.dataframe(get_top_products(df, 10))
with col_t2:
    st.write("**Top Categories**")
    st.dataframe(get_top_categories(df, 10))
    
st.markdown("#### Visualizations")
st.altair_chart(plot_top_products(df, 10), use_container_width=True)

# --- 3. CORRELATION ANALYSIS ---
st.markdown("---")
st.header("🔗 Product Correlation Analysis")
st.markdown("Identifies strong pairwise relationships between products.")

if is_dummy_data:
    st.info("Correlation Analysis is skipped because each item in your dataset is on a separate transaction ID.")
else:
    with st.spinner("Calculating Correlation Matrix..."):
        corr_data = get_correlation_matrix(df, top_n=20)
        st.altair_chart(plot_correlation_heatmap(corr_data), use_container_width=True)

# --- 4. MARKET BASKET ANALYSIS ---
st.markdown("---")
st.header("🧺 Market Basket Analysis (Apriori)")
st.markdown("Identify itemsets that are frequently bought together and generate association rules ('If a customer buys X, they are likely to buy Y').")

st.sidebar.header("MBA Settings")
min_support = st.sidebar.slider("Minimum Support", min_value=0.001, max_value=0.1, value=0.01, step=0.005)
# Initialize MBA variables
rules = pd.DataFrame()
frequent_itemsets = pd.DataFrame()

if is_dummy_data:
    st.info("Market Basket Analysis is disabled because your dataset does not contain transaction-level groupings.")
else:
    with st.spinner("Running Apriori Algorithm..."):
        frequent_itemsets, rules = perform_mba(df, min_support=min_support, min_confidence=min_confidence)

    if rules.empty:
        st.warning("No rules found with the specified Support and Confidence thresholds. Try lowering them.")
    else:
        st.success(f"Generated {len(rules)} association rules!")
        
        st.markdown("#### Association Rules DataFrame")
        # Formatting for display
        display_rules = rules.copy()
        display_rules['antecedents'] = display_rules['antecedents'].apply(lambda x: ', '.join(list(x)))
        display_rules['consequents'] = display_rules['consequents'].apply(lambda x: ', '.join(list(x)))
        st.dataframe(display_rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']].head(50))
        
        st.markdown("#### Rules Visualization")
        bubble_chart = plot_rules_bubble(rules)
        if bubble_chart: 
            st.altair_chart(bubble_chart, use_container_width=True)

# --- 5. RECOMMENDATION SYSTEM BONUS ---
st.markdown("---")
st.header("💡 Recommendation System")
st.markdown("Select a product to get top 3 recommendations based on the generated Association Rules.")

all_products = df['Item'].unique()
selected_product = st.selectbox("Select a Product to Base Recommendations On:", sorted(all_products))

if st.button("Get Recommendations"):
    if rules.empty:
         st.error("Cannot make recommendations: No rules were generated.")
    else:
        recs = get_recommendations(rules, selected_product, top_n=3)
        if recs:
            st.success(f"Customers who bought **{selected_product}** also bought:")
            for idx, rec in enumerate(recs):
                st.write(f"{idx+1}. {rec}")
        else:
            st.info(f"No strong recommendations found for **{selected_product}** with the current thresholds.")

st.markdown("---")
st.caption("Developed as part of Data Analysis Mini Project")
