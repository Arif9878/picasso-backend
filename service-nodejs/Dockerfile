FROM arf95/npm-alpine:latest as build
WORKDIR /usr/src/app
RUN apk update && apk upgrade && \
    apk add --update --no-cache

COPY package*.json ./
COPY package-lock*.json ./
COPY lerna-prod*.json ./lerna*.json
COPY . ./

RUN npm ci --production && \
    npm i lerna && npm run-script build

# remove development dependencies
RUN npm prune --production

FROM arf95/npm-alpine:latest
WORKDIR /usr/src/app

ENV TZ=Asia/Jakarta
RUN apk --update add tzdata && \
cp /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY --from=build /usr/src/app .
