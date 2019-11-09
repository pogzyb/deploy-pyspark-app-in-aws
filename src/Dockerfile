#FROM python:3.7-alpine
FROM doodmanbro/dspython:0.1.0

RUN apk update && \
    apk upgrade && \
    apk add \
    bash

ENV HOME /code
ENV PYTHONPATH=$PYTHONPATH:${HOME}/src/ml

COPY ./src/ ${HOME}/src/
COPY ./tmp /tmp
WORKDIR ${HOME}/src

RUN pip install -r requirements.txt --upgrade pip

COPY ./run.sh /usr/local/bin/run.sh
RUN chmod u+x /usr/local/bin/run.sh

EXPOSE ${APP_PORT}

ENTRYPOINT "run.sh"