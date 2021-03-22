import io

import pandas as pd
import requests


DATA = "HRDataset_v13.csv"


def transform_local(data_file: str):
    df = pd.read_csv(data_file)
    data_str = io.StringIO()
    df.to_csv(data_str, index=False)
    payload = {"data": data_str.getvalue()}
    resp = requests.post(
        "http://localhost:9000/2015-03-31/functions/function/invocations",
        json=payload
    )
    xf_df = pd.read_csv(io.StringIO(resp.json()["data"]))
    print(xf_df.head())


if __name__ == "__main__":
    transform_local(DATA)
