FROM golang:1.12.17-alpine3.11 AS build
RUN apk --no-cache add gcc g++ make ca-certificates git
WORKDIR /go/src/github.com/jabardigitalservice/picasso-backend/service-golang

COPY Gopkg.lock Gopkg.toml ./
COPY vendor vendor
COPY db_host db_host
COPY middleware middleware
COPY models models
COPY retry retry
COPY satuankerja satuankerja
COPY jabatan jabatan
COPY eventuser eventuser
COPY jobAttendance jobAttendance
COPY deviceToken deviceToken
COPY notificationService notificationService
COPY notificationWorker notificationWorker
COPY notificationMessage notificationMessage
COPY utils utils

RUN go install ./...

# 5 build the GO program
RUN CGO_ENABLED=0 GOOS=linux

FROM alpine:3.7
WORKDIR /usr/bin

ENV TZ=Asia/Jakarta
RUN apk --update add tzdata ca-certificates && \
    update-ca-certificates 2>/dev/null || true \
    cp /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY --from=build /go/bin .