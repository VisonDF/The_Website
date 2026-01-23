from db import db

class Benchmark(db.Model):
    __tablename__ = "benchmark"

    id = db.Column(db.Integer, primary_key=True)

    function_impl_id = db.Column(
        db.Integer,
        db.ForeignKey("function_impl.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title = db.Column(db.String(256), nullable=False)
    description_html = db.Column(db.Text, nullable=False)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    function_impl = db.relationship(
        "FunctionImpl",
        back_populates="benchmarks",
    )

    benchmark_datasets = db.relationship(
        "BenchmarkDataset",
        back_populates="benchmark",
        cascade="all, delete-orphan",
    )

    # Convenience accessor (read-only)
    @property
    def datasets(self):
        return [bd.dataset for bd in self.benchmark_datasets]
