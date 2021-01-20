module.exports = {
    mongoURI: `mongodb://${process.env.DB_MONGO_HOST}:${process.env.DB_MONGO_PORT}/${process.env.MONGO_DB_LOGBOOK}`
};
