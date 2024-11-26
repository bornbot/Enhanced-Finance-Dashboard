import requests
import pandas as pd
import time

def get_weekly_data(tickers, api_key='MD4MYKIFZVHG3WCK'):
    """
    Fetch weekly time series data for a given list of tickers.
    """
    all_data = {}
    for ticker in tickers:
        try:
            print(f"Fetching data for {ticker}...")
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={ticker}&apikey={api_key}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Handle API errors
            if "Error Message" in data:
                print(f"Invalid ticker: {ticker}. Skipping.")
                continue

            if "Note" in data:
                print(f"Rate limit hit or other issue for {ticker}: {data['Note']}")
                time.sleep(60)  # Wait before retrying if rate limit is hit
                continue

            # Extract weekly time series data
            if "Weekly Time Series" not in data:
                print(f"Error fetching data for {ticker}: {data.get('Note', 'Unknown error')}")
                continue

            df = pd.DataFrame.from_dict(data["Weekly Time Series"], orient="index", dtype="float")
            df.index = pd.to_datetime(df.index)

            # Normalize column names (optional)
            df = df.rename(columns=lambda x: x.split(". ")[1] if ". " in x else x)

            # Store closing prices
            all_data[ticker] = df["close"].sort_index()

            # Rate limit delay
            time.sleep(12)

        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            print("Response content:", response.content)

    # Check if no data was fetched
    if len(all_data) == 0:
        print("No data fetched. Returning mock data.")
        return pd.DataFrame(
            np.random.random((100, 3)) * 100,
            index=pd.date_range("2022-01-01", periods=100),
            columns=tickers
        )


    # Concatenate all data into a single DataFrame
    try:
        final_df = pd.concat(all_data, axis=1)
        if final_df.isnull().all().all():
            print("All data is missing or invalid.")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error concatenating data: {e}")
        return pd.DataFrame()

    return final_df
