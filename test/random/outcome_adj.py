import logging

def adjust_percentiles(df, adjustment_factor=1.0):
    """
    Adjust the percentile values if necessary by comparing 'proj' and 'adj_proj'.
    This function modifies the '25th%', '50th%', '75th%', '85th%', '95th%', and '99th%' columns.
    """
    logging.info("function call: adjust_percentiles started")

    try:
        adjustment_needed = df[df['proj'] != df['adj_proj']]
        
        for idx, row in adjustment_needed.iterrows():
            shift_factor = (row['adj_proj'] / row['proj']) * adjustment_factor

            df.at[idx, '25th%'] = max(0, row['25th%'] * shift_factor)
            df.at[idx, '50th%'] = max(0, row['50th%'] * shift_factor)
            df.at[idx, '75th%'] = row['75th%'] * shift_factor
            df.at[idx, '85th%'] = row['85th%'] * shift_factor
            df.at[idx, '95th%'] = row['95th%'] * shift_factor
            df.at[idx, '99th%'] = row['99th%'] * shift_factor

        logging.info("Percentiles adjusted successfully")
        return df

    except Exception as e:
        logging.error(f"function call: adjust_percentiles failed due to error - {str(e)}")
        raise

