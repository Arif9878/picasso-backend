const sharp = require('sharp')
const moment = require('moment')

function encode(input) {
    const keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
    let output = ""
    let chr1, chr2, chr3, enc1, enc2, enc3, enc4
    let i = 0

    while (i < input.length) {
        chr1 = input[i++]
        chr2 = i < input.length ? input[i++] : Number.NaN // Not sure if the index 
        chr3 = i < input.length ? input[i++] : Number.NaN // checks are needed here

        enc1 = chr1 >> 2
        enc2 = ((chr1 & 3) << 4) | (chr2 >> 4)
        enc3 = ((chr2 & 15) << 2) | (chr3 >> 6)
        enc4 = chr3 & 63;

        if (isNaN(chr2)) {
            enc3 = enc4 = 64
        } else if (isNaN(chr3)) {
            enc4 = 64
        }
        output += keyStr.charAt(enc1) + keyStr.charAt(enc2) +
            keyStr.charAt(enc3) + keyStr.charAt(enc4)
    }
    return output
}

function imageResize(input) {
    return sharp(input, {
            failOnError: false
        })
        .resize({
            width: 350,
            fit: sharp.fit.contain,
        })
        .png({
            compressionLevel: 9,
            quality: 85,
            adaptiveFiltering: true,
            force: true
        })
        .toBuffer()
}

function getListWeekend(start_date, end_date) {
    let list_weekend = []
    for (var d = new Date(start_date); d < new Date(end_date); d.setDate(d.getDate() + 1)) {
        if (d.getDay() === 6 || d.getDay() === 0) {
            list_weekend.push({
                'dateTask':moment(d).format('YYYY-MM-DDTHH:mm:ssZ'),
                'nameTask': 'LIBUR'
            })
        }
    }
    return list_weekend;
}

module.exports = {
    encode,
    imageResize,
    getListWeekend
}
