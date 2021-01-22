const fs = require('fs')
const PdfPrinter = require('pdfmake')
const moment = require('moment')
moment.locale('id')
const dayOffType = ['CUTI', 'SAKIT', 'IZIN']
const holidayType = ['Libur Nasional', 'Cuti Bersama']
const generateReport = (docDefinition, filePath) => {
  return new Promise((resolve, reject) => {
      try {
          const fonts = {
            Roboto: {
              normal: 'static/fonts/Roboto-Regular.ttf',
              bold: 'static/fonts/Roboto-Medium.ttf',
              italics: 'static/fonts/Roboto-Italic.ttf',
              bolditalics: 'static/fonts/Roboto-MediumItalic.ttf'
            }
          }
          const printer = new PdfPrinter(fonts)
          const pdfDoc = printer.createPdfKitDocument(docDefinition)
          const stream = pdfDoc.pipe(fs.createWriteStream(filePath))
          stream.on('finish', function(){
              const pdfFile = fs.readFileSync(filePath)
              fs.unlinkSync(filePath)
              resolve(pdfFile)
          })
          pdfDoc.end()
      } catch (err) {
          reject(err)
      }
  })
}

const logBook = (data) => {
    let records = []
    data.forEach((item, index) => {
        if (dayOffType.includes(item.nameTask)) {
            records.push([{
                    text: index + 1
                },
                {
                    text: moment(item.dateTask).format('dddd, DD MMMM YYYY')
                },
                {
                    text: item.nameTask,
                    colSpan: 5,
                    alignment: 'center'
                },
                {},
                {},
                {},
                {}
            ])
        } else if (item.nameTask === 'LIBUR' || holidayType.includes(item.type)) {
            records.push([{
                    text: index + 1,
                     color: 'red',
                },
                {
                    text: moment(item.dateTask).format('dddd, DD MMMM YYYY'),
                     color: 'red',
                },
                {
                    text: item.nameTask,
                    colSpan: 5,
                    alignment: 'center',
                     color: 'red',
                },
                {},
                {},
                {},
                {}
            ])
        } else {
            records.push([{
                    text: index + 1
                },
                {
                    text: moment(item.dateTask).format('dddd, DD MMMM YYYY')
                },
                {
                    text: item.projectName + ' - ' + item.nameTask
                },
                {
                    text: item.workPlace
                },
                {
                    text: 'PLD'
                },
                {
                    text: item.isMainTask ? '√' : ''
                },
                {
                    text: !item.isMainTask ? '√' : ''
                }
            ])
        }
    })
    return records
}

const logBookPerDay = (data) => {
    let records = []
    if (data['logBookPerDay'].length > 0 ) {
        records.push(
        // EVIDENCE   
        {
            alignment: 'center',
            style: 'boldNormal',
            pageBreak: 'before',
            pageOrientation: 'landscape',
            text: 'LAMPIRAN'
        },
        {
            fontSize: 11,
            text: 'Berikut adalah evidence daftar uraian kegiatan harian yang didetailkan setiap harinya dibulan ini.'
        })
        data['logBookPerDay'].forEach((item, index) => {
            records.push({
                margin: [0, 15, 0, 0],
                fontSize: 11,
                bold: true,
                text: 'Hari, Tanggal : ' + moment(item._id).format('dddd, DD MMMM YYYY')
            })
            item['items'].forEach(async (itemB, indexB) => {
                const isDocumentTaskURL = String(itemB.documentTaskURL) === 'null'
                records.push({
                        margin: [10, 10, 0, 0],
                        fontSize: 11,
                        text: (indexB+1) + '. ' + `${itemB.projectName} - ${itemB.nameTask}`
                    },
                    {
                        margin: [20, 0, 0, 0],
                        fontSize: 11,
                        text: 'a. FOTO'
                    },
                    {
                        margin: [80, 0, 10, 0],
                        image: itemB.blobsEvidence,
                        width: 350,
                    },
                    {
                        margin: [20, 0, 0, 0],
                        fontSize: 11,
                        text: isDocumentTaskURL ? '' : 'b. LINK'
                    },
                    {
                        margin: [20, 0, 0, 0],
                        fontSize: 11,
                        text: isDocumentTaskURL ? '' : itemB.documentTaskURL
                })
            })
        })
    }
    return records
}

