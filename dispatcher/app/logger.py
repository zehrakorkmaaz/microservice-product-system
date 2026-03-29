from datetime import datetime

from app.db import logs_collection


class RequestLogger:
    def log(self, method, path, status_code, username=None, role=None,
            target_service=None, error_message=None, duration_ms=None):
        logs_collection.insert_one({
            "timestamp": datetime.utcnow().isoformat(),
            "method": method,
            "path": path,
            "status_code": status_code,
            "username": username,
            "role": role,
            "target_service": target_service,
            "error_message": error_message,
            "duration_ms": duration_ms
        })