from fastapi import FastAPI, Request
from pydantic import BaseModel
import pickle
import numpy as np
import logging
import json
import time

from opentelemetry import trace, metrics
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.trace import SpanKind


# --------------------------
# JSON Logging Setup
# --------------------------
class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(log_entry)

logger = logging.getLogger("house-price-service")
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# --------------------------
# OpenTelemetry Tracing
# --------------------------
resource = Resource(attributes={"service.name": "house-price-service"})

# Tracer setup
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

span_exporter = OTLPSpanExporter()
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(span_exporter))

# Metrics setup
metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter())
metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[metric_reader]))
meter = metrics.get_meter(__name__)

# Metrics
api_counter = meter.create_counter(
    name="api_requests_total",
    unit="1",
    description="Total number of API requests",
)

api_latency = meter.create_histogram(
    name="api_latency_seconds",
    unit="s",
    description="API response latency in seconds",
)

# --------------------------
# FastAPI App Setup
# --------------------------
app = FastAPI()
FastAPIInstrumentor().instrument_app(app)
LoggingInstrumentor().instrument(set_logging_format=True)

# Load the model
with open("house_price_model.pkl", "rb") as f:
    model = pickle.load(f)

@app.get("/")
def read_root(request: Request):
    start_time = time.time()
    with tracer.start_as_current_span("GET /", kind=SpanKind.SERVER):
        logger.info("Health check hit")
        api_counter.add(1, {"endpoint": "/", "method": "GET"})
        api_latency.record(time.time() - start_time, {"endpoint": "/", "method": "GET"})
        return {"message": "House Price Prediction API is live!"}

class HouseFeatures(BaseModel):
    features: list[float]

@app.post("/predict/")
def predict(data: HouseFeatures, request: Request):
    start_time = time.time()
    with tracer.start_as_current_span("POST /predict", kind=SpanKind.SERVER) as span:
        span.set_attribute("input.features", str(data.features))
        api_counter.add(1, {"endpoint": "/predict", "method": "POST"})

        prediction = model.predict(np.array(data.features).reshape(1, -1))
        logger.info(f"Prediction made: {prediction[0]}")

        api_latency.record(time.time() - start_time, {"endpoint": "/predict", "method": "POST"})
        return {"predicted_price": prediction[0]}
