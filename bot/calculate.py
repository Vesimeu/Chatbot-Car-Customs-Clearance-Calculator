import logging
from config import CONFIG, EngineType, VehicleAge, EUR_TO_RUB, USD_TO_RUB, CNY_TO_RUB, KRW_TO_RUB, DELIVERY_FEES

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class WrongParamException(Exception):
    def __init__(self, message):
        super().__init__(message)
        logger.error(message)

class CustomsCalculator:
    def __init__(self):
        self.config = CONFIG
        self.reset_fields()

    def reset_fields(self):
        self.vehicle_age = None
        self.engine_capacity = None
        self.engine_power = None
        self.engine_type = None
        self.vehicle_price_rub = None
        self.korean_work_rub = None
        self.agent_fee_rub = None
        self.vladivostok_work_rub = None
        self.delivery_rub = None
        self.region = None

    def set_vehicle_details(
        self, age, engine_capacity, engine_power, engine_type, price, region,
        korean_work_rub=0, agent_fee_rub=0, vladivostok_work_rub=0, delivery_rub=0
    ):
        try:
            if age not in [e.value for e in VehicleAge]:
                raise ValueError(f"Недопустимый возраст: {age}. Допустимые: до 3, 3-5")
            self.vehicle_age = VehicleAge(age)

            self.engine_capacity = float(engine_capacity)
            if self.engine_capacity <= 0:
                raise ValueError("Объём двигателя должен быть больше 0")

            self.engine_power = float(engine_power)
            if self.engine_power <= 0:
                raise ValueError("Мощность двигателя должна быть больше 0")

            engine_type = engine_type.lower()
            if engine_type == "galosine":
                engine_type = "gasoline"
            if engine_type not in [e.value for e in EngineType]:
                raise ValueError(f"Недопустимый тип двигателя: {engine_type}. Допустимые: gasoline, diesel, electric, hybrid")
            self.engine_type = EngineType(engine_type)

            if region not in ["china", "korea"]:
                raise ValueError("Регион должен быть 'china' или 'korea'")

            self.region = region
            price = float(price)
            if price < 0:
                raise ValueError("Цена автомобиля не может быть отрицательной")

            # Конвертация цены в рубли
            if region == "china":
                self.vehicle_price_rub = price * CNY_TO_RUB
            else:  # korea
                self.vehicle_price_rub = price * KRW_TO_RUB

            if self.vehicle_price_rub < 10000:
                raise ValueError("Цена автомобиля в рублях должна быть не менее 10,000 руб.")

            # Установка комиссий
            fees = DELIVERY_FEES[region]
            self.korean_work_rub = fees["usd"] * USD_TO_RUB  # Комиссия в USD конвертируется в RUB
            self.vladivostok_work_rub = fees["rub"]          # Прямая комиссия в RUB
            self.agent_fee_rub = float(agent_fee_rub)
            self.delivery_rub = float(delivery_rub)

        except ValueError as e:
            raise WrongParamException(f"Ошибка ввода: {e}")

    def calculate_customs_clearance_fee(self):
        for price_limit, fee in sorted(self.config['tariffs']['customs_clearance_fee'].items()):
            if self.vehicle_price_rub <= price_limit:
                logger.info(f"Таможенный сбор: {fee} руб.")
                return fee
        return 30000

    def calculate_recycling_fee(self):
        adjustments = self.config['tariffs']['recycling_factors']['adjustments']
        age_key = self.vehicle_age.value
        engine_type_factors = adjustments[age_key][self.engine_type.value]
        if isinstance(engine_type_factors, dict):
            if self.engine_capacity > 3501:
                factor = engine_type_factors.get("over_3.501", engine_type_factors["default"])
            elif 3001 <= self.engine_capacity <= 3500:
                factor = engine_type_factors.get("3.001-3.500", engine_type_factors["default"])
            else:
                factor = engine_type_factors["default"]
        else:
            factor = engine_type_factors
        fee = 20000 * factor
        logger.info(f"Расчёт утилизационного сбора: базовая ставка 20,000 × коэффициент {factor} = {fee} руб.")
        return fee

    def calculate_excise(self):
        excise_rate = self.config['tariffs']['excise_rates'][self.engine_type.value]
        excise = self.engine_power * excise_rate
        logger.info(f"Расчёт акциза: {self.engine_power} л.с. × {excise_rate} руб./л.с. = {excise} руб.")
        return excise

    def calculate_customs_duty(self):
        if self.vehicle_age == VehicleAge.UNDER_THREE:
            cost_euro = self.vehicle_price_rub / EUR_TO_RUB
            brackets = self.config["tariffs"]["age_groups"]["overrides"]["до 3"]["brackets"]
            for bracket in brackets:
                if cost_euro <= bracket["max_cost_euro"]:
                    percent_duty = (bracket["percent"] / 100) * cost_euro
                    min_duty = bracket["min_per_cc"] * self.engine_capacity
                    duty_euro = max(percent_duty, min_duty)
                    duty_rub = duty_euro * EUR_TO_RUB
                    logger.info(f"Пошлина для авто до 3 лет: max({bracket['percent']}% × {cost_euro} EUR = {percent_duty} EUR, {bracket['min_per_cc']} EUR/см³ × {self.engine_capacity} см³ = {min_duty} EUR) = {duty_euro} EUR → {duty_rub} RUB")
                    return duty_rub
            bracket = brackets[-1]
            percent_duty = (bracket["percent"] / 100) * cost_euro
            min_duty = bracket["min_per_cc"] * self.engine_capacity
            duty_euro = max(percent_duty, min_duty)
            duty_rub = duty_euro * EUR_TO_RUB
            logger.info(f"Пошлина для авто до 3 лет: max({bracket['percent']}% × {cost_euro} EUR = {percent_duty} EUR, {bracket['min_per_cc']} EUR/см³ × {self.engine_capacity} см³ = {min_duty} EUR) = {duty_euro} EUR → {duty_rub} RUB")
            return duty_rub
        elif self.vehicle_age == VehicleAge.THREE_TO_FIVE:
            rates = self.config["tariffs"]["age_groups"]["overrides"]["3-5"]["engine_rates"]
            selected_rate = rates[0]["rate_per_cc"]
            for rate in rates:
                if self.engine_capacity >= rate["min_cc"]:
                    selected_rate = rate["rate_per_cc"]
            duty_rub = selected_rate * self.engine_capacity * EUR_TO_RUB
            logger.info(f"Пошлина для авто 3-5 лет: ставка {selected_rate} EUR/см³ × объём {self.engine_capacity} см³ × EUR/RUB {EUR_TO_RUB} = {duty_rub} RUB")
            return duty_rub

    def calculate_etc(self):
        try:
            duty_rub = self.calculate_customs_duty()
            clearance_fee = self.calculate_customs_clearance_fee()
            recycling_fee = self.calculate_recycling_fee()
            excise = 0

            total_pay = (
                self.vehicle_price_rub +
                self.korean_work_rub +
                duty_rub +
                recycling_fee +
                clearance_fee +
                self.agent_fee_rub +
                self.vladivostok_work_rub +
                self.delivery_rub
            )

            return {
                "Цена авто (RUB)": self.vehicle_price_rub,
                f"Комиссия ({self.region}, USD)": self.korean_work_rub,
                f"Комиссия ({self.region}, RUB)": self.vladivostok_work_rub,
                "Таможенная пошлина (RUB)": duty_rub,
                "Утилизационный сбор (RUB)": recycling_fee,
                "Таможенный сбор (RUB)": clearance_fee,
                f"Итоговая стоимость до {'Перми' if self.region == 'china' else 'Владивостока'} (RUB)": total_pay
            }
        except KeyError as e:
            logger.error(f"Отсутствует конфигурация тарифов: {e}")
            raise

    def calculate_under_three(self):
        try:
            duty_rub = self.calculate_customs_duty()
            clearance_fee = self.calculate_customs_clearance_fee()
            recycling_fee = self.calculate_recycling_fee()
            excise = 0

            total_pay = (
                self.vehicle_price_rub +
                self.korean_work_rub +
                duty_rub +
                recycling_fee +
                clearance_fee +
                excise +
                self.agent_fee_rub +
                self.vladivostok_work_rub +
                self.delivery_rub
            )

            return {
                "Цена авто (RUB)": self.vehicle_price_rub,
                f"Комиссия ({self.region}, USD)": self.korean_work_rub,
                f"Комиссия ({self.region}, RUB)": self.vladivostok_work_rub,
                "Таможенная пошлина (RUB)": duty_rub,
                "Утилизационный сбор (RUB)": recycling_fee,
                "Таможенный сбор (RUB)": clearance_fee,
                f"Итоговая стоимость до {'Перми' if self.region == 'china' else 'Владивостока'} (RUB)": total_pay
            }
        except KeyError as e:
            logger.error(f"Отсутствует конфигурация тарифов: {e}")
            raise

    def calculate(self):
        if self.vehicle_age == VehicleAge.UNDER_THREE:
            return self.calculate_under_three()
        else:
            return self.calculate_etc()

    def print_table(self):
        from tabulate import tabulate
        results = self.calculate()
        table = [[k, f"{v:,.2f}" if isinstance(v, (float, int)) else v] for k, v in results.items()]
        print(tabulate(table, headers=["Описание", "Сумма"], tablefmt="psql"))