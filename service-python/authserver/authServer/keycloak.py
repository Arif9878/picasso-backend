from keycloak import KeycloakOpenID, KeycloakAdmin

from .settings import (
        KEYCLOAK_URL,
        KEYCLOAK_CLIENT_ID,
        KEYCLOAK_REALM_NAME,
        KEYCLOAK_USERNAME_ADMIN,
        KEYCLOAK_PASSWORD_ADMIN,
        KEYCLOAK_CLIENT_SECRET_KEY
    )

# Configure client
keycloak_openid = KeycloakOpenID(
                    server_url=KEYCLOAK_URL,
                    client_id=KEYCLOAK_CLIENT_ID,
                    realm_name=KEYCLOAK_REALM_NAME,
                    client_secret_key=KEYCLOAK_CLIENT_SECRET_KEY
                )

# Configure admin
keycloak_admin =  KeycloakAdmin(
                    server_url=KEYCLOAK_URL,
                    username=KEYCLOAK_USERNAME_ADMIN,
                    password=KEYCLOAK_PASSWORD_ADMIN,
                    realm_name=KEYCLOAK_REALM_NAME,
                    verify= True)

# Get Userinfo
def userinfo_keycloak(access_token):
    userinfo = keycloak_openid.userinfo(access_token)
    return userinfo

# Get user ID from email
def get_keycloak_user_id(email):
    keycloak_user_id = keycloak_admin.get_user_id(email)
    return keycloak_user_id

# Add user and set password
def add_new_user_keycloak(data):
    new_user = keycloak_admin.create_user({"email": data["email"],
                        "username": data["username"],
                        "enabled": True,
                        "firstName": data["first_name"],
                        "lastName": data["last_name"],
                        "realmRoles": ["user_default", ]})
    return new_user

# # Update User
def update_user_keycloak(data):
    keycloak_user_id = get_keycloak_user_id(data['email'])
    update_user = keycloak_admin.update_user(user_id=keycloak_user_id, 
                                      payload={
                                        "email": data['email'],
                                        "username": data["username"],
                                        "firstName": data['first_name'],
                                        "lastName": data['last_name']
                                      })

    return update_user

# Update User Password
def set_user_password(keycloak_user_id, password):
    response = keycloak_admin.set_user_password(user_id=keycloak_user_id, password=password, temporary=False)
    return response
   
# Send Verify Email
def send_verify_email(keycloak_user_id):
    response = keycloak_admin.send_verify_email(user_id=keycloak_user_id)
    return response

# Check user detail by access token
def is_user_email_verified_by_token(access_token):
    userinfo = keycloak_openid.userinfo(access_token)
    is_verified = userinfo['email_verified']
    return is_verified

# Check user email by access token
def is_user_email_verified_by_email(email):
    user_id_keycloak = keycloak_admin.get_user_id(email)
    userinfo = keycloak_admin.get_user(user_id_keycloak)
    is_verified = userinfo['emailVerified']
    return is_verified
   