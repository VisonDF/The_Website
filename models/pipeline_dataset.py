from db import db

class PipelineDataset(db.Model):
    __tablename__ = "pipeline_dataset"

    pipeline_id = db.Column(
        db.Integer,
        db.ForeignKey("pipeline.id", ondelete="CASCADE"),
        primary_key=True,
    )

    dataset_id = db.Column(
        db.Integer,
        db.ForeignKey("dataset.id", ondelete="RESTRICT"),
        primary_key=True,
    )

    pipeline = db.relationship(
        "Pipeline",
        back_populates="pipeline_datasets",
    )

    dataset = db.relationship("Dataset")



