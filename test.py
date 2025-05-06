import logging
import unittest
from calculate import CustomsCalculator, WrongParamException

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

class TestCustomsCalculator(unittest.TestCase):
    def setUp(self):
        self.calculator = CustomsCalculator()
        self.tolerance = 20000
        self.base_params = [
            {
                "engine_capacity": 4000,
                "engine_power": 300,
                "price_rub": 5000000,
                "korean_work_rub": 0,
                "agent_fee_rub": 0,
                "vladivostok_work_rub": 0,
                "delivery_rub": 0
            },
            {
                "engine_capacity": 2000,
                "engine_power": 185,
                "price_rub": 2000000,
                "korean_work_rub": 0,
                "agent_fee_rub": 0,
                "vladivostok_work_rub": 0,
                "delivery_rub": 0
            },
            {
                "engine_capacity": 1500,
                "engine_power": 130,
                "price_rub": 2000000,
                "korean_work_rub": 0,
                "agent_fee_rub": 0,
                "vladivostok_work_rub": 0,
                "delivery_rub": 0
            }
        ]

    def test_under_three_4000cc_gasoline(self):
        params = {**self.base_params[0], "age": "до 3", "engine_type": "gasoline"}
        self.calculator.set_vehicle_details(**params)
        results = self.calculator.calculate()
        total_cost = results["Итоговая стоимость (RUB)"]
        expected_cost = 10550790
        logging.info(f"Итоговая стоимость: {total_cost} руб.")
        self.assertTrue(
            abs(total_cost - expected_cost) <= self.tolerance,
            f"Итоговая стоимость {total_cost} не в пределах {expected_cost} ± {self.tolerance}"
        )

    def test_under_three_2000cc_gasoline(self):
        params = {**self.base_params[1], "age": "до 3", "engine_type": "gasoline"}
        self.calculator.set_vehicle_details(**params)
        results = self.calculator.calculate()
        total_cost = results["Итоговая стоимость (RUB)"]
        expected_cost = 3037136
        logging.info(f"Итоговая стоимость: {total_cost} руб.")
        self.assertTrue(
            abs(total_cost - expected_cost) <= self.tolerance,
            f"Итоговая стоимость {total_cost} не в пределах {expected_cost} ± {self.tolerance}"
        )

    def test_under_three_1500cc_gasoline(self):
        params = {**self.base_params[2], "age": "до 3", "engine_type": "gasoline"}
        self.calculator.set_vehicle_details(**params)
        results = self.calculator.calculate()
        total_cost = results["Итоговая стоимость (RUB)"]
        expected_cost = 2975146
        logging.info(f"Итоговая стоимость: {total_cost} руб.")
        self.assertTrue(
            abs(total_cost - expected_cost) <= self.tolerance,
            f"Итоговая стоимость {total_cost} не в пределах {expected_cost} ± {self.tolerance}"
        )

    def test_three_to_five_1500cc_gasoline(self):
        params = {**self.base_params[2], "age": "3-5", "engine_type": "gasoline"}
        self.calculator.set_vehicle_details(**params)
        results = self.calculator.calculate()
        total_cost = results["Итоговая стоимость (RUB)"]
        expected_cost = 2253861
        logging.info(f"Итоговая стоимость: {total_cost} руб.")
        self.assertTrue(
            abs(total_cost - expected_cost) <= self.tolerance,
            f"Итоговая стоимость {total_cost} не в пределах {expected_cost} ± {self.tolerance}"
        )
    def test_three_to_five_1500cc_hibrid(self):
        params = {**self.base_params[2], "age": "3-5", "engine_type": "hybrid"}
        self.calculator.set_vehicle_details(**params)
        results = self.calculator.calculate()
        total_cost = results["Итоговая стоимость (RUB)"]
        expected_cost = 2253861
        logging.info(f"Итоговая стоимость: {total_cost} руб.")
        self.assertTrue(
            abs(total_cost - expected_cost) <= self.tolerance,
            f"Итоговая стоимость {total_cost} не в пределах {expected_cost} ± {self.tolerance}"
        )


    def test_three_to_five_2000cc_gasoline(self):
        params = {**self.base_params[1], "age": "3-5", "engine_type": "gasoline"}
        self.calculator.set_vehicle_details(**params)
        results = self.calculator.calculate()
        total_cost = results["Итоговая стоимость (RUB)"]
        expected_cost = 2518649.2
        logging.info(f"Итоговая стоимость: {total_cost} руб.")
        self.assertTrue(
            abs(total_cost - expected_cost) <= self.tolerance,
            f"Итоговая стоимость {total_cost} не в пределах {expected_cost} ± {self.tolerance}"
        )

    def test_three_to_five_2000cc_hibrid(self):
        params = {**self.base_params[1], "age": "3-5", "engine_type": "hybrid"}
        self.calculator.set_vehicle_details(**params)
        results = self.calculator.calculate()
        total_cost = results["Итоговая стоимость (RUB)"]
        expected_cost = 2518650
        logging.info(f"Итоговая стоимость: {total_cost} руб.")
        self.assertTrue(
            abs(total_cost - expected_cost) <= self.tolerance,
            f"Итоговая стоимость {total_cost} не в пределах {expected_cost} ± {self.tolerance}"
        )

    def test_three_to_five_2500cc_gasoline(self):
        params = {**self.base_params[1], "engine_capacity": 2500, "engine_power": 250, "age": "3-5", "engine_type": "gasoline"}
        self.calculator.set_vehicle_details(**params)
        results = self.calculator.calculate()
        total_cost = results["Итоговая стоимость (RUB)"]
        expected_cost = 2713757.0
        logging.info(f"Итоговая стоимость: {total_cost} руб.")
        self.assertTrue(
            abs(total_cost - expected_cost) <= self.tolerance,
            f"Итоговая стоимость {total_cost} не в пределах {expected_cost} ± {self.tolerance}"
        )

class TestValidation(unittest.TestCase):
    def setUp(self):
        self.calculator = CustomsCalculator()

    def test_invalid_inputs(self):
        test_cases = [
            {
                "desc": "Некорректный возраст",
                "params": {
                    "age": "invalid",
                    "engine_capacity": 2000,
                    "engine_power": 185,
                    "engine_type": "gasoline",
                    "price_rub": 2000000,
                    "korean_work_rub": 0,
                    "agent_fee_rub": 0,
                    "vladivostok_work_rub": 0,
                    "delivery_rub": 0
                }
            },
            {
                "desc": "Некорректный тип двигателя",
                "params": {
                    "age": "до 3",
                    "engine_capacity": 2000,
                    "engine_power": 185,
                    "engine_type": "invalid",
                    "price_rub": 2000000,
                    "korean_work_rub": 0,
                    "agent_fee_rub": 0,
                    "vladivostok_work_rub": 0,
                    "delivery_rub": 0
                }
            },
            {
                "desc": "Слишком низкая цена",
                "params": {
                    "age": "до 3",
                    "engine_capacity": 2000,
                    "engine_power": 185,
                    "engine_type": "gasoline",
                    "price_rub": 5000,
                    "korean_work_rub": 0,
                    "agent_fee_rub": 0,
                    "vladivostok_work_rub": 0,
                    "delivery_rub": 0
                }
            }
        ]

        for case in test_cases:
            with self.subTest(desc=case["desc"]):
                with self.assertRaises(WrongParamException):
                    self.calculator.set_vehicle_details(**case["params"])

if __name__ == '__main__':
    unittest.main()