# kepegawaian-apps

### First 
```bash
Rename .env-database-example file to .env-database
Rename .env-golang-example file to .env-golang
Rename .env-nodejs-example file to .env-nodejs
Rename .env-python-example file to .env-python
```

### Create network

```bash
make create-network
```

### Start/Stop all services

```bash
make start-all
make stop-all
```

### Start/Stop services one by one

#### services-database

* Compose file: [./docker-compose.service-database.yml](./docker-compose.service-database.yml)
* Start: `make start-service-database`
* Stop: `make stop-service-database`

#### services-python

* Compose file: [./docker-compose.service-python.yml](./docker-compose.service-python.yml)
* Start: `make start-service-python`
* Stop: `make stop-service-python`

#### services-nodejs

* Compose file: [./docker-compose.service-nodejs.yml](./docker-compose.service-nodejs.yml)
* Start: `make start-service-nodejs`
* Stop: `make stop-service-nodejs`

#### services-golang

* Compose file: [./docker-compose.service-python.yml](./docker-compose.service-python.yml)
* Start: `make start-service-golang`
* Stop: `make stop-service-golang`
