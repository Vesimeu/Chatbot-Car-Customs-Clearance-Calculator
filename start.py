from bot.api_client import CalcusAPIClient

client = CalcusAPIClient()
params = {
    "vehicle_age": "до 3",
    "engine_type": "gasoline",
    "engine_power": 300,
    "engine_capacity": 4000,
    "vehicle_price": 5000000,
    "currency": "RUB"
}
result = client.calculate_customs(params)
print(result)