const moment = require('moment')

const logBookPerTupoksi = (data) => {
    let records = []
    if (data['logBookTupoksi'].length > 0 ) {
        data['logBookTupoksi'].forEach((item, index) => {
            records.push(
                    {
                        bold: true,
                        text: `3.${index+1}	${item.name}`
                    },
                    {
                        
                        columns: [
                            {},
                            {
                                width: 450,
                                ul: [
                                    `Nama Tupoksi : ${item.name}`,
                                    `Jumlah Hasil Pekerjaan : ${item.count} kali \n\n`,
                                ]
                            },
                        ]
                    },
                    { text: 'Evidence Output Pekerjaan' }
                )
            item['items'].forEach(async (itemB, indexB) => {
                const isDocumentTaskURL = String(itemB.documentTaskURL) === 'null'
                if (itemB.blobsEvidence) {
                    records.push(
                        {
                            alignment: 'center',
                            margin: [0, 5, 0, 0],
                            style: 'boldNormal',
                            table: {
                                headerRows: 1,
                                widths: [ 20, 150, 270 ],
                                body: [
                                    [
                                        { text: 'No', style: 'tableHeader',},
                                        { text: 'Judul', style: 'tableHeader',},
                                        { text: 'Evidence Output Pekerjaan', style: 'tableHeader',}
                                    ],
                                    [
                                        { text: indexB+1,  rowSpan: 5 }, 'Nama Projek', `${itemB.projectName}`
                                    ],
                                    [
                                        "", "Nama Task", `${itemB.nameTask}`
                                    ],
                                    [
                                        "", "Tanggal Pengerjaan",  moment(itemB.dateTask).format('dddd, DD MMMM YYYY')
                                    ],
                                    [
                                        "", "Link (URL) Hasil Kerja", isDocumentTaskURL ? '' : itemB.documentTaskURL
                                    ],
                                    [ 
                                        "",
                                        { 
                                            image: itemB.blobsEvidence ,
                                            width: 350,
                                            colSpan: 2, 
                                            alignment: 'left' 
                                        },
                                        ""
                                    ],
                                ]
                            },
                        }
                    )
                } else {
                    records.push(
                        {
                            alignment: 'center',
                            margin: [0, 5, 0, 0],
                            style: 'boldNormal',
                            table: {
                                headerRows: 1,
                                widths: [ 20, 150, 270 ],
                                body: [
                                    [
                                        { text: 'No', style: 'tableHeader',},
                                        { text: 'Judul', style: 'tableHeader',},
                                        { text: 'Evidence Output Pekerjaan', style: 'tableHeader',}
                                    ],
                                    [
                                        { text: indexB+1,  rowSpan: 4 }, 'Nama Projek', `${itemB.projectName}`
                                    ],
                                    [
                                        "", "Nama Task", `${itemB.nameTask}`
                                    ],
                                    [
                                        "", "Tanggal Pengerjaan",  moment(itemB.dateTask).format('dddd, DD MMMM YYYY')
                                    ],
                                    [
                                        "", "Link (URL) Hasil Kerja", isDocumentTaskURL ? '' : itemB.documentTaskURL
                                    ]
                                ]
                            },
                        }
                    )
                }
            })
        })
    }
    return records
}

const BAB_3 = (data) => {
    const month = moment(data.reporting_date).format('MMMM')
    const year = moment(data.reporting_date).format('YYYY')
    return [
        {
            alignment: 'center',
            bold: true,
            text: [
                    'BAB III \n',
                    'BUKTI PELAKSANAAN URAIAN PEKERJAAN\n\n'    
            ]   
        },
        {
            alignment: 'justify',
            preserveLeadingSpaces: true,
            text: [
                `        Berikut daftar laporan hasil kerja disertai dengan bukti output pekerjaan pelaksanaan pekerjaan bulan ${month} ${year}: \n\n`    
            ]
        },
        ...logBookPerTupoksi(data)
    ]
}

module.exports = {
    BAB_3,
    logBookPerTupoksi
}
