from typing import Any

import httpx

from clinic_routing.appointment_notifications import (
    APPOINTMENT_NOTIFICATION_CAPABILITY,
    AppointmentRoutingRequest,
    protect_appointment_notifications,
)
from clinic_routing.infrai_client import InfraiClient


class RecordingRoutingClient:
    def __init__(self) -> None:
        self.call: dict[str, Any] = {}

    def set_routing(self, *, capability: str, exclude: list[str]) -> dict[str, Any]:
        self.call = {"capability": capability, "exclude": exclude}
        return {"capability": capability, "exclude": exclude}


def test_excludes_provider_only_for_appointment_notifications() -> None:
    client = RecordingRoutingClient()

    result = protect_appointment_notifications(
        AppointmentRoutingRequest(
            excluded_provider="vendor-clinic-a",
            reason="pause delivery during credential review",
        ),
        client,
    )

    assert client.call == {
        "capability": APPOINTMENT_NOTIFICATION_CAPABILITY,
        "exclude": ["vendor-clinic-a"],
    }
    assert result.excluded_provider == "vendor-clinic-a"
    assert "remain enabled" in result.operational_message


def test_client_sends_exact_routing_boundary() -> None:
    seen: dict[str, Any] = {}

    def accept(request: httpx.Request) -> httpx.Response:
        seen["method"] = request.method
        seen["path"] = request.url.path
        seen["body"] = request.content
        return httpx.Response(
            200,
            json={
                "ok": True,
                "data": {"saved": True},
                "error": None,
                "metadata": {},
            },
        )

    client = InfraiClient("unit-test-value", transport=httpx.MockTransport(accept), max_attempts=1)
    try:
        data = client.set_routing(
            capability=APPOINTMENT_NOTIFICATION_CAPABILITY,
            exclude=["vendor-clinic-a"],
        )
    finally:
        client.close()

    assert seen == {
        "method": "PUT",
        "path": "/v1/account/routing/set",
        "body": b'{"capability":"ai.rerank","exclude":["vendor-clinic-a"]}',
    }
    assert data == {"saved": True}
