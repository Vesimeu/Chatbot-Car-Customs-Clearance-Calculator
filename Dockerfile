FROM python:3.8-slim
WORKDIR /ChatbotCarCustomsClearanceCalculator
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "bot/bot.py"]