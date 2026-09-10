# Roundtrip

Roundtrip turns gallery feedback into a recoverable Lightroom revision. A local web app submits one job to GPT-6 Astra through the signed-in Codex CLI. Astra inspects the photo, operates Lightroom through the existing computer-use plugin, saves a named version, exports a JPEG, and reviews it. The server verifies the result before adding it to the gallery.

The local gallery now supports an optional hosted feedback inbox. A reviewer submits text through a secret link; the Mac polls over HTTPS, makes the edit locally, and reports its status. RAW files and exported images stay on the Mac. Cloud photo delivery and unattended batch processing are not implemented.

## Run it

Requirements:

- macOS with cloud-based Adobe Lightroom installed and signed in.
- Python 3.10 or newer and a signed-in Codex CLI supporting `gpt-6-astra`, JSON events, and structured output.
- The official native computer-use plugin enabled in Codex, with access to Lightroom.
- A prepared source RAW in Lightroom with the three versions below. Personal photos are not included in this repository.

Prepare `original.jpg`, `v1.jpg`, and `v2.jpg` as 2048-pixel-long-edge JPEGs from the same source photo. Their corresponding Lightroom version names must be:

- `Roundtrip 00 - Original`
- `Roundtrip 01 - Fuji first pass`
- `Roundtrip 02 - Subject first`

Then run from the repository root:

```sh
python3 roundtrip/server.py \
  --media-dir /path/to/your/jpeg-exports \
  --source-filename YOUR_PHOTO.ORF \
  --max-jobs 3
```

Open `http://127.0.0.1:8766` for the story, then select **Gallery** (or go directly to `/gallery`). Enter feedback and select **Revise in Lightroom**. The server operates the source photo on this Mac, using your existing Codex account. Leave Lightroom available while the job runs.

The current local demo already has its images in `.local-demo/fuji-portrait`, so `python3 roundtrip/server.py` uses that folder by default. The story and gallery share this server and navigation; no second server is needed. Optional `session-16x.mp4` and `session.mp4` recordings are served from the same media directory. Old `/?photo=…` links still open the gallery.

`--state-dir` chooses a private state folder; its default is `.local-demo/roundtrip-runtime`. Reusing that folder restores gallery history. To prepare a different photo, use a new state directory. `--max-jobs` caps newly launched jobs in a server session; `--timeout` limits each job to 900 seconds by default. These are execution limits, not a precise weekly-credit accounting mechanism.

## What the prototype actually does

1. Saves feedback with a stable photo ID, base revision, and idempotency key.
2. Allows only one active Lightroom job at a time.
3. Starts Astra with a bounded photo-editing prompt and a fresh export directory.
4. Displays progress from actual Codex messages and computer-use tool titles.
5. Requires a matching source filename and native base/version names, reported visual verification, a fresh complete JPEG with the expected dimensions, and a different SHA-256 from the base export.
6. Copies the verified image to immutable gallery history and switches the current revision atomically.

Stopping a job preserves the last verified gallery image. Lightroom may retain partial native changes, so subsequent jobs must explicitly select the requested base version. Interrupted jobs are marked failed on restart and are never silently retried. A failed job is visible; the app never substitutes a canned image or fake success animation.

## Boundaries

The server binds to loopback, checks the Host and Origin, requires a session token for mutations, and exposes only allowlisted page assets and registered JPEGs. It does not serve job prompts, raw traces, arbitrary filesystem paths, or the database. Photo feedback is rendered as text and treated as untrusted visual intent by the worker.

The worker is a general-purpose model operating a real application. Prompt boundaries and export verification do not constitute a security sandbox for malicious third-party reviewers. Use the remote inbox only with trusted reviewers and a small run allowance. Possession of its secret link allows someone to request edits and consume the configured local run allowance. It has not been tested for adversarial public access.

Structural JPEG checks and the model's visual inspection catch common wrong-file failures; they do not prove photographic authenticity or semantic correctness. Review the returned image and native version before using it for a client.

## Tests

```sh
python3 -m unittest discover -s roundtrip/tests -v
node --check roundtrip/static/app.js
```

Tests cover revision lineage, idempotency, concurrent admission, stale bases, wrong identity, invalid exports, unchanged exports, cancellation, interrupted runs, and HTTP origin/host/token/path checks. Fixtures are generated solid-color images and contain no personal photos. Unit tests do not operate Lightroom or spend model credits.

## Layout

- `server.py` — HTTP service, SQLite state, serialized Astra worker, and export validation.
- `worker_prompt.md` — bounded native-editing procedure.
- `result.schema.json` — structured worker result contract.
- `static/` — gallery, feedback, activity, and comparison UI.
- `tests/` — local tests with generated fixtures.
- `remote.py` — outbound polling, durable local admission, and remote status updates.
- `relay/` — hosted reviewer page, authenticated APIs, and D1 request storage.

