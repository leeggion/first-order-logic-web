FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# RUN python -m spacy download en_core_web_trf
RUN python -m spacy download en_core_web_sm

COPY new_requirements.txt .
RUN pip install --no-cache-dir -r new_requirements.txt
COPY . .

CMD ["flask", "run", "--host=0.0.0.0", "--reload"]
