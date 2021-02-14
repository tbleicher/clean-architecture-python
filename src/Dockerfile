FROM python:3.9-slim-buster

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# we need to add gcc to install python modules
RUN apt-get update \
  && apt-get -y install gcc \
  && apt-get clean

# get rid of pip version warnings
RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install -r requirements.txt

# switching to a non-root user please refer to
# https://aka.ms/vscode-docker-python-user-rights
RUN useradd appuser && chown -R appuser /usr/src/app
USER appuser

COPY ./app .
