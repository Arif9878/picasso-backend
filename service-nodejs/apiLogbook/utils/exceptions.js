const errors = {
    unauthorized: {
        code: 401,
        message: "Unauthorized",
    },
    forbidden: {
        code: 403,
        message: "Forbidden, You don't have enough permission to perform this action",
    },
    notFound: {
        code: 404,
        message: "Content Not Found",
    },
    serverError: {
        code: 500,
        message: "Internal Server Error",
    },
    tokenNotFound: {
        code: 401,
        message: "Token not found",
    },
    tokenExpired: {
        code: 401,
        message: "Token Expired",
    },
    validationError: {
        code: 422,
        message: "Input validation error",
    },
    evidenceError: {
        code: 422,
        message: "Image evidence isn't uploaded",
    },
    tupoksiNotFound: {
        code: 422,
        message: "Tupoksi Jabatan tidak ada",
    },
}

const success = {
    create: {
        code: 200,
        message: "Data created successfully",
    },
    update: {
        code: 200,
        message: "Data updated successfully",
    }
}
class APIError extends Error {
    constructor(props) {
        super(props)
        this.code = props.code || errors.serverError.code
        this.message = props.message || errors.serverError.message
        this.data = props.data || null
    }
}

module.exports = {
    errors,
    APIError
}
