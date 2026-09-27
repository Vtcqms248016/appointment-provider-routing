from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel, Field


APPOINTMENT_NOTIFICATION_CAPABILITY = "ai.rerank"


class RoutingWriter(Protocol):
    def set_routing(self, *, capability: str, exclude: list[str]) -> dict[str, Any]:
        """Store the routing preference and return its response data."""


class AppointmentRoutingRequest(BaseModel):
    excluded_provider: str = Field(min_length=1, max_length=120)
    reason: str = Field(min_length=1, max_length=240)


class AppointmentRoutingResult(BaseModel):
    capability: str
    excluded_provider: str
    operational_message: str


def protect_appointment_notifications(
    request: AppointmentRoutingRequest,
    client: RoutingWriter,
) -> AppointmentRoutingResult:
    client.set_routing(
        capability=APPOINTMENT_NOTIFICATION_CAPABILITY,
        exclude=[request.excluded_provider],
    )
    return AppointmentRoutingResult(
        capability=APPOINTMENT_NOTIFICATION_CAPABILITY,
        excluded_provider=request.excluded_provider,
        operational_message=(
            "Appointment reminders remain enabled; "
            f"{request.excluded_provider} is excluded for this capability."
        ),
    )
