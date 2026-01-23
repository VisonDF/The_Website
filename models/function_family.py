from db import db

class FunctionFamily(db.Model):
    __tablename__ = "function_family"

    id           = db.Column(db.Integer, primary_key=True)
    slug         = db.Column(db.String(64), nullable=False, unique=True)
    display_name = db.Column(db.String(128), nullable=False)
    description  = db.Column(db.Text)  # HTML allowed
    created_at   = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    # One family -> many implementations
    impls = db.relationship(
        "FunctionImpl",
        back_populates="family",
        cascade="all, delete-orphan",
        lazy=True,
    )


