import pandas as pd
import re

def rename_columns(data:pd.DataFrame) -> pd.DataFrame:
    cols = data.columns
    # use regext to change camel case to snake case
    # pattern = re.compile(r'(?<!^)(?=[A-Z])')
    pattern = re.compile(r'\s')
    new_cols = [pattern.sub('_', c).lower() for c in cols]
    print(f"the new columns names are {new_cols}")
    # rename in batch
    d = dict(zip(cols, new_cols))
    data = data.rename(columns=d)
    return data

def unpack_fields(data: list) -> str:
    
    fields_str = "-".join([d["value"] for d in data if d["value"] != None])

    return fields_str