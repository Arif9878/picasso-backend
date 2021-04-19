const egLogger = require('express-gateway/lib/logger')
const request = require("request")

module.exports = {
  version: '0.0.1',
  init: function (pluginContext) {

    const kcConfig = pluginContext.settings.kcConfigParams
    const logger = egLogger.createLoggerWithLabel('[EG:plugins:keycloak]')  

    pluginContext.registerGatewayRoute(() => {
      logger.debug('Register',pluginContext)
      logger.info('Registering keycloak middleware')
    })

    pluginContext.registerPolicy({
      name: 'keycloak-protect',
      schema: {
        $id: 'http://express-gateway.io/schemas/policy/keycloak-protect-policy.json',
        type: 'object',
        properties: {
        roles: {
            type: 'string'
          }
        }
      },
      policy: (actionParams) => {
        return (req, res, next) => {
            if (req.headers.authorization) {
                // configure the request to your keycloak server
                const options = {
                    method: 'GET',
                    url: `${kcConfig.authServerUrl}realms/${kcConfig.realm}/protocol/openid-connect/userinfo`,
                    headers: {
                        // add the token you received to the userinfo request, sent to keycloak
                        Authorization: req.headers.authorization,
                    },
                };
            
                // send a request to the userinfo endpoint on keycloak
                request(options, (error, response, body) => {
                    if (error) throw new Error(error);
                    console.log(body)
                    // if the request status isn't "OK", the token is invalid
                    if (response.statusCode !== 200) {
                        res.status(401).json({
                            error: `unauthorized`,
                        });
                    }
                    // the token is valid pass request onto your next function
                    else {
                        next();
                    }
                });
            } else {
                // there is no token, don't process request further
                res.status(401).json({
                    error: `unauthorized`,
                });
            }
        }
      },
    })
  },
  policies:['keycloak-protect'], 
  schema: {
    $id: 'http://express-gateway.io/schemas/plugin/keycloak-connect.json',
    kcConfigParams: {
      title: 'keycloak-connect config parameters',
      description: 'Parameters in case no config file exists',
      type: 'object'
    },
    required:[]
  }
};
