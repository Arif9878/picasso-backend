function getRandomString(length) {
  let randomString = ''
  do {
    randomString += Math.random().toString(36).substr(2)
  } while (randomString.length < length)

  randomString = randomString.substr(0, length)

  return randomString
}

module.exports = {
    getRandomString
}
