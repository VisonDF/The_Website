from datetime import timedelta

class Config:
    SECRET_KEY = "devSDMSZE343DF"
    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://df_user:pLM45!LqlpZ@localhost/df_engine_site"
    )    

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,          # persistent connections
        "max_overflow": 20,       # burst capacity
        "pool_recycle": 1800,     # avoid MySQL timeout issues
        "pool_pre_ping": True,    # auto-reconnect dead conns
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_PERMANENT=True
    PERMANENT_SESSION_LIFETIME=timedelta(hours=80)

    SESSION_COOKIE_NAME="visondf_session"
    SESSION_COOKIE_HTTPONLY=True
    SESSION_COOKIE_SAMESITE="Lax"
    SESSION_COOKIE_SECURE=False  # True in HTTPS

    REMEMBER_COOKIE_DURATION=timedelta(0)



