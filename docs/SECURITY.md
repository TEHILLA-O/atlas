# Security

Atlas treats models as untrusted reasoners and retrieved text as untrusted data.

## Prompt injection

Uploaded documents and web pages can contain instructions such as "ignore previous instructions". Atlas:

- Isolates retrieved text in `<untrusted_source>` wrappers.
- Flags common injection patterns.
- Tells agents to treat enclosed text as data only.
- Never promotes conversation history into long-term memory automatically.

This reduces risk; it does not make injection impossible.

## Tool abuse and least privilege

Agents receive only the tools they need:

| Agent | Tools |
| --- | --- |
| Planner | none |
| Researcher | `web_search`, `fetch_web_page`, `calculator` |
| Document analyst | `search_documents`, `retrieve_document_chunks` |
| Verifier / critic / synthesiser | none |

Unknown tool names are rejected by the registry.

## URL and SSRF controls

`fetch_web_page` rejects:

- Non-http(s) schemes
- Localhost and blocked hosts
- Private and link-local IP addresses, including cloud metadata ranges

## Uploads

- Extension and content-type allow-lists
- File size limit (`ATLAS_MAX_UPLOAD_MB`)
- Filename sanitisation
- HTML sanitisation before text extraction

## Secrets

- Settings use `SecretStr`
- Structured logs redaction for `api_key`, `token`, `password`, `secret`
- `.env` is gitignored; only `.env.example` is committed
- LangSmith keys are never returned by the API

## Document trust boundary

Private documents are isolated from public web evidence in metadata. Company memos are scored as `COMPANY_SOURCE`, not as government publications. Instructions inside documents are not executed as tools.

## Logging

Request IDs and correlation IDs are attached to every request. Secrets are stripped before emission.

## Residual risk

LLM systems can still be socially engineered. Atlas is a decision-support system, not an autonomous actor with destructive production credentials.
