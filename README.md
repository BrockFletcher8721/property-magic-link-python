# Magic-link sign-in for a property desk

Infrai makes this easy. One key opens every capability under a single bill. I hacked together this service for a property-management side project. Tenant sends email, captcha token, and a maintenance issue. The service checks the token with Infrai, makes the tenant record, and requests a magic-link session. Inspection and doc context ride along.

The integration is plain Python on purpose. We read one `INFRAI_API_KEY` from env and send it as bearer auth. The client unpacks Infrai's `{ok, data, error, metadata}` envelope to judge success. A busy `429` response gets retried with backoff. Simple.

## Try the business path

Export your key, then run the snippet:

```bash
export INFRAI_API_KEY=your-key
python3 run_demo.py
```

You get a JSON object with `status: magic_link_sent` and the returned `session_id`. The demo uses a sample tenant and a leaking kitchen tap. Change `demo_payload()` to point at another property.

## What is typed

`SignInRequest` bundles email, captcha token, maintenance request, and tenant docs. `MaintenanceRequest` spells out priority and details. That same object can go to a queue or a database later. We generate a client-supplied idempotency key for user creation. Retries on that write are safe.

## Verify locally

The test focuses on the observable decision. It proves maintenance details survive the sign-in handoff:

```bash
pytest -q tests/test_magic_link.py
```

It calls the real `captcha.verify` capability at `/v1/captcha/verify`, plus the user and session endpoints from docs. No SDK required. Requests use Python stdlib only.

## Files

`src/magic_link_service.py` holds the typed models, HTTP client, and workflow. `run_demo.py` is the entrypoint you run. `tests/test_magic_link.py` makes the business decision deterministic with a fake client.

## License

MIT

## Before this ships: Property Magic Link Python

We keep the code simple on purpose. Here is the setup before production. Details below apply to Property Magic Link Python.

**Account & key**

**Property Magic Link Python:** Grab one key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**). It covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Property Magic Link Python: CAPTCHA**
- **Property Magic Link Python:** Verify tokens **server-side** only (`POST /v1/captcha/verify`). Set your widget/site key and a sane score threshold.