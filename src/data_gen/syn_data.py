"""
creating synthetic victim data:
-> expand df by 'PWGTP' (duplicate by weight)
--------------------------------------
-> build metadata (col override etc)
-> instantiate + fit synthesizer
-> sample N rows
"""
import pandas as pd
from sdv.single_table import GaussianCopulaSynthesizer
from sdv.metadata import Metadata
from src.ingestion.fetch_pums import fetch_pums_data
from dotenv import load_dotenv
import os


def expand_by_weight(df, weight_col='PWGTP'):
    """
    PWGTP ~ scale by which PUMA needs to be multiplied to get the actual spread (PUMAs is only a sample)
    -> take in df
    -> duplicate rows based on the scale vals
    """
    df = df.loc[df.index.repeat(df[weight_col])]
    return df

def generate_synthetic_data(df_sam, wt_col='PWGTP', num_rows=15000, table_name='pums'):
    """
    -> remove weight cols: dont need the syn data to have the trend of weight, unnecessary
    -> make metadata using source df 
    -> create and fit synthesizer to num_rows
    """
    df_expanded = expand_by_weight(df_sam, weight_col=wt_col) # get full data (~670k) using sample data (~30k)
    # remove weight col from both expanded and sample; else metadata and fit will differ
    df_sample = df_sam.drop(columns=wt_col)
    df_expanded.drop(columns=wt_col, inplace=True)
    # this IS the meta :p
    metadata = Metadata.detect_from_dataframe(data=df_sample, table_name=table_name) # maybe save to json?
    # using gaussian copula since data is small
    gc = GaussianCopulaSynthesizer(metadata)
    gc.fit(df_expanded)
    syn_df = gc.sample(num_rows=num_rows)

    return syn_df


if __name__ == "__main__":

    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    key = os.environ.get("CENSUS_API_KEY")

    pumas = ["03101", "03102", "03103", "03104", "03105"]
    df = fetch_pums_data(key, pumas)
    print(df.shape)
    print(df.columns.tolist())
    syn_df = generate_synthetic_data(df) 
    print(syn_df.shape)
    print(syn_df.columns.tolist())
    
