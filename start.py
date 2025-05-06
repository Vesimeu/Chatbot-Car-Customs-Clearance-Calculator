from service.calculate import CustomsCalculator, WrongParamException
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def run_tests():
    calculator = CustomsCalculator()

    # Тест 1: Автомобиль до 3 лет
    print("Тест 1: Автомобиль до 3 лет")
    print("Параметры: Цена 5,000,000 RUB, Объём 4,000 см³, Мощность 300 л.с., Возраст до 3, Тип gasoline")
    try:
        calculator.set_vehicle_details(
            age="до 3",
            engine_capacity=4000,
            engine_power=300,
            engine_type="gasoline",
            price_rub=5000000,
            korean_work_rub=0,
            agent_fee_rub=0,
            vladivostok_work_rub=0,
            delivery_rub=0
        )
        print("\nРезультаты расчёта:")
        calculator.calculate()
    except (ValueError, WrongParamException) as e:
        logger.error(f"Ошибка теста 1: {e}")
        print(f"Ошибка: {e}")

    print("\n" + "="*50 + "\n")

    # Тест 2: Автомобиль 3-5 лет
    print("Тест 2: Автомобиль 3-5 лет")
    print("Параметры: Цена 2,000,000 RUB, Объём 2,000 см³, Мощность 185 л.с., Возраст 3-5, Тип gasoline")
    try:
        calculator.set_vehicle_details(
            age="3-5",
            engine_capacity=2000,
            engine_power=185,
            engine_type="gasoline",
            price_rub=2000000,
            korean_work_rub=0,
            agent_fee_rub=0,
            vladivostok_work_rub=0,
            delivery_rub=0
        )
        print("\nРезультаты расчёта:")
        calculator.calculate()
    except (ValueError, WrongParamException) as e:
        logger.error(f"Ошибка теста 2: {e}")
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    run_tests()