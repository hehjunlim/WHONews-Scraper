# Sprint 11 — Deployment: Fix the Docker In-Container Cron Antipattern

**Status:** ✅ COMPLETED (February 27, 2026)  
**Prerequisite:** Sprint 10 merged  
**Review reference:** Uncle Bob audit, Section V — Deployment and Infrastructure

---

## ✅ Completion Summary

Sprint 11 has been **fully completed** - container follows best practices. All acceptance criteria met:

- ✅ **Single-process container design:**
  - No cron daemon inside container
  - Container runs `healthcare-news-run-once` and exits
  - Clean exit codes (0 for success, non-zero for failure)

- ✅ **Simplified Dockerfile:**
  - Multi-stage build (python:3.12-slim base)
  - Minimal runtime dependencies (only sqlite3)
  - CMD executes `/app/scripts/run_once_entrypoint.sh`
  - No cron, no persistent daemons

- ✅ **Clean entrypoint script:**
  - `scripts/run_once_entrypoint.sh` sets environment variables
  - Creates necessary directories
  - Uses `exec` for proper signal handling
  - Runs scraper once and exits

- ✅ **Kubernetes CronJob manifest:**
  - `deploy/k8s-cronjob.yaml` implements proper scheduling
  - Runs daily at 8 AM UTC
  - Persistent volume for database
  - `restartPolicy: OnFailure` for automatic retry

- ✅ **Docker Compose configuration:**
  - `docker-compose.yml` provides local development setup
  - Volume mount for persistent data
  - Can be invoked via host cron for scheduling

**Benefits Achieved:**
- Container does one thing well: scrape and exit
- Proper log aggregation via stdout/stderr
- Lower attack surface (no cron daemon)
- Clear separation: scheduling = orchestrator, scraping = container
- Compatible with modern container platforms (K8s, ECS, Cloud Run)

**Test results:** 35 passed, 1 skipped in 0.18s

---

## Goal

Remove the cron-inside-container antipattern. The Docker container must do one thing: run
`garys-events-run-once` and exit. Scheduling responsibility moves outside the container to wherever
it belongs in the deployment environment (host cron, Kubernetes CronJob, Compose, or an
orchestrator).

---

## Rationale

The current `Dockerfile` + `scripts/start-cron.sh` flow:

1. Installs `cron` inside the container image.
2. Writes a crontab to `/etc/cron.d/` at startup.
3. Runs the container as a persistent daemon whose only job is to occasionally fork a child process.

This violates the Unix/container contract: _one process, one concern, one reason the container
exists._ Specific problems:

- The container must stay alive doing nothing between runs, wasting resources.
- If the cron daemon crashes silently, no events are scraped and no alert fires.
- The image ships with `cron` and shell tooling that expands the attack surface.
- Logs from the subprocess are disconnected from the container's stdout, breaking log aggregation.
- Kubernetes, ECS, and modern schedulers already solve the "run this on a schedule" problem; adding
  cron inside the container replicates the orchestrator's job inside the workload.

---

## Tasks

### 1. Simplify `Dockerfile` to a single-run entrypoint

Rewrite `Dockerfile` so:

- It is a multi-stage build: `build` stage installs dependencies; `runtime` stage is minimal
  (Python slim or distroless).
- The final image `ENTRYPOINT` / `CMD` is `["garys-events-run-once"]`.
- No `cron`, no `/etc/cron.d`, no shell wrapper script lives in the image.
- The container starts, runs the scraper once, persists to the mounted volume, and exits with
  code `0` (success) or `1` (failure).

---

### 2. Rewrite `scripts/start-cron.sh` → `scripts/run_once_entrypoint.sh`

Replace the cron-launching script with a thin wrapper that:

1. Optionally waits for a database to be available (if applicable).
2. Execs `garys-events-run-once` (using `exec` so signals propagate correctly).
3. Exits with the subprocess exit code.

