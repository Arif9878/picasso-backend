const {
    body
} = require('express-validator')

module.exports.form = () => [
    body('projectName', 'Nama project tidak boleh kosong').notEmpty(),
    body('nameTask', 'Nama task tidak boleh kosong').notEmpty(),
    body('difficultyTask', 'Format data tidak sesuai').isNumeric().optional({nullable: true, checkFalsy: true}),
]
