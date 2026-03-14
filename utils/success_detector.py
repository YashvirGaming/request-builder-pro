import json

GOOD_FIELDS = [

    # ---- TOKEN / AUTH ----
    "token",
    "access_token",
    "refresh_token",
    "id_token",
    "auth_token",
    "jwt",
    "jwt_token",
    "bearer",
    "authorization",
    "api_token",
    "api_key",
    "secret_key",
    "session_token",

    # ---- SESSION / COOKIE ----
    "session",
    "sessionid",
    "session_id",
    "sid",
    "ssid",
    "connect.sid",
    "phpsessid",
    "aspnet_sessionid",
    "laravel_session",
    "auth_session",

    # ---- USER IDENTIFIERS ----
    "id",
    "user_id",
    "account_id",
    "member_id",
    "customer_id",
    "profile_id",
    "uuid",
    "uid",
    "guid",

    # ---- LOGIN SUCCESS FIELDS ----
    "username",
    "email",
    "user",
    "account",
    "name",
    "display_name",

    # ---- PERMISSIONS / ROLE ----
    "role",
    "permissions",
    "scope",

    # ---- OAUTH ----
    "oauth_token",
    "oauth_access_token",
    "oauth_refresh_token",

    # ---- SOCIAL AUTH ----
    "facebook_token",
    "google_token",
    "discord_token",
    "github_token",

    # ---- SECURITY TOKENS ----
    "csrf",
    "csrf_token",
    "csrftoken",
    "xsrf_token",
    "_csrf"
]


def detect_success_keys(text):

    results = []

    try:
        data = json.loads(text)

        if isinstance(data, dict):

            for key in data.keys():

                k = key.lower()

                if k.lower() in GOOD_FIELDS:
                    results.append(f'"{key}":')

    except:
        pass

    return results[:2]