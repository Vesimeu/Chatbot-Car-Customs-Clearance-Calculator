from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, RegexpCommandsFilter
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from api_client import CalcusAPIClient
from keyboards import get_region_keyboard, get_age_keyboard, get_engine_type_keyboard
from convector import USD_TO_RUB
from usage_tracker import check_and_update_usage, MAX_ATTEMPTS
import logging
import re

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Определение состояний FSM
class CalculationStates(StatesGroup):
    region = State()
    age = State()
    engine_type = State()
    engine_capacity = State()
    engine_power = State()
    price = State()

def register_handlers(dp: Dispatcher):
    client = CalcusAPIClient()

    @dp.message_handler(commands=['start'])
    async def cmd_start(message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        can_proceed, remaining_attempts, reset_date = check_and_update_usage(user_id)

        if not can_proceed:
            await message.answer(
                f"Вы исчерпали лимит ({MAX_ATTEMPTS} расчёта в день). "
                f"Попробуйте снова завтра ({reset_date})."
            )
            return

        # Сбрасываем состояние перед началом нового расчёта
        await state.finish()
        async with state.proxy() as data:
            data['remaining_attempts'] = remaining_attempts

        await message.answer("Выберите регион:", reply_markup=get_region_keyboard())
        await CalculationStates.region.set()

    @dp.message_handler(Text(equals=["Китай", "Корея"]), state=CalculationStates.region)
    async def process_region(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['region'] = message.text
        await message.answer("Выберите возраст автомобиля:", reply_markup=get_age_keyboard())
        await CalculationStates.age.set()

    @dp.message_handler(Text(equals=["до 3", "3-5"]), state=CalculationStates.age)
    async def process_age(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['vehicle_age'] = message.text
        await message.answer("Выберите тип двигателя:", reply_markup=get_engine_type_keyboard())
        await CalculationStates.engine_type.set()

    @dp.message_handler(Text(equals=["Бензиновый", "Дизельный", "Гибридный", "Электрический"]),
                        state=CalculationStates.engine_type)
    async def process_engine_type(message: types.Message, state: FSMContext):
        engine_map = {
            "Бензиновый": "gasoline",
            "Дизельный": "diesel",
            "Гибридный": "hybrid",
            "Электрический": "electric"
        }
        try:
            async with state.proxy() as data:
                data['engine_type'] = engine_map[message.text]
                if data['engine_type'] == "electric":
                    data['engine_capacity'] = 0  # Устанавливаем объём 0 для электрического
                    await message.answer("Введите мощность двигателя (л.с.):", reply_markup=types.ReplyKeyboardRemove())
                    await CalculationStates.engine_power.set()
                else:
                    await message.answer("Введите объём двигателя (см³):", reply_markup=types.ReplyKeyboardRemove())
                    await CalculationStates.engine_capacity.set()
        except LookupError as e:
            logger.error(f"Ошибка состояния: {e}")
            await message.answer("Произошла ошибка. Пожалуйста, начните заново с /start.")
            await state.finish()

    @dp.message_handler(regexp=r'^\d+(\.\d+)?$', state=CalculationStates.engine_capacity)
    async def process_engine_capacity(message: types.Message, state: FSMContext):
        try:
            capacity = float(message.text)
            if capacity <= 0:
                raise ValueError("Объём должен быть положительным")
            async with state.proxy() as data:
                data['engine_capacity'] = capacity
            await message.answer("Введите мощность двигателя (л.с.):")
            await CalculationStates.engine_power.set()
        except ValueError:
            await message.answer("Пожалуйста, введите корректное число (например, 2000).")
        except LookupError as e:
            logger.error(f"Ошибка состояния: {e}")
            await message.answer("Произошла ошибка. Пожалуйста, начните заново с /start.")
            await state.finish()

    @dp.message_handler(regexp=r'^\d+(\.\d+)?$', state=CalculationStates.engine_power)
    async def process_engine_power(message: types.Message, state: FSMContext):
        try:
            power = float(message.text)
            if power <= 0:
                raise ValueError("Мощность должна быть положительной")
            async with state.proxy() as data:
                data['engine_power'] = power
                currency = "CNY" if data["region"] == "Китай" else "KRW"
            await message.answer(f"Введите стоимость автомобиля ({currency}):")
            await CalculationStates.price.set()
        except ValueError:
            await message.answer("Пожалуйста, введите корректное число (например, 300).")
        except LookupError as e:
            logger.error(f"Ошибка состояния: {e}")
            await message.answer("Произошла ошибка. Пожалуйста, начните заново с /start.")
            await state.finish()

    @dp.message_handler(regexp=r'^\d+(\.\d+)?$', state=CalculationStates.price)
    async def process_price(message: types.Message, state: FSMContext):
        try:
            price = float(message.text)
            if price <= 0:
                raise ValueError("Стоимость должна быть положительной")
            async with state.proxy() as data:
                currency = "CNY" if data["region"] == "Китай" else "KRW"
                data['vehicle_price'] = price
                data['currency'] = currency
                remaining_attempts = data['remaining_attempts']

            # Параметры для API
            params = {
                "vehicle_age": data["vehicle_age"],
                "engine_type": data["engine_type"],
                "engine_power": data["engine_power"],
                "engine_capacity": data["engine_capacity"],
                "vehicle_price": data["vehicle_price"],
                "currency": data["currency"]
            }

            # Вызов API
            result = client.calculate_customs(params)
            if not result:
                await message.answer("Ошибка расчёта. Попробуйте позже.")
                await state.finish()
                return

            # Комиссии
            region = data["region"]
            if region == "Китай":
                usd_fee = 4100 * USD_TO_RUB
                rub_fee = 50000
                destination = "Перми"
            else:
                usd_fee = 2500 * USD_TO_RUB
                rub_fee = 150000
                destination = "Владивостока"

            # Итоговая стоимость
            total_cost = result["total2"] + usd_fee + rub_fee

            # Формирование ответа
            response = (
                f"Результаты расчёта:\n"
                f"Таможенный сбор: {result['sbor']:,.0f} RUB\n"
                f"Таможенная пошлина: {result['tax']:,.0f} RUB\n"
                f"Утилизационный сбор: {result['util']:,.0f} RUB\n"
                f"Комиссия ({region}, USD): {usd_fee:,.0f} RUB\n"
                f"Комиссия ({region}, RUB): {rub_fee:,.0f} RUB\n"
                f"Итоговая стоимость до {destination}: {total_cost:,.0f} RUB\n\n"
                f"Осталось расчётов на сегодня: {remaining_attempts}\n"
                f"Чтобы ещё раз рассчитать, напишите /start"
            )

            await message.answer(response, reply_markup=types.ReplyKeyboardRemove())
            await state.finish()

        except ValueError:
            await message.answer("Пожалуйста, введите корректное число (например, 5000000).")
        except LookupError as e:
            logger.error(f"Ошибка состояния: {e}")
            await message.answer("Произошла ошибка. Пожалуйста, начните заново с /start.")
            await state.finish()
