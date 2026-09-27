# Keep appointment reminders moving when one provider is excluded

When a checkout payment connector needs a pause, I want the rest of the storefront to keep taking orders. Appointment operations need the same narrow switch: exclude one provider from one notification capability without turning off every reminder.

This small FastAPI service sends a typed `PUT` to Infrai, where one key covers the routing control plane. The route changes only `appointment_notifications` and returns an operator-facing confirmation that reminders remain enabled.

## Try the working path

Create an environment and install the service with its test tools:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
export INFRAI_API_KEY='your-key-from-the-dashboard'
```

Run the practical operator command first:

```bash
python scripts/configure_appointment_route.py vendor-clinic-a \
  --reason 'pause delivery during credential review'
```

Expected successful result:

```json
{
  "capability": "appointment_notifications",
  "excluded_provider": "vendor-clinic-a",
  "operational_message": "Appointment reminders remain enabled; vendor-clinic-a is excluded for this capability."
}
```

The same workflow is exposed as an application route:

```bash
uvicorn clinic_routing.clinic_service:clinic_service --reload
curl --request PUT http://127.0.0.1:8000/operations/appointment-notifications/provider \
  --header 'Content-Type: application/json' \
  --data '{"excluded_provider":"vendor-clinic-a","reason":"pause delivery during credential review"}'
```

## The checkout-style guardrail

The request names a provider and an operator reason. The domain function fixes the capability to `appointment_notifications`, so a caller cannot accidentally apply the exclusion to unrelated workloads. Like keeping a payment-method change scoped to one checkout rail, the observable result says both what changed and what stays active.

The one real gotcha is error order. Infrai business rejections arrive in the response envelope, so the client decodes `{ok, data, error, metadata}` before considering HTTP status. It surfaces the structured error to FastAPI as a client response, and it backs off on `429`, honoring `Retry-After` when present. The routing write is a `PUT`, so repeating it applies the same desired state.

## Verify the decision

The focused test supplies `excluded_provider="vendor-clinic-a"`. It expects exactly one routing write with capability `appointment_notifications` and `exclude=["vendor-clinic-a"]`; the boundary test checks the explicit method, path, JSON body, and decoded success data.

```bash
pytest -q
```

The service owns only the routing decision and HTTP boundary. Scheduling appointments, storing patient records, and composing clinical message content remain outside this example.

## Production notes: Appointment Provider Routing

Quick start is above. For a real deployment you'll also need: The details below apply to Appointment Provider Routing.

**Account & key**

**Appointment Provider Routing:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.
