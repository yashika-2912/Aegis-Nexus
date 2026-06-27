from backend.services.telemetry_service import TelemetryService
from backend.storage.metrics_cache import telemetry_store

sample_application = TelemetryService(telemetry_store)
