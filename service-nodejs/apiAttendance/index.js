const bodyParser = require("body-parser")
const mongoose = require("mongoose")
const express = require("express")
const helmet = require('helmet')
const cors = require('cors')
const path = require('path')
const Raven = require('raven')

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
const db = require("./utils/database").mongoURI

// default options
app.use(cors())
app.use(helmet());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

const connectWithRetry = function() {
    return mongoose.connect(db, { useNewUrlParser: true, useUnifiedTopology: true }, function(err) {
        if (err) {
            console.error('Failed to connect to mongo on startup - retrying in 5 sec', err)
            setTimeout(connectWithRetry, 5000)
        } else {
            console.log("mongoDB Connected")
        }
    })
}

connectWithRetry()

mongoose.Promise = global.Promise

// Authentications
// app.use(authenticate)

// Configure raven setup
Raven.config(process.env.SENTRY_DSN_NODEJS).install()
app.use(Raven.requestHandler())

// Import models
app.set('models', mongoose.models)

// Import modules
const route = require('./routes')
const routesClientApp = require('./routesClientApp')

//routes
app.use('/api/attendance', require('./controllers/authenticate'), route)
app.use('/api/client', require('./controllersClient/clientToken'), routesClientApp)

// The error handler middleware
app.use(Raven.errorHandler())

const host = process.env.HOST || "0.0.0.0"
const port = process.env.ATTENDANCE_PORT || 80

app.listen(port, () => {
    console.log(`Api Attendance service listening on port ${host}:${port}`)
})

