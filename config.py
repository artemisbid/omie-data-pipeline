from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


def _read_int(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None or raw_value.strip() == "":
        return default
    return int(raw_value)


@dataclass(frozen=True, slots=True)
class AppConfig:
    omie_app_key: str
    omie_app_secret: str
    omie_company_id: str | None
    supabase_url: str
    supabase_service_role_key: str
    raw_data_dir: Path
    http_timeout: int = 30
    http_max_retries: int = 3
    load_batch_size: int = 500
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            omie_app_key=os.getenv("OMIE_APP_KEY", "").strip(),
            omie_app_secret=os.getenv("OMIE_APP_SECRET", "").strip(),
            omie_company_id=os.getenv("OMIE_COMPANY_ID", "").strip() or None,
            supabase_url=os.getenv("SUPABASE_URL", "").strip(),
            supabase_service_role_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip(),
            raw_data_dir=Path(os.getenv("RAW_DATA_DIR", "data/raw")),
            http_timeout=_read_int("HTTP_TIMEOUT", 30),
            http_max_retries=_read_int("HTTP_MAX_RETRIES", 3),
            load_batch_size=_read_int("LOAD_BATCH_SIZE", 500),
            log_level=os.getenv("LOG_LEVEL", "INFO").strip() or "INFO",
        )

    def validate_extract_config(self) -> None:
        missing = []
        if not self.omie_app_key:
            missing.append("OMIE_APP_KEY")
        if not self.omie_app_secret:
            missing.append("OMIE_APP_SECRET")
        if missing:
            joined = ", ".join(missing)
            raise ValueError(f"Missing required environment variables: {joined}")

    def validate_load_config(self) -> None:
        missing = []
        if not self.supabase_url:
            missing.append("SUPABASE_URL")
        if not self.supabase_service_role_key:
            missing.append("SUPABASE_SERVICE_ROLE_KEY")
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