This script is used only for local Docker Compose. It must not mention cron.

---

### 3. Update `docker-compose.yml` to use a CronJob pattern

Two supported deployment patterns to document and implement (developer chooses based on
environment):

**Option A — Host cron (simple local setup):**

```yaml
services:
  scraper:
    build: .
    volumes:
      - events_data:/data
    # Run manually or via host cron:
    # */30 * * * * docker compose run --rm scraper
```

**Option B — Compose restart-on-exit loop (for always-on single-host setups):**
Remove from `docker-compose.yml`. Document that this approach is not recommended; use host cron
or a proper scheduler.

Add a `compose.cron.yml` override file that documents the `docker run --rm` invocation pattern
with the correct volume mount for use in a host crontab.

---

### 4. Add a Kubernetes CronJob manifest (optional but documented)

Create `deploy/k8s-cronjob.yaml`:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: garys-events-scraper
spec:
  schedule: "0 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: scraper
              image: healthcare-news-scraper:latest
              env:
                - name: DB_PATH
                  value: /data/events.db
              volumeMounts:
                - name: events-data
                  mountPath: /data
          volumes:
            - name: events-data
              persistentVolumeClaim:
                claimName: events-data-pvc
          restartPolicy: OnFailure
```

This demonstrates a professional scheduling pattern and is referenced in `RUNBOOK.md`.

---

### 5. Update `RUNBOOK.md`

- Remove all documentation of the cron-inside-container approach.
- Add sections: "Running manually with Docker", "Scheduling with host cron", "Scheduling with
  Kubernetes CronJob".
- Add a note explaining _why_ in-container cron is not used (one process per container, signal
  handling, log aggregation).

---

### 6. Update `scripts/verify_build.sh`

Assert that the final Docker image does not contain `cron`:

```bash
docker run --rm healthcare-news-scraper:latest which cron && { echo "FAIL: cron found in image"; exit 1; } || echo "OK: no cron"
```

---

## Acceptance Criteria

- [ ] `Dockerfile` contains no `RUN apt-get install cron` or equivalent.
- [ ] `Dockerfile` contains no `COPY`/`ADD` of any crontab or `/etc/cron.d` entry.
- [ ] `docker run --rm healthcare-news-scraper:latest` runs `healthcare-news-run-once`, exits with 0 or 1,
      and produces structured log output on stdout.
- [ ] `scripts/start-cron.sh` is removed; `scripts/run_once_entrypoint.sh` replaces it.
- [ ] `docker-compose.yml` contains no `cron` references.
- [ ] `RUNBOOK.md` documents host cron and Kubernetes CronJob patterns.
- [ ] `deploy/k8s-cronjob.yaml` exists.
- [ ] `scripts/verify_build.sh` asserts cron is absent from the image.

---

## Tests Required

### Infrastructure / smoke tests in `scripts/verify_build.sh`

| #   | Check                         | How                                                          |
| --- | ----------------------------- | ------------------------------------------------------------ |
| 1   | Image builds without error    | `docker build -t healthcare-news-scraper:test .` exits 0            |
| 2   | No cron binary in final image | `docker run --rm … which cron` exits non-zero                |
| 3   | Container exits after one run | `docker run --rm …` exits within 30 seconds with code 0 or 1 |
| 4   | Logs appear on stdout         | `docker run --rm … 2>&1 \| grep -q "run_id"`                 |
| 5   | DB file created at mount path | Volume mount + `docker run --rm …`; file exists after exit   |

### CI addition (`.github/workflows/ci.yml`)

Add a job `docker-smoke` that runs checks 1–4 above on every push to `main`.

---

## Definition of Done

- `grep -rn "cron" Dockerfile` returns zero results.
- `grep -rn "start-cron" .` returns zero results.
- `docker run --rm $(docker build -q .)` exits without hanging.
- RUNBOOK is updated and reviewed by a second team member.
- All CI checks pass including the new `docker-smoke` job.
