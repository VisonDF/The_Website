from datetime import timedelta

class Config:
    SECRET_KEY = "dev-secret"
    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://df_user:strong_password_here@localhost/df_engine_site"
    )    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_PERMANENT=True
    PERMANENT_SESSION_LIFETIME=timedelta(hours=80)

    SESSION_COOKIE_NAME="visondf_session"
    SESSION_COOKIE_HTTPONLY=True
    SESSION_COOKIE_SAMESITE="Lax"
    SESSION_COOKIE_SECURE=False  # True in HTTPS

    REMEMBER_COOKIE_DURATION=timedelta(0)



