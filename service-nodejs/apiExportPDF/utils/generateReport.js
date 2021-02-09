const fs = require('fs')
const PdfPrinter = require('pdfmake')
const moment = require('moment')
moment.locale('id')
const dayOffType = ['CUTI', 'SAKIT', 'IZIN']
const holidayType = ['Libur Nasional', 'Cuti Bersama']
const { Cover } = require('./templateReport/Cover')
const { BAB_1 } = require('./templateReport/Bab-1')
const { BAB_2 } = require('./templateReport/Bab-2')
const { BAB_3 } = require('./templateReport/Bab-3')
const { penutup } = require('./templateReport/Penutup')

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
    const { jabatan } = data
    data['logBook'].forEach((item, index) => {
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
                    text: jabatan.includes(item.tupoksiJabatanName) ? '√' : ''
                },
                {
                    text: !jabatan.includes(item.tupoksiJabatanName) ? '√' : ''
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
            pageBreak: 'before',
            pageOrientation: 'landscape',
            text: 'B. Evidence Foto Kegiatan Kinerja Harian'
        },
        {
            fontSize: 11,
            preserveLeadingSpaces: true,
            text: '         Berikut adalah evidence daftar uraian kegiatan harian yang didetailkan setiap harinya dibulan ini.'
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
      pageMargins: [ 90, 60, 40, 60 ],
      content: [
          ...Cover(data),
          ...BAB_1,
          ...BAB_2(data),
          ...BAB_3(data),
          ...penutup,
          // BODY   
          {
              alignment: 'center',
              bold: true,
              fontSize: 11,
              pageBreak: 'before',
              pageOrientation: 'landscape',
              color: 'black',
              text: 'LAMPIRAN',
          },
         {
            margin: [0, 10, 0, 0],
            text: `A. Laporan Kerja Harian ${month.toUpperCase()}`,
         },
         {
            margin: [0, 10, 0, 0],
            text: `Berikut daftar laporan kerja harian  ${month.toUpperCase()}`,
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
                    ...logBook(data)
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
