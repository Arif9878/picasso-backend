const moment = require('moment')
moment.locale('id')
module.exports = {
    onUpdated: (session) => ({
        updatedAt: new Date(moment().format()),
        updatedBy: {
            _id : session ? session.user_id : null,
            email: session ? session.email : null,
            username: session ? session.username : null,
            divisi: session ? session.divisi : null,
            jabatan: session ? session.jabatan : null,
        },
        modifiedBy: session || null,
    }),
    onCreated : (session) => ({
        createdBy: {
            _id : session ? session.user_id : null,
            email: session ? session.email : null,
            username: session ? session.username : null,
            divisi: session ? session.divisi : null,
            jabatan: session ? session.jabatan : null,
        },
        modifiedBy: session || null,
    }),
    filePath: (file) => ({
        filePath: file ? file.filePath : null,
        fileURL: file ? file.fileURL : null,
        fileBlob: file ? file.fileBlob : null,
    }),
}
