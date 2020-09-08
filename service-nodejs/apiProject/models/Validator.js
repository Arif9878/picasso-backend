const {
    body
} = require('express-validator')

module.exports.form = () => [
    body('projectName', 'Nama project tidak boleh kosong').notEmpty(),
]
