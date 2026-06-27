# Security and Privacy

Report vulnerabilities privately through GitHub’s security reporting channel when available.

The sample treats the AdServices token and attribution response as sensitive, short-lived data:

- attribution is user-triggered and never requested during launch;
- the token and response are not persisted, cached, uploaded elsewhere, or logged;
- the session is ephemeral with cookies, credential storage, and URL caching disabled;
- only Apple’s fixed HTTPS endpoint is used;
- every HTTP redirect is rejected before URLSession can forward the attribution token;
- request and resource timeouts are bounded;
- response status, JSON MIME type, 64 KiB size, and strict Boolean schema are validated;
- only `404` and `500` responses retry, with three total attempts and bounded delays;
- lifecycle cancellation and request generations reject late or duplicate completions.

Coordinator startup rejects and cancels timeout or request handles returned after a synchronous terminal callback.

Native tests use `URLProtocol` mocks only. They do not generate a real token or contact Apple. A live physical-device test may expose campaign metadata to the app process; never capture that data in screenshots, logs, crash reports, analytics, or issue attachments.
