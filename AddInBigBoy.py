#AddInBigBoy: for every routeframeid in combined, replace the latitude, longitude, 
#postcode and address, with the matching entry in bigboy

import pandas as pd

def update_location_data(combo_df, bigboy_df):
	
    # Merge the DataFrames on the 'routeframeID' column
    merged_df = combo_df.merge(
        bigboy_df[['routeFrameID', 'address1', 'address2', 'latitude', 'longitude', 'postCode']], 
        on='routeFrameID', 
        how='left', 
        suffixes=('', '_bigboy')
    )

    # Update location data in Combo with values from BigBoy
    location_columns = ['address1', 'address2', 'latitude', 'longitude', 'postCode']
    for col in location_columns:
        merged_df[col] = merged_df[col + '_bigboy'].combine_first(merged_df[col])

    # Drop the temporary columns created from BigBoy
    merged_df = merged_df[combo_df.columns]  # Keep only the original Combo columns

    return merged_df

# Example usage (uncomment to use in a separate script):
