FROM python:3.10
WORKDIR /

RUN apt-get update -y
RUN apt-get upgrade -y
COPY ./requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .

ENV PSQL_HOST 123
ENV PSQL_DBNAME 123
ENV PSQL_PORT 5432
ENV PSQL_USER root
ENV PSQL_PASSWORD 123
ENV TOKEN 123
ENV API_TOKEN 123
ENV API_ID 123


CMD python3 handlers.py 