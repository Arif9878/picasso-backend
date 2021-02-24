const moment = require('moment')

const Cover = (data) => {
    const month = moment(data.reporting_date).format('MMMM')
    const year = moment(data.reporting_date).format('YYYY')
    const {
      user
    } = data
    return [
        {
            text: 'LAPORAN KINERJA INDIVIDU',
            alignment: 'center',
            bold: true,
            fontSize: 16
        },
        {
            text: `BULAN ${month.toUpperCase()} ${year}`,
            alignment: 'center',
            margin: [0, 15, 0, 85],
            style: 'boldNormal'
        },
        {
            image: 'static/images/logo_jabarprov.png',
            alignment: 'center',
            margin: [0, 15, 0, 0],
            width: 150
        },
        {
            text: `${user.first_name} ${user.last_name}`,
            margin: [0, 85, 0, 0],
            alignment: 'center',
            style: 'boldNormal'
        },
        {
            text: `${user.jabatan}`,
            alignment: 'center',
            style: 'boldNormal'
        },
        {
            text: `${user.divisi}`,
            alignment: 'center',
            style: 'boldNormal'
        },
        {
            text: `${user.manager_category || '-'}`,
            alignment: 'center',
            margin: [0, 125, 0, 0],
            style: 'boldNormal'
        },
        {
            text: 'UPTD PUSAT LAYANAN DIGITAL, DATA DAN INFORMASI GEOSPASIAL',
            alignment: 'center',
            style: 'boldNormal'
        },
        {
            text: '(JABAR DIGITAL SERVICE)',
            alignment: 'center',
            style: 'boldNormal'
        },
        {
            text: 'DINAS KOMUNIKASI DAN INFORMATIKA PROVINSI JAWA BARAT',
            alignment: 'center',
            style: 'boldNormal'
        },
        {
            text: `${year}`,
            alignment: 'center',
            style: 'boldNormal',
        },
    ]
}

module.exports = {
    Cover
}
