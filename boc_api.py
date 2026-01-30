import pandas as pd
import requests


def get_boc_data(series_codes, start_date=None, end_date=None):
    """
    Description
    """
    if isinstance(series_codes, list):
        series = ",".join(series_codes)
    else:
        series = series_codes

    url = f"https://www.bankofcanada.ca/valet/observations/{series}/json"

    params = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    df = pd.DataFrame(data["observations"])

    df["date"] = pd.to_datetime(df["d"])
    series_list = series.split(",") if "," in series else [series]
    for s in series_list:
        if s in df.columns:
            df[s] = df[s].apply(
                lambda x: float(x["v"]) if isinstance(x, dict) and x.get("v") else None
            )

    cols = ["date"] + series_list
    df = df[cols]

    return df


df = get_boc_data(
    ["IEXE0124", "V122530", "V122531", "V122538"], start_date="2010-01-01"
)
print(df.head(30))
print(f"Start date: {df['date'].min()}")
print(f"End date: {df['date'].max()}")


# 'IEXE0124' -> the Policy Rate
# 'V80691211' -> 5Y Bond
# 'V80691311' -> 10Y Bond
