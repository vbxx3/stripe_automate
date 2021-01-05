FROM python:3.8

COPY .env .
COPY requirements.txt .

RUN pip install -r requirements.txt

COPY main.py .
COPY recaptcha.py .

CMD ["python", "./main.py"]