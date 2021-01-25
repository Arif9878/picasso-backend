const bodyParser = require("body-parser")
const mongoose = require("mongoose")
const express = require("express")
const helmet = require('helmet')
const cors = require('cors')
const path = require('path')
const Raven = require('raven')
const timeout = require('connect-timeout')
const { MongoClient } = require('mongodb')

// Import middleware
const env = process.env.NODE_ENV
try {
    switch(env) {
        case 'undefined':
            require('dotenv').config();
            break
        case 'development':
            require('dotenv').config({
                path: path.resolve(process.cwd(), '../../.env'),
            })
            break
        default:
            Error('Unrecognized Environment')
    }
} catch (err) {
    Error('Error trying to run file')
}

const app = express()

// default options
app.use(cors())
app.use(helmet())
app.use(timeout('5m'))
app.use(bodyParser.urlencoded({ extended: true }))
app.use(bodyParser.json())

function haltOnTimedout (req, res, next) {
    req.clearTimeout()
    req.setTimeout(300000)
    next()
}

app.use(haltOnTimedout)

mongoose.Promise = global.Promise

// Configure raven setup
Raven.config(process.env.SENTRY_DSN_NODEJS).install()
app.use(Raven.requestHandler())

// Import models
app.set('models', mongoose.models)

// Import modules
const route = require('./routes')

async function onHealthCheckDB () {
  const client = await MongoClient.connect(`mongodb://${process.env.DB_MONGO_HOST}:${process.env.DB_MONGO_PORT}`)
  const db1 = await client.db(process.env.MONGO_DB_LOGBOOK).admin().ping()
  const db2 = await client.db(`${process.env.MONGO_DB_ATTENDANCE}`).admin().ping()
  const db3 = await client.db(`${process.env.MONGO_DB_HOLIDAY_DATE}`).admin().ping()
  const results = {
      logbookDB : db1,
      attendaceDB : db2,
      holidayDateDB : db3
  }
  return results
}

//routes
app.use('/api/export-pdf', route)
app.get('/api/healthcheck', async (req, res) => {
  const healthChecks = await onHealthCheckDB()
  res.send(healthChecks)
})
// The error handler middleware
app.use(Raven.errorHandler())

const host = process.env.HOST || "0.0.0.0"
const port = process.env.EXPORT_PDF_PORT || 80

// start the server
app.listen(port, () => {
    console.log(`Api Export PDF service listening on port ${host}:${port}`)
})
