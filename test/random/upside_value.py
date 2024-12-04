def upside_value(df):
    # Ensure 'dk$' column exists and avoid division by zero
    if 'dk$' not in df.columns or df['dk$'].isnull().all():
        raise ValueError("Column 'dk$' is missing or contains no valid values.")
    
    # Replace zeros in 'dk$' to avoid division errors
    df['dk$'].replace(0, float('nan'), inplace=True)

    # Replace 0 values in percentiles with small non-zero values to avoid unrealistic projections
    df['25%'].replace(0, 0.01, inplace=True)
    df['50%'].replace(0, 0.02, inplace=True)
    df['75%'].replace(0, 0.03, inplace=True)
    df['85%'].replace(0, 0.04, inplace=True)
    df['95%'].replace(0, 0.05, inplace=True)
    df['99%'].replace(0, 0.06, inplace=True)
    
    # Calculate the points-per-dollar values and multiply by 1000
    df['25th_value'] = (df['25%'] / df['dk$']) * 1000
    df['50th_value'] = (df['50%'] / df['dk$']) * 1000
    df['adj_proj_value'] = (df['adj_proj'] / df['dk$']) * 1000
    df['75th_value'] = (df['75%'] / df['dk$']) * 1000
    df['85th_value'] = (df['85%'] / df['dk$']) * 1000
    df['95th_value'] = (df['95%'] / df['dk$']) * 1000
    df['99th_value'] = (df['99%'] / df['dk$']) * 1000

    # Define the desired order of the columns
    column_order = [
        '25th_value', '50th_value', 'adj_proj_value', 
        '75th_value', '85th_value', '95th_value', '99th_value'
    ]
    
    # Ensure columns are present in the dataframe before reordering
    existing_columns = [col for col in column_order if col in df.columns]
    
    # Reorder the DataFrame to reflect the desired column order
    df = df[existing_columns + [col for col in df.columns if col not in column_order]]
    
    return df