Official runtime references: [Codex non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode) and [Codex MCP configuration](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).

## Remote review setup

Deploy the separate `relay/` Sites app with its generated D1 migration. Set two independently generated secrets in hosted environment variables: `REVIEW_KEY` and `WORKER_KEY` (at least 32 random characters each). The review link is `https://YOUR-INBOX/#REVIEW_KEY`; the fragment is sent in an Authorization header by the page, not in the URL path or query. The Sites audience must also allow the intended reviewer. An owner-only Sites deployment still requires the owner's sign-in.

Save a pairing file outside version control, for example `.local-demo/roundtrip-runtime/remote.json`:

```json
{
  "url": "https://YOUR-INBOX",
  "photo_id": "portrait",
  "review_key": "YOUR_RANDOM_REVIEW_KEY",
  "worker_key": "YOUR_DIFFERENT_RANDOM_WORKER_KEY"
}
```

Start the local app with `--remote-config .local-demo/roundtrip-runtime/remote.json`. Keep the server running and Lightroom available. The gallery shows connection status and a copyable review link. No inbound port or tunnel is required. The Mac checks every three seconds. A received request stays in the hosted database if the connection drops. New submissions are refused while the Mac is offline, busy, or has exhausted its run allowance. The local form is disabled while paired, so all submissions share the hosted inbox. Restarting with a new allowance enables queued requests to run.

Automated editing is scoped to one photo and one local state directory in this prototype; the hosted review gallery supports four photographs. Each request records its base revision, so feedback for an older export is refused rather than applied to the latest photo. Do not pair multiple Macs to the same inbox. Rotating `REVIEW_KEY` invalidates the old reviewer link; rotating `WORKER_KEY` requires updating the Mac's pairing file. Both environment changes require redeployment.

The hosted gallery stores JPEG previews in private R2 and keeps per-photo revisions and comments in D1. RAWs, filesystem paths, and raw tool traces stay on the Mac. Media reads require the review credential; uploads require the separate worker credential. Open `/import`, enter the photographer key, choose a photo, and upload its Lightroom JPEG export (maximum 3 MB). The three additional photographs allow comments; automated edits still target only the original study. The initial study importer recognizes `original.jpg`, `v1.jpg`, `v2.jpg`, and its existing final revision identifier. Gallery titles are a bounded prototype catalog in `relay/lib/gallery.ts`; personal filenames and media are excluded from source.

Local gallery API verification: run the relay on port 8770 with its local D1/R2 bindings and test credentials, then run `python3 roundtrip/relay/tests/check-gallery.py` from the repository root. The check uploads generated gray fixtures only.

## Supported reviewer prompts

The hosted page offers six example prompts. A deliberately narrow, shared request grammar validates every clause on both the relay and the Mac. It accepts supported light, color, grain, texture, vignette, and crop commands; unknown or mixed transformation requests are rejected before they can launch Lightroom. This may reject some otherwise reasonable paraphrases; the example buttons provide accepted wording. The runtime also checks the whole request before using tools. No image generation, identity/gender-presentation changes, body/face reshaping, clothing swaps, or object/scene synthesis is permitted.

## Local multi-photo demo

For local execution without a hosted relay, omit `--remote-config` and supply `--catalog PATH` with a private JSON array. Each entry has `id`, `title`, `source_filename`, and an absolute `jpeg` path. Optional `base_version` names an existing Lightroom version. Without it, the worker must visually match the current Lightroom edit to the imported JPEG and save a named base before editing. Camera filenames alone are insufficient identity evidence. Re-import preserves existing photo identities and revisions.

The gallery offers photo selection, one shared Lightroom queue, feedback attached to each job, progress, revision history, and JPEG downloads. `?photo=PHOTO_ID` opens a particular photograph. The request button starts a real native editing job; it is not an ordinary comment. Earlier hosted comments are not automatically replayed. The washed-out/hands-only proof-of-concept request is supported by the shared admission policy.

## Hosting portability

The complete editing process runs on the photographer’s Mac. A future Vercel deployment would host only the reviewer interface and short HTTP requests for authentication, durable job submission/status, and signed image delivery. It must use persistent database/object storage, not serverless process memory or a local SQLite file. Keep the Mac worker polling outward over authenticated HTTPS, with photo identity, base revision, idempotency key, and a single global edit lease in each job contract. Publish a completed revision only after its actual JPEG has been uploaded and verified. The current Sites relay uses D1/R2 and still requires a storage adapter and multi-photo worker protocol before being deployed on Vercel; no Vercel deployment is claimed here.
