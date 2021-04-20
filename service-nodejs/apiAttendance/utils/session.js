const moment = require('moment')
moment.locale('id')

module.exports = {
    onUpdated: (session) => ({
        updatedAt: new Date(moment().format()),
        updatedBy: {
            _id : session ? session.user_id : null,
            fullname: session ? session.fullname : null,
            email: session ? session.email : null,
            username: session ? session.username : null,
            divisi: session ? session.divisi : null,
            jabatan: session ? session.jabatan : null,
        },
        modifiedBy: session || null,
    }),
    onCreated : (session) => ({
        createdAt: new Date(moment().format()),
        createdBy: {
            _id : session ? session.user_id : null,
            fullname: session ? session.fullname : null,
            email: session ? session.email : null,
            username: session ? session.username : null,
            divisi: session ? session.divisi : null,
            jabatan: session ? session.jabatan : null,
        },
        modifiedBy: session || null,
    }),
    onCreatedClientApp : (session) => ({
        createdAt: new Date(moment().format()),
        createdBy: {
            _id : session ? session.id : null,
            email: session ? session.email : null,
            username: session ? session.username : null,
            divisi: session ? session.divisi : null,
            jabatan: session ? session.jabatan : null,
        },
        modifiedBy: session || null,
    }),
}
