const sharp = require('sharp')
const servers_nats = [process.env.NATS_URI]
const nats = require('nats').connect({
    'servers': servers_nats
})

const URL = require("url").URL;

const stringIsAValidUrl = (s) => {
  try {
    new URL(s);
    return true;
  } catch (err) {
    return false;
  }
};

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

function getTupoksiJabatanDetail(Id) {
    return new Promise(resolve => {
        nats.request('TupoksiJabatanDetail',String(Id), function(resp) {
            resolve(JSON.parse(resp))
            nats.unsubscribe(this._sid)
        })
    })
}

module.exports = {
    encode,
    imageResize,
    getTupoksiJabatanDetail,
    stringIsAValidUrl
}
