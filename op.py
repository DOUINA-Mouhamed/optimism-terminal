import requests
import time
import os
import sys
import select

if os.name == 'nt':
    import msvcrt
else:
    import tty
    import termios

# Constants
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/coins/markets"
UPDATE_INTERVAL = 30
MAX_RETRY_WAIT = 60

log_messages = []
show_logs = True

ASCII_ART = """
      \033[91m████████      \033[0m
   \033[91m██████████████   \033[0m
  \033[91m████████████████  \033[0m
 \033[91m██████████████████ \033[0m
\033[91m██████    █    █████\033[0m
\033[91m█████  █  █    █████\033[0m
\033[91m█████    █  ████████\033[0m
 \033[91m██████████████████ \033[0m
  \033[91m████████████████  \033[0m
   \033[91m██████████████   \033[0m
      \033[91m████████      \033[0m
"""

price_data = {
    "price": None,
    "high_24h": None,
    "low_24h": None,
    "market_cap": None,
    "volume": None,
    "price_change_percentage": None,
}

def clear_terminal():
    """Clears the terminal screen regardless of the OS."""
    os.system('cls' if os.name == 'nt' else 'clear')

def log_message(message):
    """Adds a message to the log with a timestamp and keeps only the last 5 logs."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    log_messages.insert(0, log_entry)
    if len(log_messages) > 5:
        log_messages.pop()

def fetch_price():
    """Fetch the current price, 24h high, low, market cap, and volume of OP/USDT from CoinGecko."""
    try:
        params = {"vs_currency": "usd", "ids": "optimism"}
        response = requests.get(COINGECKO_API_URL, params=params, headers={"Cache-Control": "no-cache"}, timeout=10)
        if response.status_code == 200:
            data = response.json()[0]
            price_data["price"] = data.get("current_price")
            price_data["high_24h"] = data.get("high_24h")
            price_data["low_24h"] = data.get("low_24h")
            price_data["market_cap"] = data.get("market_cap")
            price_data["volume"] = data.get("total_volume")
            price_data["price_change_percentage"] = data.get("price_change_percentage_24h")
            log_message(f"Price fetched successfully: ${price_data['price']:.3f}")
        elif response.status_code == 429:
            retry_after = response.headers.get('Retry-After')
            wait_time = int(retry_after) if retry_after is not None else MAX_RETRY_WAIT
            log_message(f"Rate limited by CoinGecko. Retrying in {wait_time} seconds.")
            time.sleep(wait_time)
        else:
            log_message(f"Error: Received status code {response.status_code} from CoinGecko.")
    except requests.exceptions.RequestException as e:
        log_message(f"Network error: {e}")

def display_ascii_art():
    """Display the ASCII art in its own section."""
    print("\n" + ASCII_ART + "\n")

def display_price():
    """Display the price, 24h high, low, market cap, and volume of OP/USDT on the terminal."""
    clear_terminal()
    display_ascii_art()

    if price_data['price_change_percentage'] is not None:
        if price_data['price_change_percentage'] > 0:
            change_symbol = "\033[92m▲\033[0m"
            change_color = "\033[92m"
        else:
            change_symbol = "\033[91m▼\033[0m"
            change_color = "\033[91m"
        change_24h = f"{change_color}{change_symbol} {price_data['price_change_percentage']:.2f}%\033[0m"
    else:
        change_24h = "N/A"

    # Display data
    print("============================")
    print("  Optimism Terminal")
    print("============================")
    print(f"  OP/USDT Price: ${price_data['price']:.3f}" if price_data['price'] else "  Price: N/A")
    print(f"  24h High: \033[92m${price_data['high_24h']:.3f}\033[0m" if price_data['high_24h'] else "  24h High: N/A")
    print(f"  24h Low: \033[91m${price_data['low_24h']:.3f}\033[0m" if price_data['low_24h'] else "  24h Low: N/A")
    print("============================")
    print(f"  Change 24h: {change_24h}")
    print(f"  Market Cap: ${price_data['market_cap']:,}" if price_data['market_cap'] else "  Market Cap: N/A")
    print(f"  Volume: ${price_data['volume']:,}" if price_data['volume'] else "  Volume: N/A")
    print("============================")

    if show_logs:
        print("\nLogs:")
        for log in log_messages:
            print(f"- {log}")
    print("\nPress [L] to show/hide logs")

def main():
    """Main loop to continuously fetch and display the price."""
    global show_logs
    while True:
        start_time = time.time()
        fetch_price()
        display_price()
        elapsed_time = time.time() - start_time
        for _ in range(int(UPDATE_INTERVAL * 10)):
            time.sleep(0.1)
            if os.name == 'nt' and msvcrt.kbhit():
                if msvcrt.getch().decode('utf-8').lower() == 'l':
                    show_logs = not show_logs
                    break

if __name__ == "__main__":
    main()
