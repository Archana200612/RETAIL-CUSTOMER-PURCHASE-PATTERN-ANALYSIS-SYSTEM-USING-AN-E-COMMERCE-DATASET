import pandas as pd
import altair as alt

def get_summary_statistics(df):
    """
    Returns general summary stats like total revenue, unique customers, etc.
    """
    stats = {
        'Total Revenue ($)': float(df['Total_Spend'].sum()) if 'Total_Spend' in df.columns else 0,
        'Total Transactions': df['Transaction_ID'].nunique() if 'Transaction_ID' in df.columns else len(df),
        'Unique Customers': df['Customer_ID'].nunique() if 'Customer_ID' in df.columns else 0,
        'Total Items Sold': int(df['Quantity'].sum()) if 'Quantity' in df.columns else 0
    }
    return stats

def get_top_products(df, n=10):
    if 'Item' not in df.columns:
        return pd.DataFrame(columns=['Product', 'Quantity'])
    
    counts = df['Item'].value_counts().head(n).reset_index()
    # Handle different pandas versions (Pandas 2.0+ uses 'count', older uses Series name)
    if 'count' in counts.columns:
        return counts.rename(columns={'Item': 'Product', 'count': 'Quantity'})
    else:
        return counts.rename(columns={'index': 'Product', 'Item': 'Quantity'})

def get_top_categories(df, n=10):
    if 'Category' not in df.columns:
        return pd.DataFrame(columns=['Category', 'Frequency'])
        
    counts = df['Category'].value_counts().head(n).reset_index()
    if 'count' in counts.columns:
        return counts.rename(columns={'Category': 'Category', 'count': 'Frequency'})
    else:
        return counts.rename(columns={'index': 'Category', 'Category': 'Frequency'})

def plot_top_products(df, n=10):
    top_products = get_top_products(df, n)
    chart = alt.Chart(top_products).mark_bar().encode(
        x=alt.X('Quantity:Q', title='Number of Purchases'),
        y=alt.Y('Product:N', sort='-x', title='Product Name'),
        color=alt.Color('Quantity:Q', scale=alt.Scale(scheme='viridis')),
        tooltip=['Product', 'Quantity']
    ).properties(
        title=f'Top {n} Most Purchased Products',
        width=600,
        height=400
    ).interactive()
    return chart

def get_correlation_matrix(df, top_n=20):
    """
    Pivot data to see correlation between products.
    Limited to top_n items to prevent performance issues.
    """
    # Filter for top N items only to keep matrix manageable
    top_items = df['Item'].value_counts().head(top_n).index
    df_filtered = df[df['Item'].isin(top_items)]
    
    if df_filtered.empty:
        return pd.DataFrame(columns=['Product 1', 'Product 2', 'Correlation'])

    # Grouping data into a basket format
    basket = df_filtered.groupby(['Transaction_ID', 'Item'])['Quantity'].sum().unstack().reset_index().fillna(0)
    basket.set_index('Transaction_ID', inplace=True)
    
    # Convert quantities to 1 (bought) or 0 (not bought)
    basket_sets = basket.map(lambda x: 1 if x > 0 else 0)
    
    corr_matrix = basket_sets.corr().reset_index().melt(id_vars='index')
    corr_matrix.columns = ['Product 1', 'Product 2', 'Correlation']
    return corr_matrix

def plot_correlation_heatmap(corr_data):
    chart = alt.Chart(corr_data).mark_rect().encode(
        x='Product 1:N',
        y='Product 2:N',
        color=alt.Color('Correlation:Q', scale=alt.Scale(scheme='coolwarm', domain=[-1, 1])),
        tooltip=['Product 1', 'Product 2', 'Correlation']
    ).properties(
        title="Product Purchase Correlation Heatmap",
        width=600,
        height=600
    )
    return chart
