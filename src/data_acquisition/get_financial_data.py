import yfinance as yf
import pandas as pd
import os
import time
from datetime import datetime
from pathlib import Path

# --- Configuration ---
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
    'IBM',      # IBM Corp.
    'INTC'      # Intel Corp.
]

START_DATE = "2015-01-01"
END_DATE = datetime.now().strftime('%Y-%m-%d')

# Define the relative path for the output directory
RELATIVE_OUTPUT_DIR = "../../data/raw/financial_data"

# --- Main Script ---
def download_all_stock_data(tickers, start, end, output_dir):
    """
    Downloads historical stock data for a list of tickers from Yahoo Finance
    and saves each to a separate CSV file.
    """
    os.makedirs(output_dir, exist_ok=True)
    print(f"-> Data will be saved in: {output_dir}\n", flush=True)
    
    failed_tickers = []

    for ticker in tickers:
        filepath = os.path.join(output_dir, f"{ticker}.csv")
        
        if os.path.exists(filepath):
            print(f"Data for {ticker} already exists. Skipping.", flush=True)
            continue

        print(f"Downloading data for {ticker}...", flush=True)
        try:
            stock_data = yf.download(ticker, start=start, end=end, progress=False)
            
            if stock_data.empty:
                print(f"  -> No data found for {ticker}.", flush=True)
                failed_tickers.append(ticker)
                continue

            stock_data.to_csv(filepath)
            print(f"  -> Successfully saved data for {ticker}.", flush=True)
            time.sleep(1)

        except Exception as e:
            print(f"  -> Could not download data for {ticker}. Error: {e}", flush=True)
            failed_tickers.append(ticker)
            continue
    
    if failed_tickers:
        print("\n--- Download Summary ---", flush=True)
        print(f"Could not download data for: {failed_tickers}", flush=True)
    else:
        print("\n--- Download Summary ---", flush=True)
        print("All tickers downloaded successfully!", flush=True)

if __name__ == "__main__":
    # --- NEW DEBUGGING BLOCK ---
    print("--- Starting Sanity Checks ---")
    
    # 1. Print the Current Working Directory (where the script THINKS it's running from)
    current_working_directory = os.getcwd()
    print(f"Current Working Directory (os.getcwd()): {current_working_directory}")
    
    # 2. Get the absolute path of the script file itself
    script_path = Path(__file__).resolve()
    print(f"Script's Absolute Path (__file__):      {script_path}")
    
    # 3. Calculate the absolute path where the data SHOULD be saved
    # This combines the script's location with the relative path
    output_dir_absolute = (script_path.parent / RELATIVE_OUTPUT_DIR).resolve()
    print(f"Calculated Absolute Output Path:       {output_dir_absolute}")
    
    print("--- Starting Data Download ---\n", flush=True)
    
    # We now pass the absolute path to the function to be 100% sure
    download_all_stock_data(TICKER_LIST, START_DATE, END_DATE, output_dir_absolute)
    
    print("--- Script Finished ---", flush=True)