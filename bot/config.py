from enum import Enum

# Перечисления для атрибутов автомобиля
class EngineType(Enum):
    GASOLINE = "gasoline"
    DIESEL = "diesel"
    ELECTRIC = "electric"
    HYBRID = "hybrid"

class VehicleAge(Enum):
    UNDER_THREE = "до 3"
    THREE_TO_FIVE = "3-5"

# Курсы валют (константы)
EUR_TO_RUB = 92.908
USD_TO_RUB = 92.0  # Примерный курс USD/RUB
CNY_TO_RUB = 11   # Примерный курс CNY/RUB
KRW_TO_RUB = 0.07   # Примерный курс KRW/RUB

# Комиссии для доставки
DELIVERY_FEES = {
    "china": {
        "usd": 4100,      # 4.100 USD
        "rub": 50000      # 50.000 RUB
    },
    "korea": {
        "usd": 2500,      # 2.500 USD
        "rub": 150000     # 150.000 RUB
    }
}

# Конфигурация тарифов
CONFIG = {
    "tariffs": {
        "recycling_factors": {
            "adjustments": {
                "до 3": {
                    "gasoline": {
                        "default": 0.17,
                        "over_3.501": 137.11
                    },
                    "diesel": {
                        "default": 0.17,
                        "over_3.501": 137.11
                    },
                    "electric": 0.17,
                    "hybrid": {
                        "default": 0.17,
                        "over_3.501": 137.11
                    }
                },
                "3-5": {
                    "gasoline": {
                        "default": 0.26,
                        "3.001-3.500": 164.84,
                        "over_3.501": 180.24
                    },
                    "diesel": {
                        "default": 0.26,
                        "3.001-3.500": 164.84,
                        "over_3.501": 180.24
                    },
                    "electric": 0.26,
                    "hybrid": {
                        "default": 0.26,
                        "3.001-3.500": 164.84,
                        "over_3.501": 180.24
                    }
                }
            }
        },
        "age_groups": {
            "overrides": {
                "до 3": {
                    "brackets": [
                        {"min_cost_euro": 0, "max_cost_euro": 8500, "percent": 54, "min_per_cc": 2.5},
                        {"min_cost_euro": 8501, "max_cost_euro": 16700, "percent": 48, "min_per_cc": 3.5},
                        {"min_cost_euro": 16701, "max_cost_euro": 42300, "percent": 48, "min_per_cc": 5.5},
                        {"min_cost_euro": 42301, "max_cost_euro": 84500, "percent": 48, "min_per_cc": 7.5},
                        {"min_cost_euro": 84501, "max_cost_euro": 169000, "percent": 48, "min_per_cc": 15},
                        {"min_cost_euro": 169001, "max_cost_euro": float('inf'), "percent": 48, "min_per_cc": 20}
                    ]
                },
                "3-5": {
                    "engine_rates": [
                        {"min_cc": 0, "rate_per_cc": 1.5},
                        {"min_cc": 1001, "rate_per_cc": 1.7},
                        {"min_cc": 1501, "rate_per_cc": 2.7},
                        {"min_cc": 1801, "rate_per_cc": 2.7},
                        {"min_cc": 2301, "rate_per_cc": 3.0},
                        {"min_cc": 3001, "rate_per_cc": 3.6}
                    ]
                }
            }
        },
        "excise_rates": {
            "gasoline": 58,
            "diesel": 58,
            "electric": 0,
            "hybrid": 58
        },
        "customs_clearance_fee": {
            200000: 1067,
            450000: 2134,
            1200000: 4269,
            2700000: 11746,
            4200000: 16524,
            5500000: 21344,
            7000000: 27540,
            8000000: 30000,
            9000000: 30000,
            10000000: 30000,
            float('inf'): 30000
        }
    }
}