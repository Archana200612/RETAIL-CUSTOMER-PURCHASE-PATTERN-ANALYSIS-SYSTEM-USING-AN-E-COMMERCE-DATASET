import pandas as pd
import numpy as np

def load_and_clean_data(file):
    """
    Loads dataset, handles missing values, removes duplicates, 
    and formats transaction IDs.
    """
    try:
        # Try standard UTF-8 first
        df = pd.read_csv(file)
    except UnicodeDecodeError:
        try:
            # Fallback for files with special characters (like currency symbols)
            file.seek(0) # Reset file pointer for streamlit
            df = pd.read_csv(file, encoding='latin1')
        except Exception as e:
            return pd.DataFrame(), {'error': f"Encoding error: {str(e)}"}
    except Exception as e:
        # Return an empty dataframe and a special error flag in stats
        return pd.DataFrame(), {'error': f"Could not read file: {str(e)}"}
    
    # Clean column names: strip whitespace and handle casing/aliases
    df.columns = df.columns.str.strip()
    
    # Create a mapping for standard names (case-insensitive)
    standard_map = {
        'transaction_id': 'Transaction_ID',
        'transaction': 'Transaction_ID',
        'customer_id': 'Customer_ID',
        'date': 'Date',
        'item': 'Item',
        'product': 'Item',
        'productid': 'Item',
        'product_name': 'Item',
        'category': 'Category',
        'productcategory': 'Category',
        'quantity': 'Quantity',
        'qty': 'Quantity',
        'salesvolume': 'Quantity',
        'price': 'Price',
        'total_spend': 'Total_Spend',
        'total': 'Total_Spend',
        'spend': 'Total_Spend'
    }
    
    # Apply mapping
    new_columns = {}
    for col in df.columns:
        if col.lower() in standard_map:
            new_columns[col] = standard_map[col.lower()]
            
    df.rename(columns=new_columns, inplace=True)
    
    # Calculate Total_Spend if missing but Price and Quantity exist
    if 'Total_Spend' not in df.columns and 'Price' in df.columns and 'Quantity' in df.columns:
        df['Total_Spend'] = df['Price'] * df['Quantity']
    
    original_shape = df.shape
    
    # Clean Missing Values
    df.dropna(inplace=True)
    missing_removed = original_shape[0] - df.shape[0]
    
    # Remove Duplicates
    shape_before_dup = df.shape
    df.drop_duplicates(inplace=True)
    duplicates_removed = shape_before_dup[0] - df.shape[0]
    
    # Ensure proper string formatting
    if 'Transaction_ID' in df.columns:
        df['Transaction_ID'] = df['Transaction_ID'].astype(str).str.strip().str.upper()
    if 'Customer_ID' in df.columns:
        df['Customer_ID'] = df['Customer_ID'].astype(str).str.strip().str.upper()
    if 'Item' in df.columns:
        df['Item'] = df['Item'].astype(str).str.strip().str.title()
    if 'Category' in df.columns:
        df['Category'] = df['Category'].astype(str).str.strip().str.title()
        
    cleaned_shape = df.shape
    
    stats = {
        'original_rows': original_shape[0],
        'missing_removed': missing_removed,
        'duplicates_removed': duplicates_removed,
        'final_rows': cleaned_shape[0]
    }
    
    return df, stats
