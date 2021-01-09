from keycloak import KeycloakOpenID

from .settings import (
        KEYCLOAK_URL,
        KEYCLOAK_CLIENT_ID,
        KEYCLOAK_REALM_NAME,
        KEYCLOAK_CLIENT_SECRET_KEY
    )

# Configure client
keycloak_openid = KeycloakOpenID(
                    server_url=KEYCLOAK_URL,
                    client_id=KEYCLOAK_CLIENT_ID,
                    realm_name=KEYCLOAK_REALM_NAME,
                    client_secret_key=KEYCLOAK_CLIENT_SECRET_KEY
                )

def userinfo_keycloak(access_token):
    # Get Userinfo
    userinfo = keycloak_openid.userinfo(access_token)