const bodyParser = require("body-parser")
const mongoose = require("mongoose")
const express = require("express")
const helmet = require('helmet')
const cors = require('cors')
const path = require('path')
const Raven = require('raven')
const fileUpload = require('express-fileupload')
const timeout = require('connect-timeout')

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

const authenticate = require('./controllers/authenticate')

const app = express()

// default options
app.use(cors())
app.use(helmet());
app.use(timeout('5m'))
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(fileUpload())
app.use(haltOnTimedout)

function haltOnTimedout (req, res, next) {
  if (!req.timedout) next()
}

mongoose.Promise = global.Promise

// Authentications
app.use(authenticate)

// Import models
app.set('models', mongoose.models)

// Import modules
const route = require('./routes')

//routes
app.use('/api/logbook', route)
Raven.config(process.env.SENTRY_URI).install()

const host = process.env.HOST || "0.0.0.0"
const port = process.env.LOGBOOK_PORT || 80

// start the server
app.listen(port, () => {
    console.log(`Api Logbook service listening on port ${host}:${port}`)
})
