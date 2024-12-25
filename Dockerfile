FROM python:3.10.12

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD python ctrl_budgets/manage.py runserver 0.0.0.0:8000