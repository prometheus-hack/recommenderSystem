FROM python:3.9

COPY . .

RUN pip install --upgrade -r requirements.txt