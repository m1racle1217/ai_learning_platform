import os
import time
from dataclasses import dataclass, field


@dataclass
class RuntimeLifecycle:
    enabled: bool
    idle_seconds: float = 20.0
    started_at: float = field(default_factory=time.monotonic)
    last_heartbeat_at: float | None = None

    def heartbeat(self) -> None:
        self.last_heartbeat_at = time.monotonic()

    def should_shutdown(self) -> bool:
        if not self.enabled:
            return False
        now = time.monotonic()
        last_seen = self.last_heartbeat_at or self.started_at
        return now - last_seen > self.idle_seconds


_lifecycle = RuntimeLifecycle(enabled=False)


def get_lifecycle() -> RuntimeLifecycle:
    return _lifecycle


def configure_auto_shutdown(idle_seconds: float | None = None) -> RuntimeLifecycle:
    global _lifecycle
    configured_idle = idle_seconds
    if configured_idle is None:
        configured_idle = float(os.getenv("AI_LEARNING_IDLE_SHUTDOWN_SECONDS", "20"))
    _lifecycle = RuntimeLifecycle(enabled=True, idle_seconds=configured_idle)
    return _lifecycle
