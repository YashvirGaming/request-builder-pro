# SUCCESS indicators
SUCCESS_KEYWORDS = [
"access_token",
"id_token",
"refresh_token",
"token",
"auth_token",
"session",
"session_id",
"sessionId",
"bearer",
"jwt",
"jwt_token",
"authorization",
"authorized",
"authenticated",
"login_success",
"logged_in",
"success",
"status\":\"ok",
"status\":\"success",
"user_id",
"account_id",
"profile",
"dashboard",
"welcome",
"api_key",
"credential",
"grant",
"granted"
]


# FAILURE indicators
FAILURE_KEYWORDS = [
"invalid",
"invalid_password",
"invalid_credentials",
"incorrect_password",
"incorrect",
"wrong_password",
"login_failed",
"authentication_failed",
"unauthorized",
"forbidden",
"access_denied",
"denied",
"invalid_token",
"expired_token",
"expired",
"error",
"failed",
"user_not_found",
"account_locked",
"captcha_required"
]


# RETRY indicators
RETRY_KEYWORDS = [
"rate_limit",
"too_many_requests",
"retry_later",
"temporarily_unavailable",
"server_busy",
"timeout",
"service_unavailable",
"slow_down"
]


# TOKEN field names
TOKEN_FIELDS = [
"csrf",
"csrf_token",
"_csrf",
"csrfmiddlewaretoken",
"_token",
"xsrf",
"_xsrf",
"authenticity_token",
"access_token",
"id_token",
"refresh_token",
"api_token",
"api_key"
]

# SESSION COOKIE names (very common across websites)
SESSION_COOKIES = [
"session",
"sessionid",
"session_id",
"sid",
"auth_session",
"user_session",
"secure_session",
"connect.sid",
"phpsessid",
"jsessionid",
"laravel_session",
"csrftoken",
"token",
"access_token",
"refresh_token",
"remember_token",
"remember_me",
"logged_in",
"auth",
"authorization",
"user_token",
"jwt",
"jwt_token"
]

# AUTO SUCCESS TOKEN detection (used by code generator)
AUTO_SUCCESS_TOKENS = [
"access_token",
"id_token",
"refresh_token",
"jwt",
"jwt_token",
"session",
"sessionid",
"session_id",
"csrftoken",
"csrf_token",
"auth_token",
"bearer",
"authorization",
"api_key",
"user_id",
"account_id"
]