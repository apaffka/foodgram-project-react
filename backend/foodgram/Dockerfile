FROM python:3.8-slim

RUN mkdir /mycode

COPY requirements.txt  /mycode

RUN pip install --upgrade pip
RUN pip install -r /mycode/requirements.txt --no-cache-dir

COPY . /mycode

WORKDIR /mycode

CMD ["bash", "docker-endpoint.sh"]