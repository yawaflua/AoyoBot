FROM python:3.10
WORKDIR /

RUN apt-get update -y
RUN apt-get upgrade -y
COPY ./requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .

CMD python3 handlers.py 