const reportForm = (data) => {
  const month = moment(data.reporting_date).format('MMMM')
  const year = moment(data.reporting_date).format('YYYY')
  
  const {
      user,
      jabatan
  } = data
  const docDefinition = {
      compress: true,
      content: [
          {
              image: 'static/images/logo_jabarprov.png',
              alignment: 'center',
              margin: [0, 15, 0, 0],
              width: 150
          },
          {
            text: 'LAPORAN',
            alignment: 'center',
            margin: [0, 85, 0, 0],
            bold: true,
            fontSize: 16
          },
          {
            text: `Bulan ${month} ${year}`,
            alignment: 'center',
            style: 'boldNormal'
          },
          {
            text: 'IMPLEMENTASI DAN PEMELIHARAAN INFRASTRUKTUR COMMAND CENTER',
            alignment: 'center',
            margin: [0, 85, 0, 0],
            style: 'boldNormal'
          },
          {
            text: `${user.first_name} ${user.last_name}`,
            margin: [0, 85, 0, 0],
            alignment: 'center',
            style: 'boldNormal'
          },
          {
            text: `${user.divisi}`,
            alignment: 'center',
            style: 'boldNormal'
          },
          {
            text: 'TENAGA AHLI PENGELOLA LAYANAN DIGITAL',
            alignment: 'center',
            margin: [0, 105, 0, 0],
            style: 'boldNormal'
          },
          {
            text: 'DINAS KOMUNIKASI INFORMATIKA',
            alignment: 'center',
            style: 'boldNormal'
          },
          {
            text: 'PROVINSI JAWA BARAT',
            alignment: 'center',
            style: 'boldNormal'
          },
          {
            text: `${year}`,
            alignment: 'center',
            style: 'boldNormal'
          },
          // BODY   
          {
              alignment: 'center',
              bold: true,
              fontSize: 11,
              pageBreak: 'before',
              pageOrientation: 'landscape',
              color: 'black',
              fillColor: '#1aa3ff',
              table: {
                headerRows: 1,
                widths: [ '*' ],
                body: [
                  [ { text: 'LAPORAN HARIAN', border: [] } ],
                  [ { text: 'JABAR DIGITAL SERVICE', border: [] } ]
                ]
              }
          },
          {
            margin: [0, 25, 0, 0],
            style: 'boldNormal',
            table: {
                headerRows: 1,
                widths: [ 70, 120, '*' ],
                body: [
                    [ 
                        { text: `Bulan: ${month}`, border: [] },
                        { text: `Tahun: ${year}`, border: [] },
                        { 
                            text: 'Instansi: Dinas Komunikasi dan Informatika Jawa Barat',
                            alignment: 'right',
                            border: []
                        },

                    ],
                ]
            }
         },
         {
            margin: [0, 5, 0, 0],
            style: 'boldNormal',
            table: {
                headerRows: 1,
                widths: [ 120, 10, 10, '*' ],
                body: [
                    [ 
                        { text: 'Nama' },
                        { text: '' },
                        { text: ':' },
                        { text: `${user.first_name} ${user.last_name}` }
                    ],
                    [ 
                        { text: 'Divisi' },
                        { text: '' },
                        { text: ':' },
                        { text: `${user.divisi}` }
                    ],
                    [ 
                        { text: 'Jabatan' },
                        { text: '' },
                        { text: ':' },
                        { text: `${user.jabatan}` }
                    ],
                    [ 
                        { text: 'URAIAN TUGAS\n(DESKRIPSI JABATAN)' },
                        { text: '' },
                        { text: ':' },
                        jabatan.map(function(item, index) {
                            return { text: index+1 +". "+ item }
                        })
                    ],
                ]
            }
         },
         {
            margin: [0, 10, 0, 0],
            text: `RINCIAN HASIL KERJA SELAMA BULAN ${month.toUpperCase()}`,
            style: 'boldNormal'
         },
         // RINCIAN TABEL LAPORAN
         {
            alignment: 'center',
            margin: [0, 5, 0, 0],
            style: 'boldNormal',
            table: {
                headerRows: 2,
                widths: [ 20, 80, '*', 100, 100, 100, 100 ],
                body: [
                    [ 
                        { text: 'No', style: 'tableHeader', rowSpan: 2 },
                        { text: 'HARI/TANGGAL', style: 'tableHeader', rowSpan: 2 },
                        { text: 'KEGIATAN', style: 'tableHeader', rowSpan: 2 },
                        { text: 'TEMPAT', style: 'tableHeader', rowSpan: 2 },
                        { text: 'PENYELENGGARA', style: 'tableHeader', rowSpan: 2 },
                        { text: 'KETERANGAN', style: 'tableHeader', colSpan: 2 },
                        {},
                    ],
                    [
                        "", "", "", "", "",
                        { text: 'Tugas Pokok', style: 'tableHeader' },
                        { text: 'Tugas Tambahan', style: 'tableHeader', },
                    ],
                    ...logBook(data.logBook)
                ]
            }
         },
        ...logBookPerDay(data)
      ],
      styles: {
          header: {
              bold: true,
              fontSize: 15
          },
          tableHeader: {
            bold: true,
            fontSize: 12,
            color: 'black',
            fillColor: '#1aa3ff'
          },
          boldNormal: {
            bold: true,
            fontSize: 11
          }
      },
      defaultStyle: {
          fontSize: 12,
      }
  }

    return docDefinition
}

module.exports = {
  reportForm,
  generateReport,
  holidayType
}
