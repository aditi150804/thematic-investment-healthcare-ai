# AI-Powered Thematic Investment Strategy & Portfolio Construction Tool

## Project Summary

This project develops and backtests a thematic investment strategy focused on the "AI in Healthcare" revolution. It uses Natural Language Processing (NLP) with TensorFlow and data science techniques to analyze alternative data (scientific publications) and identify innovative public companies. The goal is to create a data-driven "Promise Score" to see if it can predict future stock performance against the S&P 500 benchmark.

### Core Investment Themes Analyzed
* **AI in Drug Discovery & Development:** Identifying companies using AI to find novel drug targets and accelerate clinical trials.
* **AI in Diagnostics & Medical Imaging:** Identifying companies developing AI for disease detection and medical image analysis.

---

## Methodology & Project Journey

This project was executed in three main phases, including a significant initial phase of environment debugging which demonstrated deep problem-solving skills.

### 1. Data Acquisition & Environment Setup

* **Initial Challenge:** Overcame a series of complex, persistent environment and library versioning issues. This involved diagnosing conflicts between Conda and venv, solving silent script failures, and debugging esoteric `yfinance` and `pandas` behavior. The final solution required creating a clean, non-Conda virtual environment (`final_env`) and establishing robust coding patterns (like using `python3 -m pip`) to ensure reproducibility.

* **Financial Data:** Downloaded historical daily stock price data for a universe of ~35 selected public companies using the `yfinance` library. A custom script was built to handle and clean unusual data formats returned by the library.

* **Alternative Data (PubMed):** Developed a sophisticated data acquisition script using `BioPython` to query the PubMed database.
    * Implemented a **dual-search strategy**:
        * For pure healthcare/biotech firms, searched by **author affiliation** to find research they directly published.
        * For technology-enabling firms (e.g., NVIDIA, Google), searched by **keyword mentions** in titles/abstracts to find research that utilized their platforms.
    * The search was designed to cast a wide net, collecting all AI-related papers for later, more detailed analysis.

### 2. Feature Engineering & Analysis

This phase was conducted in a Jupyter Notebook to transform raw, unstructured text into quantitative, forward-looking innovation signals.

* **Semantic Relevance Score:** Instead of simple keyword counting, this project used **TensorFlow Hub's Universal Sentence Encoder (USE)**, a state-of-the-art deep learning model.
    * The model converted the abstracts of ~50-100 publications per company into numerical vectors (embeddings).
    * **Cosine similarity** was used to calculate a score representing how close in *meaning* each paper was to our core investment themes.

* **Publication Impact Score:** To measure research quality, journal ranking data was downloaded from **Scimago Journal & Country Rank**. This data was merged with the PubMed data to assign an impact score (`SJR Score`) to each publication.

* **Temporal Momentum Score:** Calculated the year-over-year percentage change in a company's AI-related publication volume. This measures if a company's innovation efforts are accelerating or decelerating.

* **Final Composite "Promise Score":** The three features above (Relevance, Impact, Momentum) were normalized using `scikit-learn`'s `MinMaxScaler` and combined into a final weighted score for each company for each year. This represents the project's ultimate, data-driven view of a company's innovation promise.

### 3. Backtesting & Results

The final phase tested the core hypothesis: "Does a high 'Promise Score' predict future stock returns?"

* **Strategy:** A simple portfolio was simulated. At the start of each year (from 2019 to 2025), the strategy "invested" in an equal-weighted portfolio of the **Top 5** companies based on their Promise Score from the previous year.
* **Performance:** The strategy's historical performance was calculated using the 1-year forward returns and compared against an S&P 500 ETF (SPY) benchmark.

#### **Key Finding:**

The analysis concluded that this simple, Top-5 thematic strategy **underperformed the S&P 500 benchmark** during the test period. The strategy exhibited significantly higher volatility, with sharp dips in 2020 and 2022 but a period of strong outperformance in 2021. This is a realistic and valuable finding, highlighting the high-risk, high-volatility nature of concentrated, innovation-focused thematic investing. The goal of the project—to build a robust framework for testing such a hypothesis—was successfully achieved.

![Backtest Performance Chart](image_1f78de.png) ---

## Tech Stack

* **Language:** Python 3.12
* **Core Libraries:** Pandas, NumPy, Scikit-learn
* **AI / NLP:** TensorFlow, TensorFlow Hub, spaCy, NLTK
* **Data Acquisition:** yfinance, BioPython, Requests
* **Environment:** venv, pip
* **Development:** VS Code, Jupyter Notebook

---

## Future Improvements

* **Incorporate More Data:** Add more alternative data sources like ClinicalTrials.gov, patent databases, and full-text 10-K financial reports.
* **Refine Backtesting:** Implement more sophisticated portfolio construction methods (e.g., risk parity, mean-variance optimization) and include risk management rules (e.g., stop-losses).
* **Build Interactive Dashboard:** Develop a web application using Streamlit or Dash to allow users to explore the data and results interactively.