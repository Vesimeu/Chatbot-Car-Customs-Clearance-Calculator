import logging
import requests
import os
from typing import Dict, Optional
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class CalcusAPIClient:
    def __init__(self):
        self.base_url = "https://calcus.ru/api/v1/Customs"
        self.client_id = os.getenv("CALCUS_CLIENT_ID")
        self.api_key = os.getenv("CALCUS_API_KEY")
        self.headers = {
            "Api-Client-Id": self.client_id,
            "Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def _map_params(self, params: Dict) -> Dict:
        """
        Преобразует параметры из формата бота в формат, ожидаемый API.

        Args:
            params: Параметры в формате бота (country_from, vehicle_type, vehicle_price, etc.).

        Returns:
            Словарь с параметрами в формате API.
        """
        # Маппинг engine_type
        engine_map = {
            "gasoline": 1,
            "diesel": 2,
            "hybrid": 3,
            "electric": 4
        }

        # Маппинг vehicle_age
        age_map = {
            "до 3": "0-3",
            "3-5": "3-5"
        }

        api_params = {
            "owner": 1,  # Физическое лицо для личного использования
            "age": age_map.get(params.get("vehicle_age"), params.get("vehicle_age")),
            "engine": engine_map.get(params.get("engine_type")),
            "power": params.get("engine_power"),
            "power_unit": 1,  # Лошадиные силы
            "value": params.get("engine_capacity"),
            "price": params.get("vehicle_price"),
            "curr": params.get("currency", "RUB")
        }

        return api_params

    def calculate_customs(self, params: Dict) -> Optional[Dict]:
        """
        Отправляет запрос к API calcus.ru для расчёта таможенных платежей.

        Args:
            params: Параметры для API (в формате бота).

        Returns:
            Словарь с результатами расчёта или None в случае ошибки.

        Raises:
            requests.exceptions.RequestException: Если запрос не удался.
        """
        # Преобразование параметров
        api_params = self._map_params(params)

        try:
            logger.info(f"Sending request to API with params: {api_params}")
            response = requests.post(self.base_url, json=api_params, headers=self.headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            logger.info(f"API response: {result}")
            return result
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}, Response: {response.text}")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error occurred: {e}")
            return None
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timed out: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None