import pandas as pd
import logging

# Set up logging configuration
logging.basicConfig(filename='community_function.log', 
                    level=logging.INFO, 
                    format='%(asctime)s %(message)s')

def clean_filter(df):
    # Log the start of the function
    logging.info("function call: clean_filter started")

    try:
        required_columns = [
            'Name', 'Pos', 'Team', 'Opp', 'Salary', 'SS Proj', 
            'My Proj', 'My Own', 'dk_25_percentile', 'dk_50_percentile', 
            'dk_75_percentile', 'dk_85_percentile', 'dk_95_percentile', 'dk_99_percentile', 'dk_std'
        ]
        df_filtered = df[required_columns]
        df_filtered = df_filtered[df_filtered['dk_75_percentile'].notna()]
        df_filtered['Salary'] = pd.to_numeric(df_filtered['Salary'], errors='coerce')
        df_filtered = df_filtered.sort_values(by=['Name', 'Salary'])

        if df_filtered['Name'].duplicated().any():
            duplicated_names = df_filtered[df_filtered['Name'].duplicated(keep=False)]

            for name in duplicated_names['Name'].unique():
                name_rows = df_filtered[df_filtered['Name'] == name]
                captain_row = name_rows[name_rows['Salary'] == name_rows['Salary'].max()]
                df_filtered = df_filtered.drop(captain_row.index)

        df_deduped = df_filtered.drop_duplicates(subset='Name', keep='first')
        df_deduped['My Proj'] = df_deduped['My Proj'].fillna(df_deduped['SS Proj'])
        df_deduped = df_deduped.rename(columns={
            'Salary': 'DK$',
            'My Own': 'Roster%',
            'dk_25_percentile': '25th%',
            'dk_50_percentile': '50th%',
            'dk_75_percentile': '75th%',
            'dk_85_percentile': '85th%',
            'dk_95_percentile': '95th%',
            'dk_99_percentile': '99th%',
            'SS Proj': 'proj',
            'My Proj': 'adj_proj',
            'dk_std': 'dk_std'  # Ensure this column remains as is
        })

        df_deduped.columns = df_deduped.columns.str.lower()

        df_deduped = df_deduped[[
            'name', 'pos', 'team', 'opp', 'dk$', 'roster%',
            'proj', 'adj_proj', '25th%', '50th%', 
            '75th%', '85th%', '95th%', '99th%', 'dk_std'
        ]]

        # Remove players who have a zero projection in the '95th%' column
        df_deduped = df_deduped[df_deduped['95th%'] != 0]

        # Sort by 'dk$' in descending order
        df_deduped = df_deduped.sort_values(by='dk$', ascending=False)

        # Log successful execution
        logging.info("function call: clean_filter ran successfully")
        
        return df_deduped

    except Exception as e:
        # Log any error that occurs
        logging.error(f"function call: clean_filter failed due to error - {str(e)}")
        raise

