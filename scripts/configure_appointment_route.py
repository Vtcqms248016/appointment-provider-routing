from __future__ import annotations

import argparse
import json
import os

from clinic_routing.appointment_notifications import (
    AppointmentRoutingRequest,
    protect_appointment_notifications,
)
from clinic_routing.infrai_client import InfraiClient


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("provider", help="provider identifier to exclude")
    parser.add_argument("--reason", required=True, help="operator note for this change")
    args = parser.parse_args()

    api_key = os.environ.get("INFRAI_API_KEY")
    if not api_key:
        raise SystemExit("Set INFRAI_API_KEY before running this command.")

    client = InfraiClient(api_key)
    try:
        result = protect_appointment_notifications(
            AppointmentRoutingRequest(
                excluded_provider=args.provider,
                reason=args.reason,
            ),
            client,
        )
        print(json.dumps(result.model_dump(), indent=2))
    finally:
        client.close()


if __name__ == "__main__":
    main()

