const {
    body
} = require('express-validator')

const formCheckin = () => [
    body('date', 'Tanggal tidak boleh kosong').notEmpty(),
    body('location', 'Lokasi tidak boleh kosong').notEmpty(),
    body('mood', 'Suasana hati tidak boleh kosong').isIn(['worst', 'sad', 'neutral', 'good', 'excellent'])
]

const formCheckout = () => [
    body('date', 'Tanggal tidak boleh kosong').notEmpty(),
]

module.exports = {
    formCheckin,
    formCheckout
}
