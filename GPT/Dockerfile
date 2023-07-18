FROM python:3.9

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["flask", "--app", "server.py", "run", "--host", "0.0.0.0", "--port", "5007"]
