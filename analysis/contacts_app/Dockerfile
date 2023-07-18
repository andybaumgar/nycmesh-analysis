FROM python:3.10.2-slim-buster
RUN apt-get update

RUN mkdir /app
WORKDIR /app
COPY ../../requirements.txt .
RUN pip3 install -r requirements.txt

COPY ../../ .

RUN pip3 install -e .

WORKDIR /app/analysis/contacts_app
CMD [ "gunicorn", "--workers=5", "--threads=1", "-b 0.0.0.0:80", "app:server"]