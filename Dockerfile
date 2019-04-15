FROM python:3.6

ADD . /app/
WORKDIR /app

RUN ["pip", "install", "-r", "requirements.txt"]

EXPOSE 8080/tcp

ENTRYPOINT ["python", "api.py", "--mongo-uri", "mongodb://mongodb:27017"]