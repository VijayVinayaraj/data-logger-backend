FROM python:3.11-alpine

RUN apk add build-base
ADD . /code
WORKDIR /code 
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python3","server.py"]