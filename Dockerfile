FROM python:3.11-slim

#RUN apt-get update && apt-get install -y \
#    build-essential \
#    libpq-dev \
#    && rm -rf /var/lib/apt/lists/*

WORKDIR /src

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

COPY . .

CMD ["python", "src/main.py"]