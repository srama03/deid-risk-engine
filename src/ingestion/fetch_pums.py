import requests
import pandas as pd

def fetch_pums_data(key, pumas, year=2024, state_code=37, get_vars="AGEP,SEX,RAC1P,HISP,PWGTP", const_cols='state'):
  """
  -> pull pums from census using api; current default to NC from acs period 2020-24
  -> drop columns that will be constant (state in this case)
  -> return df of pums
  """
  
  url = f"https://api.census.gov/data/{year}/acs/acs5/pums"
  pumas = ','.join(pumas)
  params = {
    "get":get_vars,
    "for":f"public use microdata area:{pumas}",
    "in": f"state:{state_code}",
    "key": key
  }
  response = requests.get(url, params)
  # check for screw ups
  response.raise_for_status()
  data = response.json()
  pums = pd.DataFrame(data[1:], columns=data[0])
  # drop state
  pums.drop(columns=const_cols, inplace=True)
  # change dtype of the age and wt to int
  pums[["AGEP", "PWGTP"]] = pums[["AGEP", "PWGTP"]].apply(pd.to_numeric)
  return pums