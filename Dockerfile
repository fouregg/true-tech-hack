FROM python:3.10-bullseye

ENV POETRY_HOME=/root/.poetry
ENV PATH=$PATH:/root/.poetry/bin
ENV PYTHONPATH /usr/app/

RUN apt-get update
RUN apt-get install libasound-dev libportaudio2 libportaudiocpp0 portaudio19-dev -y
RUN pip install pyaudio

WORKDIR /usr/app/

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
