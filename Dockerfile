FROM python:3.8-slim-buster

WORKDIR /app
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt
ADD epg_grabber /app/

CMD [ "python3", "-u", "app.py" ]