# Financial Market Backtesting Database Engine

This repository contains the infrastructure setup, data ingestion pipeline, and baseline performance test for a high-throughput relational database engine designed for financial time-series backtesting and portfolio optimization.

---

## 📁 Repository File Structure

```text
FinancialDatabaseProject/
├── propose.py           # Core Python pipeline script (DB creation, ETL, baseline benchmark)
├── stock_exchange.db    # SQLite database file generated automatically on runtime
├── README.md            # Comprehensive documentation and execution guide
└── .gitignore           # Ignores generated database binaries and environment artifacts
```

---

## 📊 Data Source & Hyperlink

* **Source:** [Yahoo Finance API](https://finance.yahoo.com/) (retrieved via the [`yfinance`](https://pypi.org/project/yfinance/) open-source Python wrapper).
* **Dataset Scope:** Historical daily Open-High-Low-Close-Volume (OHLCV) market price bars from **2025-01-01 to 2026-01-01** for 5 major market equities:
  * `AAPL` (Apple Inc.)
  * `MSFT` (Microsoft Corp.)
  * `NVDA` (NVIDIA Corp.)
  * `AMZN` (Amazon.com Inc.)
  * `GOOGL` (Alphabet Inc.)

---

## 🛠️ Database Schema & Relational Design

The system implements a **3rd Normal Form (3NF)** relational database schema in **SQLite** consisting of two main entities connected by foreign key relationships:

```
+------------------------------------+        +-----------------------------------------+
|             companies              |        |              stock_prices               |
|            (Dimension)             |        |                 (Fact)                  |
+------------------------------------+        +-----------------------------------------+
| PK  ticker       TEXT              |<-------| FK  ticker       TEXT                   |
|     company_name TEXT NOT NULL     |   1:N  | PK  id           INTEGER AUTOINCREMENT     |
|     sector       TEXT              |        |     price_date   DATE NOT NULL             |
+------------------------------------+        |     close_price  REAL NOT NULL             |
                                              |     volume       INTEGER                   |
                                              |     UNIQUE(ticker, price_date)          |
                                              +-----------------------------------------+
```

### Constraints & Integrity Rules
1. **Primary Keys:** `companies.ticker` acts as the primary key for corporate metadata. `stock_prices.id` serves as a auto-incrementing unique surrogate key.
2. **Foreign Key Integrity:** `stock_prices.ticker` references `companies.ticker`, preventing orphaned price ticks.
3. **Unique Composite Constraint:** `UNIQUE(ticker, price_date)` ensures no duplicate date ticks are inserted for any given asset.

---

## 🚀 Terminal Commands & Execution Guide

### 1. Prerequisites & Virtual Environment Setup
Open your terminal inside the project directory and create a virtual environment:

```bash
# Navigate to project directory
cd FinancialDatabaseProject

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 2. Install Required Packages
Install the required database, API, and data manipulation dependencies:

```bash
pip install pandas yfinance sqlalchemy
```

### 3. Run the Database Ingestion & Benchmark Script
Execute `propose.py` to build the database schema, download live Yahoo Finance data, execute the ETL pipeline, and benchmark initial query latency:

```bash
python propose.py
```

---

## 📈 Pipeline Walkthrough (`propose.py`)

1. **DB Cleanup & Reset:** Automatically checks for and removes any pre-existing `stock_exchange.db` file to ensure a clean, reproducible state.
2. **Schema Instantiation:** Initializes the SQLite engine using SQLAlchemy `text()` raw SQL statements, creating the `companies` and `stock_prices` tables with explicit relational constraints.
3. **API Data Extraction:** Uses `yfinance.download()` to fetch raw market tick data across the target temporal range.
4. **ETL & Data Normalization:** Unpivots multi-indexed columns using Pandas `stack()`, cleans columns, formats date strings into standardized `YYYY-MM-DD` objects, and filters required fields (`ticker`, `price_date`, `close_price`, `volume`).
5. **Relational Population:** Bulk inserts company metadata into the dimension table and normalized price records into the fact table via `.to_sql()`.
6. **Baseline Performance Evaluation:** Runs a parameterized raw SQL lookup (`SELECT ... WHERE ticker = 'AAPL' ORDER BY price_date DESC LIMIT 5`) and measures execution time in milliseconds.

---

## 💡 Output Showcase

Upon executing `python propose.py`, you will see output similar to the following in your terminal:

```text
Fetching live market data from Yahoo Finance...
[*********************100%***********************]  5 of 5 completed

--- INFRASTRUCTURE TEST SUCCESSFUL ---
Database populated with ~1250 historical records.
Baseline Query execution time for 'AAPL': 1.248 ms

Most recent data fetched from your new database:
Date: 2025-12-31 | Ticker: AAPL | Close: $252.10
Date: 2025-12-30 | Ticker: AAPL | Close: $250.85
Date: 2025-12-29 | Ticker: AAPL | Close: $249.50
Date: 2025-12-26 | Ticker: AAPL | Close: $248.10
Date: 2025-12-24 | Ticker: AAPL | Close: $247.95
```