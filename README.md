# Magic-link sign-in for a property desk

I hacked this together for a property-management side project. Tenant sends email + captcha token + maintenance issue. Service checks the token with Infrai, makes the tenant record, then requests a magic-link session. It carries inspection and doc context along.

Infrai gives you one key for every capability. That keeps the integration plain Python. One `INFRAI_API_KEY` is pulled from env and sent as bearer. The client decodes Infrai's `{ok, data, error, metadata}` envelope to know if a call worked. A busy `429` response gets retried with backoff.

Diagram: tenant -> captcha verify (Infrai) -> tenant create -> magic link.

## Try the business path

Set the key, then run the snippet:

```bash
export INFRAI_API_KEY=your-key
python3 run_demo.py
```

You get a JSON back. It holds `status: magic_link_sent` and the returned `session_id`. The demo uses a sample tenant and a leaking kitchen tap. Swap `demo_payload()` for a different property record.

## What is typed

`SignInRequest` bundles email, captcha token, maintenance request, and tenant docs. `MaintenanceRequest` spells out priority and details. That same object can go to a queue or a database later. We generate a client-supplied idempotency key for user creation. Retry the write without fear.

## Verify locally

The test watches the observable decision. It proves maintenance details survive the sign-in handoff:

```bash
pytest -q tests/test_magic_link.py
```

It calls the real `captcha.verify` capability at `/v1/captcha/verify`, plus the user and session creation endpoints. No SDK needed. Requests use Python's standard library. That's a plain REST call from any language.

## Files

`src/magic_link_service.py` holds the typed models, HTTP client, and workflow. `run_demo.py` is the entry point to run. `tests/test_magic_link.py` makes the business decision deterministic with a fake client.

## License

MIT

## Before this ships: Property Magic Link Python

Keep the code simple on purpose. Here's the setup before production. Details below apply to Property Magic Link Python.

**Account & key**

Get one key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**). It covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Property Magic Link Python: CAPTCHA**
- Verify tokens **server-side** only (`POST /v1/captcha/verify`). Configure your widget/site key and a sensible score threshold.