# Architecture Patterns Reference

## Stack Configurations

### Laravel PHP (via Laravel Forge)
- Forge manages PHP-FPM + Nginx, SSL, cron, queue daemons, and Git deployments on bare metal
- DB: Managed MySQL (default) or PostgreSQL
- Queue: Managed Redis + Laravel Horizon, supervised by Forge daemon manager
- Storage: Spaces (DO) or S3 (AWS) — use Laravel Flysystem S3 driver
- Cache: Redis shared with queue (fine for small/medium projects)
- Admin panel: Filament or Nova runs as a route within the same Laravel app — no separate server
- Zero-downtime: Forge atomic deployments (symlink swap) or Laravel Envoyer for blue/green

### Next.js
- Co-located on Forge server via PM2, proxied by Forge-managed Nginx — OR — DO App Platform (~$25/mo, simpler deploys)
- Always clarify SSR vs static export — significantly affects server sizing
- Static assets served via Spaces CDN

### Node.js / NestJS
- Droplet with PM2 or Docker; Managed PostgreSQL (preferred); Redis + BullMQ for queues

### Python (rare)
- Gunicorn + Nginx on Droplet; Managed PostgreSQL; Celery + Redis

---

## Docker Coexistence with Laravel Forge

**Core rule: Never containerise PHP-FPM or Laravel itself. Forge owns that layer.**

| Concern | Guidance |
|---|---|
| File location | `docker-compose.yml` at `/srv/docker/<project>/` |
| Volumes | Named Docker volumes only — no bind mounts into `/home/forge` |
| Networking | Custom bridge network; expose ports to localhost only; proxy via Nginx |
| Resource limits | Apply `mem_limit` + `cpus` in Compose to protect PHP-FPM |
| Deploy sync | Add `docker compose up -d` to Forge post-deployment hook |
| Volume backups | Daily cron: tar named volumes → upload to Spaces |

---

## Environment Model

| Environment | Always on? | Spec | Notes |
|---|---|---|---|
| Production | Yes | Full spec, HA DB | Load balancer, automated backups |
| UAT | On-demand | ~50% of prod | Hourly billed; spin up/down via DO API or script |
| Dev/QA | Yes | Minimal | Shared by all devs and QA testers |

**UAT on-demand pattern:**
- Provision via DO API or `doctl`; add to Forge; deploy via webhook
- Use a DB snapshot/fork — never point UAT at production DB
- Basic Droplet (2vCPU/4GB) billed hourly ~$0.03/hr — 3-day session ≈ $2.16
- Automate spin-up/down with GitHub Actions or a shell script

---

## Shared Workload Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Resource contention | Medium | Apply docker-compose resource limits |
| Volume data loss | High | Named volumes + daily backup to Spaces |
| Forge agent conflict | Low | Never Dockerise PHP-FPM |
| Port conflicts | Medium | Bridge network + Nginx proxy only |
| Deployment coupling | Low-Medium | Add `docker compose up -d` to Forge deploy hook |
| Log pollution | Low | Separate Docker log driver; forward to Logtail |

---

## Scaling Strategy

**Vertical (scale up):** Increase Droplet or DB tier. Trigger: CPU >70%, RAM >80%, p95 response >500ms.

**Horizontal (scale out):** Add App Droplets behind Load Balancer. Requires Redis-backed sessions and Spaces for file storage (both already recommended).

**Service separation triggers:**
- Container RAM consistently >30% of Droplet RAM → dedicated Droplet or DOKS node
- Docker services deploy independently >3×/week → consider DOKS
- Security audit requires full workload isolation → separate Droplets per project

**Phased roadmap:**
- Phase 1: Single Droplet, Docker co-located (~$90–320/mo)
- Phase 2 (~500+ concurrent): Split Next.js to App Platform; dedicated Horizon worker Droplet
- Phase 3 (~2000+ concurrent): Multiple App Droplets; DOKS for Docker; Read Replica DB
- Phase 4 (enterprise): Full Kubernetes, CDN for all traffic, dedicated DB cluster

---

## Database Backup & Disaster Recovery Strategy

Every plan must include a backup strategy. Default to a **two-layer** approach:

**Layer 1 — Managed automated backups (provider-native).**
- Use the managed DB's built-in daily backups + point-in-time recovery (DO Managed DB: 7-day;
  RDS: configurable). Covers fast restore of recent state, same provider.

**Layer 2 — Offsite logical dumps to object storage (the part clients ask for).**
- Nightly `mysqldump` / `pg_dump`, compressed and encrypted, uploaded to a bucket on a
  **different provider or region** than the database (true DR — survives a provider outage).
- Targets (client choice): **AWS S3, Cloudflare R2, Google Cloud Storage, Backblaze B2,
  DO Spaces, Azure Blob**, or client-specified. Prefer **R2 / B2** for backups — S3-compatible
  with no egress fees, so restores are cheap.
- Tooling: **`rclone`** (one tool, works with S3/R2/GCS/B2/Azure), or native `aws cli` /
  `gsutil`, or `restic` for deduplicated encrypted backups.

**Retention — Grandfather-Father-Son (GFS):** e.g. 7 daily, 4 weekly, 6–12 monthly. Apply
lifecycle/expiry rules on the bucket so old objects auto-delete.

**Also back up:** object-storage/uploads (bucket versioning or cross-region replication) and
Docker named volumes (daily tar → bucket — see Shared Workload Risks).

**Verify, don't assume:** schedule **restore drills** (quarterly default). A backup that has
never been restored is not a backup. Document the restore runbook in the report.

**Encryption:** dumps encrypted at rest (gpg or bucket SSE) and transferred over TLS.

How this shows up: a small **bucket line item** in the cost estimate, a **backup bucket +
nightly cron** in the generated IaC (`terraform.md` / `ansible.md`), and the ops checklist below.

---

## Client Report Structure (11 Sections)

1. Requirements Summary — repeat back what was understood
2. Assumptions — all assumptions for client confirmation
3. Architecture Design — topology, Docker strategy, environment model, UAT approach
4. Infrastructure Components — what each service is and why
5. Cost Estimates — all three tiers, all environments, combined total, disclaimer
6. Deployment & Operations — Forge, Docker, CI/CD, queues, cron, backups, monitoring; reference the generated Terraform + Ansible (or Forge high-level steps) deliverable
7. Infrastructure Tiers — Low / Recommended / HA with trade-offs
8. Scaling Strategy — vertical, horizontal, separation triggers, phased roadmap
9. Risks — shared workload risks table with mitigations
10. Effort Estimation — initial setup hours + ongoing ops hours/month
11. Management Summary — non-technical summary with cost table and next steps

## Operations Checklist (include in reports)
- Forge deploy script: `composer install --no-dev`, `artisan migrate --force`, `config:cache`, `queue:restart`
- Horizon: Forge daemon supervisor, dashboard restricted to admin IP
- Scheduler: Single Forge-managed cron entry `* * * * * php artisan schedule:run`
- CI/CD: GitHub Actions → test → build → Forge webhook → `docker compose up -d`
- Monitoring: DO built-in alerts + Sentry (errors) + Logtail (logs) + UptimeRobot (uptime)
- Backups: Managed DB (automated, 7-day) **+ nightly encrypted `mysqldump`/`pg_dump` offsite to S3 / R2 / GCS (different provider/region) via `rclone`, GFS retention** + Droplet snapshots + Docker volume tars to bucket
- Restore drills: scheduled test restore (quarterly) with a documented runbook — confirm backups are actually recoverable