from db import db

class Pipeline(db.Model):
    __tablename__ = "pipeline"

    id = db.Column(db.Integer, 
                   primary_key=True,
                   autoincrement=True)

    title            = db.Column(db.String(256), nullable=False)
    description_html = db.Column(db.Text, nullable=False)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    pipeline_datasets = db.relationship(
        "PipelineDataset",
        back_populates="pipeline",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin"
    )

    # Convenience accessor (read-only)
    @property
    def datasets(self):
        return [bd.dataset for bd in self.pipeline_datasets]




