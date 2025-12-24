# Trends Script

A Python automation script that aggregates trending topics from various sources and sends a daily summary notification to your phone.

## Features

- **Twitter Trends**: Fetches top trends for Poland and Global (via trends24.in).
- **Google Trends**: Retrieves trending searches in the US/UK.
- **Yahoo Finance**: Scrapes trending stock tickers.
- **Crypto**: Gets top cryptocurrency movers via CoinGecko.
- **Notifications**: Sends a push notification using [ntfy.sh](https://ntfy.sh).

## How It Works

The script `script/trends.py` performs the following:
1.  **Scraping & APIs**: Connects to various services to gather data.
2.  **Formatting**: Compiles the data into a concise message.
3.  **Delivery**: Posts the message to a specified `ntfy.sh` topic.

## Deployment

This project is deployed using **GitHub Actions** to run automatically twice a day.

- **Workflow File**: `.github/workflows/daily_trends.yml`
- **Schedule**: Runs at 6:00 AM and 6:00 PM UTC daily.
- **Environment**: Ubuntu Latest with Python 3.12.

### Configuration

The notification topic is configured in a `.env` file in the root directory:
```
NTFY_TOPIC=trends_app_daily
```

## Local Usage

The project uses `uv` for dependency management and execution.

1.  Run the script:
    ```bash
    uv run script/trends.py
    ```
