from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException

from .appointment_notifications import (
    AppointmentRoutingRequest,
    AppointmentRoutingResult,
    protect_appointment_notifications,
)
from .infrai_client import InfraiClient, InfraiError


clinic_service = FastAPI(title="Appointment notification routing")


@clinic_service.put(
    "/operations/appointment-notifications/provider",
    response_model=AppointmentRoutingResult,
)
def update_appointment_provider(
    request: AppointmentRoutingRequest,
) -> AppointmentRoutingResult:
    api_key = os.environ.get("INFRAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="INFRAI_API_KEY is not configured")

    client = InfraiClient(api_key)
    try:
        return protect_appointment_notifications(request, client)
    except InfraiError as error:
        client_status = error.status_code if 400 <= error.status_code < 500 else 502
        raise HTTPException(
            status_code=client_status,
            detail={"code": error.code, "message": str(error.details.get("message", error))},
        ) from error
    finally:
        client.close()

