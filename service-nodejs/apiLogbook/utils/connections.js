const mongoose = require('mongoose');
const db1 = require("../utils/database").mongoURI1
const db2 = require("../utils/database").mongoURI2
const db3 = require("../utils/database").mongoURI3

function makeNewConnection(uri) {
    const db = mongoose.createConnection(uri, {
        useNewUrlParser: true,
        useUnifiedTopology: true,
    });

    db.on('error', function (error) {
        console.log(`MongoDB :: connection ${this.name} ${JSON.stringify(error)}`)
        db.close().catch(() => console.log(`MongoDB :: failed to close connection ${this.name}`))
    })

    db.on('connected', function () {
        // mongoose.set('debug', function (col, method, query, doc) {
        //     console.log(`MongoDB :: ${this.conn.name} ${col}.${method}(${JSON.stringify(query)},${JSON.stringify(doc)})`)
        // })
        console.log(`MongoDB :: connected ${this.name}`)
    })

    db.on('disconnected', function () {
        console.log(`MongoDB :: disconnected ${this.name}`)
    })

    return db
}

const logBookConnection = makeNewConnection(db1);
const attendanceConnection = makeNewConnection(db2);
const holidaydateConnection = makeNewConnection(db3);

module.exports = {
    logBookConnection,
    attendanceConnection,
    holidaydateConnection,
};