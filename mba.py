import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
import altair as alt

def encode_units(x):
    if x <= 0:
        return 0
    if x >= 1:
        return 1

def perform_mba(df, min_support=0.01, min_confidence=0.1):
    """
    Performs Apriori and Association Rules generation.
    Returns frequent itemsets and rules dataframe.
    """
    # Grouping into baskets
    basket = (df.groupby(['Transaction_ID', 'Item'])['Quantity']
              .sum().unstack().reset_index().fillna(0)
              .set_index('Transaction_ID'))
    
    basket_sets = basket.map(encode_units)
    
    # Apply Apriori
    frequent_itemsets = apriori(basket_sets, min_support=min_support, use_colnames=True)
    
    if frequent_itemsets.empty:
        return frequent_itemsets, pd.DataFrame()
        
    # Generate Rules
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
    
    # Sorting by lift
    if not rules.empty:
        rules = rules.sort_values('lift', ascending=False)
        
    return frequent_itemsets, rules

def plot_rules_bubble(rules, max_rules=50):
    """
    Bubble chart of association rules using Altair.
    """
    if rules.empty:
        return None
        
    display_rules = rules.head(max_rules).copy()
    display_rules['antecedents_str'] = display_rules['antecedents'].apply(lambda x: ', '.join(list(x)))
    display_rules['consequents_str'] = display_rules['consequents'].apply(lambda x: ', '.join(list(x)))
    display_rules['rule'] = display_rules['antecedents_str'] + " -> " + display_rules['consequents_str']

    chart = alt.Chart(display_rules).mark_circle().encode(
        x=alt.X('support:Q', title='Support'),
        y=alt.Y('confidence:Q', title='Confidence'),
        size=alt.Size('lift:Q', title='Lift'),
        color=alt.Color('lift:Q', scale=alt.Scale(scheme='viridis')),
        tooltip=['rule', 'support', 'confidence', 'lift']
    ).properties(
        title='Association Rules: Support vs Confidence (Bubble size = Lift)',
        width=600,
        height=400
    ).interactive()
    
    return chart

def get_recommendations(rules, product, top_n=3):
    """
    Recommends products based on a selected product.
    looks for the product in the antecedents.
    """
    if rules.empty:
        return []
        
    # Filtering rules where the product is in antecedents
    recommendations = []
    seen = set()
    for idx, row in rules.iterrows():
        if product in row['antecedents']:
            for con in row['consequents']:
                if con not in seen and con != product:
                    recommendations.append((con, row['lift']))
                    seen.add(con)
                    
    # Sort by lift score and return top n
    recommendations.sort(key=lambda x: x[1], reverse=True)
    return [rec[0] for rec in recommendations[:top_n]]
