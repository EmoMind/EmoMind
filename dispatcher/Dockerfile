FROM python:3.10.1

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["flask", "--app", "dispatcher.py", "run", "--host", "0.0.0.0", "--port", "5001"]