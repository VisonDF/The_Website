from db import db

class BenchmarkDataset(db.Model):
    __tablename__ = "benchmark_dataset"

    benchmark_id = db.Column(
        db.Integer,
        db.ForeignKey("benchmark.id", ondelete="CASCADE"),
        primary_key=True,
    )

    dataset_id = db.Column(
        db.Integer,
        db.ForeignKey("dataset.id", ondelete="RESTRICT"),
        primary_key=True,
    )

    benchmark = db.relationship(
        "Benchmark",
        back_populates="benchmark_datasets",
    )

    dataset = db.relationship("Dataset")
