FROM python:3.10.1

RUN apt-get update
RUN apt-get install -y ffmpeg libopus-dev

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]
