FROM python:3.7-slim

RUN python -m pip install --upgrade pip

COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt

ENV TZ=Asia/Jakarta
RUN apk --update add tzdata ca-certificates && \
    update-ca-certificates 2>/dev/null || true \
    cp /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY . .
