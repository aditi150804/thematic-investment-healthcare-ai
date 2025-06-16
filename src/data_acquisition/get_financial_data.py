import yfinance as yf
import pandas as pd
import os
import time
from datetime import datetime
from pathlib import Path

# --- Dynamic Path Configuration ---
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

# --- Configuration ---
# Your full list of 35 tickers
TICKER_LIST = [
    # AI-Native Drug Discovery (6 Companies)
    'RXRX',     # Recursion Pharmaceuticals
    'RLAY',     # Relay Therapeutics
    'SDGR',     # Schrodinger
    'ABCL',     # AbCellera Biologics
    'ABSI',     # Absci
    'CERT',     # Certara

    # AI-Native Diagnostics (7 Companies)
    'TEM',      # Tempus AI
    'GH',       # Guardant Health
    'IRTC',     # iRhythm Technologies
    'BFLY',     # Butterfly Network
    'WGS',      # GeneDx
    'NEO',      # NeoGenomics Laboratories
    '328130.KQ',# Lunit Co. Ltd. (Note: KOSDAQ ticker, may require special handling)

    # Large Pharma/Biotech with AI Initiatives (11 Companies)
    'PFE',      # Pfizer
    'NVS',      # Novartis AG
    'RHHBY',    # Roche Holding AG (ADR)
    'MRK',      # Merck & Co.
    'AZN',      # AstraZeneca PLC
    'GSK',      # GSK plc
    'JNJ',      # Johnson & Johnson
    'SNY',      # Sanofi
    'BAYRY',    # Bayer AG (ADR)
    'AMGN',     # Amgen
    'GILD',     # Gilead Sciences

    # Tech Companies with Healthcare AI Platforms (6 Companies)
    'NVDA',     # NVIDIA Corp.
    'GOOGL',    # Alphabet Inc. (Google)
    'MSFT',     # Microsoft Corp.
    'AMZN',      # Amazon.com, Inc.
    'IBM',       # IBM Corp.
    'INTC'      # Intel Corp.
]

START_DATE = "2015-01-01"
END_DATE = datetime.now().strftime('%Y-%m-%d')

OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "financial_data"

# --- Main Script ---
def download_all_stock_data(tickers, start, end, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory '{output_dir}' is ready.", flush=True)

    failed_tickers = []
    for ticker in tickers:
        filepath = os.path.join(output_dir, f"{ticker}.csv")
        if os.path.exists(filepath):
            print(f"Data for {ticker} already exists. Skipping.", flush=True)
            continue

        print(f"Downloading data for {ticker}...", flush=True)
        try:
            # Setting auto_adjust=True and actions=False is a more modern yfinance approach
            stock_data = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True, actions=False)
            
            if stock_data.empty:
                print(f"  -> No data found for {ticker}.", flush=True)
                failed_tickers.append(ticker)
                continue
            
            # --- THE FINAL, BRUTE-FORCE FIX for TUPLE COLUMNS ---
            # This directly addresses the [('Close', 'IBM')] format
            if len(stock_data.columns) > 0 and isinstance(stock_data.columns[0], tuple):
                print(f"  -> Detected tuple-based columns. Flattening...")
                # Replace the tuple columns with just the first element of each tuple
                stock_data.columns = [col[0] for col in stock_data.columns]
            # --- END OF FINAL FIX ---

            # Turn the 'Date' index into a real column
            stock_data.reset_index(inplace=True)

            # yfinance with auto_adjust=True doesn't have 'Adj Close', the 'Close' IS the adjusted close.
            # We will create the 'Adj Close' column ourselves to match our required format.
            if 'Adj Close' not in stock_data.columns and 'Close' in stock_data.columns:
                stock_data['Adj Close'] = stock_data['Close']

            required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
            
            if not all(col in stock_data.columns for col in required_columns):
                print(f"  -> Downloaded data for {ticker} is missing required columns AFTER processing. Skipping.")
                print(f"     Found columns: {stock_data.columns.tolist()}")
                failed_tickers.append(ticker)
                continue
            
            clean_data = stock_data[required_columns]
            clean_data.to_csv(filepath, index=False)

            print(f"  -> Successfully saved clean data for {ticker}.")
            time.sleep(1)
        except Exception as e:
            print(f"  -> Could not download data for {ticker}. Error: {e}", flush=True)
            failed_tickers.append(ticker)
            continue
    
    if failed_tickers:
        print(f"\nCould not download data for: {failed_tickers}", flush=True)
    else:
        print("\nAll tickers downloaded successfully!", flush=True)

if __name__ == "__main__":
    print("--- Starting Financial Data Acquisition ---", flush=True)
    download_all_stock_data(TICKER_LIST, START_DATE, END_DATE, OUTPUT_DIR)
    print("--- Script Finished ---", flush=True)