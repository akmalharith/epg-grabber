FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt ./requirements.txt
COPY epg_grabber ./
RUN pip3 install -r requirements.txt

CMD python3 -u app.py