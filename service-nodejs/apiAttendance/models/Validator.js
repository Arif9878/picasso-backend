const {
    body
} = require('express-validator')

const formCheckin = () => [
    body('date', 'Tanggal tidak boleh kosong').notEmpty(),
    body('location', 'Lokasi tidak boleh kosong').notEmpty()
]

const formCheckout = () => [
    body('date', 'Tanggal tidak boleh kosong').notEmpty(),
]

module.exports = {
    formCheckin,
    formCheckout
}
