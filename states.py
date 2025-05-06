from aiogram.dispatcher.filters.state import State, StatesGroup

class CalculatorStates(StatesGroup):
    age = State()
    engine_type = State()
    engine_capacity = State()
    engine_power = State()
    price = State()