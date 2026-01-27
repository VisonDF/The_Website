from db import db

class FunctionImpl(db.Model):
    __tablename__ = "function_impl"

    id = db.Column(db.Integer, primary_key=True)

    family_id = db.Column(
        db.Integer,
        db.ForeignKey("function_family.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    real_name = db.Column(db.String(128), nullable=False)
    api_level = db.Column(db.Enum("high", "low"), nullable=False, index=True)
    network   = db.Column(db.Boolean, nullable=False)
    gpu       = db.Column(db.Boolean, nullable=False)

    signature_html   = db.Column(db.Text)
    description_html = db.Column(db.Text)

    default_dataset_id = db.Column(
        db.Integer,
        db.ForeignKey("dataset.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    # Relationships
    family          = db.relationship("FunctionFamily", back_populates="impls")
    default_dataset = db.relationship("Dataset")

    benchmark = db.relationship(
        "Benchmark",
        back_populates="function_impl",
        cascade="all, delete-orphan",
        uselist=False,
        lazy=True,
    )



