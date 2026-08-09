# Project Instructions

## Tech Stack
- **Language**: Python 3.10+
- **Deep Learning**: PyTorch >= 2.0.0, Einops, HuggingFace Hub, Safetensors
- **Data & Math**: Pandas, NumPy, Plotly, Matplotlib
- **Data Feed Sources**: AKShare, Baostock, Eastmoney API
- **Web UI**: Flask, Flask-CORS

## Code Style & Conventions
- **Format**: PEP 8 styling. Use descriptive variable names matching pandas dataframe structures (e.g., `df`, `x_df`, `x_timestamp`).
- **Data Column Names**: Standardize time-series dataframes to:
  - `timestamps` / `date` (datetime)
  - `open`, `high`, `low`, `close` (float)
  - `volume` (float/int)
  - `amount` (float)
- **Path Handling**: Avoid hardcoding absolute Windows paths (e.g., `D:\...`). Use relative paths with `os.path` helper functions to remain platform-independent.

## Execution & Running

### Core Tasks
- **Web UI Application**: Run live web predictor on http://localhost:7070:
  ```bash
  python webui/run.py
  ```
- **Fetch A-Share Data**: Fetch historical daily data for a given stock code to `./examples/data/`:
  ```bash
  python examples/get_date_new.py
  ```
- **Run Basic Forecasts**: Make forecasts from a local CSV file:
  ```bash
  python examples/prediction_example.py
  ```
- **Macro-Enhanced Forecast**: Perform predictions factoring in SSE index trend, sectors, macro policies, and Fed interest rates:
  ```bash
  python examples/prediction_new.py
  ```
- **Backtest Strategy**: Evaluate Kronos buy/sell signals on historical data:
  ```bash
  python examples/run_backtest_kronos.py
  ```

### Fine-Tuning Models
- Fine-tune tokenizer: `python finetune/train_tokenizer.py`
- Fine-tune predictor: `python finetune/train_predictor.py`
- Configuration: `finetune/config.py`

## Project Structure
- `model/` — Core implementation of Kronos model (`kronos.py`, `module.py`)
- `webui/` — Flask Web UI application interface for visual forecasting
- `examples/` — Python scripts demonstrating prediction, data acquiring, and backtesting
- `finetune/` — Scripts and configs to fine-tune Kronos on proprietary stock domains
- `tests/` — Regression and unit tests for the ML pipeline
