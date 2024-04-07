FROM python:3.10-slim
RUN apt-get update \
    && apt-get install -y ffmpeg
RUN mkdir /app
COPY requirements.txt /app
RUN pip3 install -r /app/requirements.txt --no-cache-dir
COPY ./bot ./app/bot
COPY ./main.py ./app
WORKDIR /app
CMD ["python3", "main.py"]
