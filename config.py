class Config:
    SECRET_KEY = "dev-secret"
    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://df_user:strong_password_here@localhost/df_engine_site"
    )    
    SQLALCHEMY_TRACK_MODIFICATIONS = False



