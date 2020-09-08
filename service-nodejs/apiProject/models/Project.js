const mongoose = require('mongoose')
const Schema = mongoose.Schema
const attributes = require('./Attributes')

const Project = new Schema({
    projectName: {
        type: String,
        required: true,
        default: null
    },
    projectDescription: {
      type: String,
      required: false,
      default: null
    },
    ...attributes
})

Project.index({
  projectName: 1
})

module.exports = mongoose.models.LogBook || mongoose.model('Project', Project)
