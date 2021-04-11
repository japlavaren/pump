from collections import OrderedDict
from decimal import Decimal
from os import system
from typing import Dict, List, Tuple

from binance.client import Client
from binance.websockets import BinanceSocketManager
from terminaltables import AsciiTable

indicators = OrderedDict()
indicators['c'] = 'Zmena CENA'
indicators['v'] = 'Zmena OBJEM'

results = 10
symbol_max_len = 13
first_tickers: Dict[str, dict] = {}


def process_tickers(message_tickers: List[dict]) -> None:
    """
        "e": "24hrTicker",  // Event type
        "E": 123456789,     // Event time
        "s": "BNBBTC",      // Symbol
        "p": "0.0015",      // Price change
        "P": "250.00",      // Price change percent
        "w": "0.0018",      // Weighted average price
        "x": "0.0009",      // First trade(F)-1 price (first trade before the 24hr rolling window)
        "c": "0.0025",      // Last price
        "Q": "10",          // Last quantity
        "b": "0.0024",      // Best bid price
        "B": "10",          // Best bid quantity
        "a": "0.0026",      // Best ask price
        "A": "100",         // Best ask quantity
        "o": "0.0010",      // Open price
        "h": "0.0025",      // High price
        "l": "0.0010",      // Low price
        "v": "10000",       // Total traded base asset volume
        "q": "18",          // Total traded quote asset volume
        "O": 0,             // Statistics open time
        "C": 86400000,      // Statistics close time
        "F": 0,             // First trade ID
        "L": 18150,         // Last trade Id
        "n": 18151          // Total number of trades
    """
    changes: Dict[str, List[Tuple[str, Decimal]]] = {}

    for ticker in message_tickers:
        # str to Decimal conversion
        for key in 'p', 'P', 'w', 'x', 'c', 'Q', 'b', 'B', 'a', 'A', 'o', 'h', 'l', 'v', 'q':
            ticker[key] = Decimal(ticker[key])

        symbol = ticker['s']

        # load first ticker value
        if symbol not in first_tickers:
            first_tickers[symbol] = ticker
            continue

        first = first_tickers[symbol]

        # calculate diff
        for key in indicators.keys():
            diff = (ticker[key] - first[key]) / first[key]
            changes.setdefault(key, []).append((symbol, diff))

    if len(changes) == 0:
        return

    for key, diff in changes.items():
        changes[key] = sorted(diff, key=lambda d: d[1], reverse=True)

    columns = []

    for key, name in indicators.items():
        column = [name]
        column += [f'{symbol.ljust(symbol_max_len)} {diff * 100:.2}%' for symbol, diff in changes[key][:results]]
        columns.append(column)

    system('clear')
    table = AsciiTable(list(zip(*columns)))
    print(table.table)


if __name__ == '__main__':
    client = Client()
    bm = BinanceSocketManager(client)
    bm.start_ticker_socket(process_tickers)
    bm.start()
