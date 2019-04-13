FROM python:3.6

ADD . /app/
ADD config.yml /app/
WORKDIR /app

RUN ["pip", "install", "-r", "requirements.txt"]

EXPOSE 80/tcp

ENTRYPOINT ["python", "api.py"]