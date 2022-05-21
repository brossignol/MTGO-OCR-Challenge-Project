FROM python:3.10.4

RUN mkdir /MTGO-OCR-Challenge-Project

WORKDIR /MTGO-OCR-Challenge-Project

COPY Pipfile .
COPY Pipfile.lock .

RUN cd /MTGO-OCR-Challenge-Project
RUN pip install pipenv
RUN pipenv install

COPY . .
