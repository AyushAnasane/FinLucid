import csv
import os
import requests
import yfinance as yf
from django.conf import settings

_nse_cache = None
_bse_cache = None
_mf_cache = None


def get_nse_tickers():
    """NSE stocks + ETFs, symbol -> name"""
    global _nse_cache
    if _nse_cache is None:
        tickers = {}

        stock_path = os.path.join(settings.BASE_DIR, 'core', 'data', 'nse_tickers.csv')
        with open(stock_path, newline='', encoding='latin-1') as f:
            for row in csv.DictReader(f):
                symbol = row['SYMBOL'].strip().upper()
                tickers[symbol] = row['NAME OF COMPANY'].strip()

        etf_path = os.path.join(settings.BASE_DIR, 'core', 'data', 'nse_etfs.csv')
        with open(etf_path, newline='', encoding='latin-1') as f:
            for row in csv.DictReader(f):
                symbol = row['Symbol'].strip().upper()
                tickers[symbol] = row['SecurityName'].strip()

        _nse_cache = tickers
    return _nse_cache


def get_bse_tickers():
    """BSE stocks + ETFs, symbol -> name"""
    global _bse_cache
    if _bse_cache is None:
        tickers = {}

        stock_path = os.path.join(settings.BASE_DIR, 'core', 'data', 'bse_tickers.csv')
        if os.path.exists(stock_path):
            with open(stock_path, newline='', encoding='latin-1') as f:
                for row in csv.DictReader(f):
                    symbol = row.get('Security Id', '').strip().upper()
                    name = row.get('Security Name', '').strip()
                    if symbol:
                        tickers[symbol] = name

        etf_path = os.path.join(settings.BASE_DIR, 'core', 'data', 'bse_etfs.csv')
        if os.path.exists(etf_path):
            with open(etf_path, newline='', encoding='latin-1') as f:
                for row in csv.DictReader(f):
                    symbol = row.get('Security Id', '').strip().upper()
                    name = row.get('Security Name', '').strip()
                    if symbol:
                        tickers[symbol] = name

        _bse_cache = tickers
    return _bse_cache


def get_tickers_for_exchange(exchange):
    return get_nse_tickers() if exchange == 'NSE' else get_bse_tickers()


def get_mf_schemes():
    """AMFI mutual fund schemes, scheme_code -> scheme name"""
    global _mf_cache
    if _mf_cache is None:
        try:
            resp = requests.get("https://api.mfapi.in/mf", timeout=10)
            data = resp.json()
            _mf_cache = {str(item['schemeCode']): item['schemeName'] for item in data}
        except Exception:
            _mf_cache = {}
    return _mf_cache


def get_live_price(asset_type, identifier, exchange='NSE'):
    try:
        if asset_type in ('stock', 'etf'):
            suffix = '.NS' if exchange == 'NSE' else '.BO'
            ticker = yf.Ticker(f"{identifier}{suffix}")
            return round(ticker.fast_info['last_price'], 2)
        elif asset_type == 'mf':
            resp = requests.get(f"https://api.mfapi.in/mf/{identifier}/latest", timeout=10)
            data = resp.json()
            return round(float(data['data'][0]['nav']), 4)
    except Exception:
        return None
    return None