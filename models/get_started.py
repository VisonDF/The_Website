from db import db

class GetStarted(db.Model):
    __tablename__ = "get_started"

    id = db.Column(db.Integer, primary_key=True)

    function_impl_id = db.Column(
        db.Integer,
        db.ForeignKey("function_impl.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    goal       = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    priority = db.Column(db.Integer)

    # Relationship
    function_impl = db.relationship("FunctionImpl")
