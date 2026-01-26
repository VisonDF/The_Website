from db import db

class Dev(db.Model):
    __tablename__ = "dev"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    title = db.Column(db.String(256), nullable=False)

    description_html = db.Column(db.Text, nullable=False)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        nullable=False
    )


