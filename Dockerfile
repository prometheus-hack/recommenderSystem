FROM python:3.11-slim

COPY . .

RUN pip install --upgrade -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]