module.exports = {
    mongoURI1: `mongodb://${process.env.DB_MONGO_HOST}:${process.env.DB_MONGO_PORT}/${process.env.MONGO_DB_LOGBOOK}`,
    mongoURI2: `mongodb://${process.env.DB_MONGO_HOST}:${process.env.DB_MONGO_PORT}/${process.env.MONGO_DB_ATTENDANCE}`,
    mongoURI3: `mongodb://${process.env.DB_MONGO_HOST}:${process.env.DB_MONGO_PORT}/${process.env.MONGO_DB_HOLIDAY_DATE}`
};
