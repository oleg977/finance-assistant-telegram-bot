import requests
from typing import Dict, Optional


class CurrencyAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Используем бесплатный API для получения курсов
        self.base_url = "https://v6.exchangerate-api.com/v6"

    def get_exchange_rates(self, base_currency: str = "USD") -> Optional[Dict]:
        """Получение курсов валют относительно базовой валюты"""
        try:
            url = f"{self.base_url}/{self.api_key}/latest/{base_currency}"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                if data.get('result') == 'success':
                    return {
                        'base': data['base_code'],
                        'rates': data['conversion_rates'],
                        'last_update': data.get('time_last_update_utc', 'Unknown')
                    }
            return None
        except Exception as e:
            print(f"Ошибка при получении курсов валют: {e}")
            return None

    def get_rub_rate(self) -> Optional[Dict]:
        """Получение курса рубля к USD и EUR"""
        rates = self.get_exchange_rates("USD")
        if rates:
            rub_rate = rates['rates'].get('RUB')
            if rub_rate:
                return {
                    'usd_to_rub': rub_rate,
                    'eur_to_rub': rub_rate / rates['rates'].get('EUR', 1),
                    'last_update': rates['last_update']
                }
        return None

    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> Optional[float]:
        """Конвертация валюты"""
        try:
            url = f"{self.base_url}/{self.api_key}/pair/{from_currency}/{to_currency}/{amount}"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                if data.get('result') == 'success':
                    return data.get('conversion_result')
            return None
        except Exception as e:
            print(f"Ошибка при конвертации валюты: {e}")
            return None