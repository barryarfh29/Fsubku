FROM python:3.11-alpine

WORKDIR /app

COPY . .
RUN apk add --no-cache tzdata \
    ; cp /usr/share/zoneinfo/Asia/Jakarta /etc/localtime \
    ; echo "Asia/Jakarta" > /etc/timezone \
    ; pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
