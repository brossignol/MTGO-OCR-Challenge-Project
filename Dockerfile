FROM python:3.10.4

RUN mkdir /MTGO-OCR-Challenge-Project

WORKDIR /MTGO-OCR-Challenge-Project

COPY requirements.txt .

RUN cd /MTGO-OCR-Challenge-Project
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python", "bot.py"]
