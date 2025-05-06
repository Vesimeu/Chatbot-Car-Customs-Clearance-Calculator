import logging
import unittest
from calculate import CustomsCalculator, WrongParamException


class TestCustomsCalculator(unittest.TestCase):
    def setUp(self):
        self.calculator = CustomsCalculator()

    def test_vehicle_under_three(self):
        """Тест расчётов для автомобиля до 3 лет."""
        self.calculator.set_vehicle_details(
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
        results = self.calculator.calculate()

        logging.info(results["Итоговая стоимость (RUB)"])

        self.assertAlmostEqual(results["Таможенная пошлина (RUB)"], 2787240.0, places=2)
        self.assertAlmostEqual(results["Утилизационный сбор (RUB)"], 2742200.0, places=2)
        self.assertEqual(results["Таможенный сбор (RUB)"], 21344)
        self.assertEqual(results["Акциз (RUB)"], 17400)
        self.assertAlmostEqual(results["Итоговая стоимость (RUB)"], 10568184.0, places=2)

    def test_vehicle_under_three(self):
        """Тест расчётов для автомобиля до 3 лет."""
        self.calculator.set_vehicle_details(
            age="до 3",
            engine_capacity=2000,
            engine_power=185,
            engine_type="gasoline",
            price_rub=2000000,
            korean_work_rub=0,
            agent_fee_rub=0,
            vladivostok_work_rub=0,
            delivery_rub=0
        )
        results = self.calculator.calculate()

        logging.info(results["Итоговая стоимость (RUB)"])

        self.assertAlmostEqual(results["Итоговая стоимость (RUB)"], 10568184.0, places=2)

    def test_vehicle_three_to_five(self):
        """Тест расчётов для автомобиля 3-5 лет."""
        self.calculator.set_vehicle_details(
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
        results = self.calculator.calculate()
        logging.info(results["Итоговая стоимость (RUB)"])

        self.assertAlmostEqual(results["Итоговая стоимость (RUB)"], 2518649.2, places=2)

    def test_vehicle_three_to_five(self):
        """Тест расчётов для автомобиля 3-5 лет."""
        self.calculator.set_vehicle_details(
            age="3-5",
            engine_capacity=2500,
            engine_power=250,
            engine_type="gasoline",
            price_rub=2000000,
            korean_work_rub=0,
            agent_fee_rub=0,
            vladivostok_work_rub=0,
            delivery_rub=0
        )
        results = self.calculator.calculate()
        logging.info(results["Итоговая стоимость (RUB)"])

        self.assertAlmostEqual(results["Итоговая стоимость (RUB)"], 2713757, places=2)

    def test_invalid_age(self):
        """Тест обработки некорректного возраста."""
        with self.assertRaises(WrongParamException):
            self.calculator.set_vehicle_details(
                age="invalid",
                engine_capacity=2000,
                engine_power=185,
                engine_type="gasoline",
                price_rub=2000000,
                korean_work_rub=0,
                agent_fee_rub=0,
                vladivostok_work_rub=0,
                delivery_rub=0
            )

    def test_invalid_engine_type(self):
        """Тест обработки некорректного типа двигателя."""
        with self.assertRaises(WrongParamException):
            self.calculator.set_vehicle_details(
                age="до 3",
                engine_capacity=2000,
                engine_power=185,
                engine_type="invalid",
                price_rub=2000000,
                korean_work_rub=0,
                agent_fee_rub=0,
                vladivostok_work_rub=0,
                delivery_rub=0
            )



    def test_low_price(self):
        """Тест обработки слишком низкой цены."""
        with self.assertRaises(WrongParamException):
            self.calculator.set_vehicle_details(
                age="до 3",
                engine_capacity=2000,
                engine_power=185,
                engine_type="gasoline",
                price_rub=5000,
                korean_work_rub=0,
                agent_fee_rub=0,
                vladivostok_work_rub=0,
                delivery_rub=0
            )


if __name__ == '__main__':
    unittest.main()