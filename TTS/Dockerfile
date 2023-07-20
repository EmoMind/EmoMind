FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu20.04

RUN apt-get update
RUN apt install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt update
RUN apt install -y python3.9
RUN apt install -y python3-pip

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY download.py .
RUN python3 download.py

COPY . .

CMD ["flask", "--app", "server.py", "run", "--host", "0.0.0.0", "--port", "5008"]
