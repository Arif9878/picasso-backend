const BAB_2 = (data) => {
    const { user, jabatan } = data
    return [
        {
            alignment: 'center',
            bold: true,
            text: [
                    'BAB II \n',
                    'RUANG LINGKUP & DESKRIPSI PEKERJAAN\n\n'    
            ]   
        },
        {
            alignment: 'justify',
            preserveLeadingSpaces: true,
            text: [
                '        Ruang lingkup pekerjaan adalah Pengelolaan Layanan Digital di Pemerintah Provinsi Jawa Barat yang terbagi kedalam 5 bidang, yakni:  \n'    
            ]
        },
        {
            ol: [
                'Bidang Komunikasi dan Konten',
                'Bidang Implementasi dan Pengelolaan',
                'Bidang Data',
                'Bidang Pengembangan TIK dan',
                'Bidang Analisis.\n\n'
            ]
        },
        { 
            text: 'Untuk merealisasikan ruang lingkup pekerjaan diatas, sebagai tim pengelola layanan digital, Saya :' 
        },
        {
            
            columns: [
                {},
                {
                    width: 415,
                    preserveLeadingSpaces: true,
                    text: [ 
                        `Nama    : ${user.first_name} ${user.last_name} \n`,
                        `Role       : ${user.jabatan} \n`,
                        `Bidang  : ${user.divisi}`
                        ],
                }
            ]
        },

        {
            text: 'Memiliki Uraian Pekerjaan Sebagai Berikut :'
        },
        {
            type: 'lower-alpha',
            ol: [
                ...jabatan,
                'Melaksanakan tugas lain di luar uraian pekerjaan yang tidak sesuai tugas pokok dan fungsi\n\n'
            ],
            pageBreak: 'after'
        }
    ]
}

module.exports = {
    BAB_2
}