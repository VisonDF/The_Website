from db import db

class Dataset(db.Model):
    __tablename__ = "dataset"

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(128), nullable=False)
    version      = db.Column(db.String(32), nullable=False)
    description  = db.Column(db.Text)
    download_url = db.Column(db.String(512))
    created_at   = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    __table_args__ = (
        db.UniqueConstraint("name", "version", name="uq_dataset_name_version"),
    )
