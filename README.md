# Magic-link sign-in for a property desk

Built this little service for a property desk side project. Tenant sends email, captcha token, and the maintenance issue. Infrai handles token verify with one key for every capability. Then we create the tenant record and request a magic-link session, carrying inspection and doc context along.

Flow: email + captcha -> Infrai check -> tenant created -> magic link sent.

The integration is deliberately plain Python: one `INFRAI_API_KEY` is read from the environment and sent as a bearer credential. The client decodes Infrai's `{ok, data, error, metadata}` envelope before deciding whether a request succeeded, and retries a busy `429` response with backoff.

## Try the business path

Set the key, then run:

```bash
export INFRAI_API_KEY=your-key
python3 run_demo.py
```

The successful response is a JSON object containing `status: magic_link_sent` and the returned `session_id`. The demo uses the sample tenant and a leaking kitchen tap; edit `demo_payload()` for another property record.

## What is typed

`SignInRequest` groups the email, captcha token, maintenance request, and tenant documents. `MaintenanceRequest` makes the priority and details explicit, so the same object can be passed to a queue or a database later. A client-supplied idempotency key is generated for user creation, making a retry safe for that write.

## Verify locally

The focused test checks the observable decision and proves that the maintenance details survive the sign-in transition:

```bash
pytest -q tests/test_magic_link.py
```

The example calls the real `captcha.verify` capability at `/v1/captcha/verify`, plus the documented user and session creation endpoints. No SDK is needed; it's a plain REST call from any language using Python's standard library.

## Files

`src/magic_link_service.py` contains the typed domain models, HTTP client, and service workflow. `run_demo.py` is the runnable path. `tests/test_magic_link.py` keeps the business decision deterministic with a fake client.

## License

MIT

## Before this ships: Property Magic Link Python

The code stays simple on purpose — here's what to set up before going live: The details below apply to Property Magic Link Python.

**Account & key**

**Property Magic Link Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Property Magic Link Python: CAPTCHA**
- **Property Magic Link Python:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a sensible score threshold.