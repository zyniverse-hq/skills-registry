# Intake Form Reference

This is the **structured questionnaire** the skill walks the user through before any
recommendation. Treat it like a form: present grouped sections, accept answers in any
order, fill obvious defaults, and **echo the completed form back** before pricing.

## How to run the form

- If an interactive question UI is available (e.g. Claude Code's question tool), present
  one section at a time as multiple-choice where possible — this is the "form filling"
  experience. Otherwise, paste the whole form as a markdown checklist and let the user
  fill it in one message.
- **Never block on a field that has a sensible default.** Pick the default, mark it
  `(assumed)`, and move on. Only the few fields marked **required** truly need an answer.
- Group answers into the **Filled Form** summary table (see bottom) and repeat it back.
- One section's answers can pre-fill another (e.g. Laravel backend ⇒ MySQL default,
  Forge deploy default, PHP-FPM not containerised).

---

## Section A — Hosting Provider & Region

| Field | Options / Notes | Default |
|---|---|---|
| Provider **(required)** | DigitalOcean, AWS, GCP, Azure, Hetzner, Linode/Akamai, Vultr, or "other / client-specified" | DigitalOcean |
| Region | Closest to end users (e.g. blr1, nyc3, fra1, us-east-1) | Nearest to primary user base |
| Existing account? | Client-owned account vs. we provision | Client-owned |

> The skill supports **any hosting provider**. For DO and AWS we have pricing reference
> files. For any other provider, follow `references/providers.md` (look up live pricing,
> reuse the same table structure) and the provider-mapping in `references/terraform.md`.

---

## Section B — Backend Stack

| Field | Options / Notes | Default |
|---|---|---|
| Framework **(required)** | Laravel (PHP), Node.js, NestJS, Python (Django/FastAPI), other | — |
| Admin panel | Filament / Nova (Laravel route, no extra server), or separate admin app | None |
| Runtime concurrency | Workers/processes expected (PM2 instances, PHP-FPM children) | Auto-size from traffic |
| Background jobs | Laravel Horizon, BullMQ, Celery, none | Match framework |

Stack-driven defaults to apply automatically:
- **Laravel** ⇒ MySQL default, Redis for cache+queue, **deploy via Forge** (never
  containerise PHP-FPM), Spaces/S3 via Flysystem.
- **Node/NestJS** ⇒ PostgreSQL default, Redis + BullMQ, PM2 or Docker, deploy via
  Terraform + Ansible.
- **Python** ⇒ PostgreSQL, Gunicorn + Nginx, Celery + Redis.

---

## Section C — Frontend Stack

| Field | Options / Notes | Default |
|---|---|---|
| Frontend | Next.js, React/Vite SPA, Vue/Nuxt, server-rendered (Blade/Inertia), API-only (no frontend) | Next.js if separate frontend |
| **SSR vs static** (Next.js) **(required if Next.js)** | SSR (needs a Node runtime) vs static export (CDN only) — strongly affects sizing | SSR |
| Hosting choice | Co-located on app server, separate PaaS (App Platform/Vercel), or CDN/static bucket | Co-located for small, PaaS for medium+ |

---

## Section D — Database

| Field | Options / Notes | Default |
|---|---|---|
| Engine | MySQL, PostgreSQL, MongoDB, other | MySQL (Laravel) / PostgreSQL (Node/Python) |
| Managed vs self-hosted | Managed strongly preferred | Managed |
| Size & growth | Current GB + monthly growth | Small (<10GB), modest growth (assumed) |
| High availability | Standby/failover node needed? | No for Low tier, Yes for HA tier |
| Read replicas | Needed now? | No |

---

## Section E — Caching, Queues & Search

| Field | Options / Notes | Default |
|---|---|---|
| Redis | Cache + queue (shared is fine for small/medium) | Yes, managed Redis |
| Queue driver | Horizon (Laravel), BullMQ (Node), Celery (Python) | Match framework |
| Search | None, Meilisearch, Elasticsearch/OpenSearch | None |

---

## Section F — Storage & File Uploads

| Field | Options / Notes | Default |
|---|---|---|
| User file uploads? **(required)** | Yes/No — determines object storage need | — |
| Object storage | Spaces (DO) / S3 (AWS) / equivalent | Yes if uploads, else No |
| CDN | For static assets / uploads | Bundled with object storage where available |
| Estimated storage | GB now + growth | 250GB tier (assumed) |

---

## Section G — Domains & Sub-domains

This section drives the **DNS records Terraform will create** and the SSL setup.

| Field | Options / Notes | Default |
|---|---|---|
| Root domain **(required)** | e.g. `example.com` | — |
| DNS managed where? | At the provider (so Terraform manages records), registrar, or Cloudflare | Provider DNS if available |
| Sub-domains | List each one and what it points to. Common pattern below. | Derive from environments + services |
| SSL | Let's Encrypt (auto), provider-managed cert, or client cert | Let's Encrypt |
| www handling | Redirect `www` → apex (or vice versa) | Redirect to apex |

**Common sub-domain pattern** (offer this, let the user edit):

| Sub-domain | Points to |
|---|---|
| `app.example.com` / apex | Production frontend / app |
| `api.example.com` | Backend API |
| `admin.example.com` | Admin panel (if separate) |
| `staging.example.com` / `uat.example.com` | UAT environment |
| `dev.example.com` | Dev/QA environment |
| `cdn.example.com` / `assets.example.com` | Object storage / CDN |

---

## Section H — Configuration & Scale (sizing inputs)

| Field | Options / Notes | Default |
|---|---|---|
| Concurrent users / RPM **(required)** | Rough peak concurrency or requests/min | 100 concurrent (assumed Small) |
| Traffic pattern | Steady, spiky, scheduled bursts | Steady |
| Growth horizon | Expected scale in 6–12 months | 2–3× (assumed) |
| Compliance | None, SOC2, HIPAA, PCI, data residency | None |
| Uptime target | Best-effort vs. HA / multi-AZ | Best-effort (Low/Recommended), HA tier optional |

Sizing heuristic (starting point — always sanity-check against the provider reference):
- **≤100 concurrent** → 2 vCPU / 4GB app, 1–2GB DB, 1GB Redis (Small)
- **~100–500** → dedicated-CPU app 2 vCPU / 8GB, 2–4GB DB, 2GB Redis, load balancer
- **500–2000** → multiple app nodes + LB, 4 vCPU DB, read replica candidate
- **2000+** → horizontal scale / Kubernetes, dedicated DB cluster (see scaling roadmap)

---

## Section I — Environments

| Field | Options / Notes | Default |
|---|---|---|
| Which environments? **(required)** | Production, UAT, Dev/QA, custom | Prod + Dev/QA (+ UAT on-demand) |
| UAT model | Always-on vs on-demand (hourly billed) | On-demand |
| UAT frequency | How often spun up | Occasional (cost as on-demand) |

---

## Section J — Budget & Deployment Preference

| Field | Options / Notes | Default |
|---|---|---|
| Budget range | Monthly $ target — guides tier selection | Show all three tiers |
| Number of projects | Affects shared cost amortisation (Forge, Spaces, Redis) | 1 |
| Deployment method | Laravel ⇒ Forge (high-level steps). Others ⇒ Terraform + Ansible. CI/CD via GitHub Actions | Per stack default |
| IaC scripts wanted? | Generate ready-to-use Terraform + Ansible? | Yes |

---

## Section K — Backup & Disaster Recovery

Always raise this — it is a required part of every infra plan, not an afterthought.
Capture **what** is backed up, **where** it lands (offsite object storage), **how often**,
**how long** it's kept, and **how restore is verified**.

| Field | Options / Notes | Default |
|---|---|---|
| Database backup target **(required)** | AWS S3, Cloudflare R2, Google Cloud Storage bucket, Backblaze B2, DO Spaces, Azure Blob, or "client-specified" | R2 or S3 (cheap, S3-compatible) |
| Offsite copy? | Keep backups on a **different provider/region** than the DB for true DR | Yes — different provider/region |
| Frequency | Managed DB automated backups (point-in-time) **+** nightly logical dump (`mysqldump`/`pg_dump`) to the bucket | Both: managed daily + nightly dump |
| Retention (GFS) | e.g. 7 daily, 4 weekly, 12 monthly | 7 daily / 4 weekly / 6 monthly |
| Encryption | Encrypt dumps at rest (gpg/SSE) + TLS in transit | Yes |
| Other data | Object-storage/uploads bucket, Docker volumes — backed up too? | Uploads: provider versioning/replication; volumes: tar → bucket |
| Restore drills | How often a test restore is performed | Quarterly |
| Tooling | `rclone` (multi-cloud), `aws cli`, `gcloud`, or `restic` | `rclone` (works with S3/R2/GCS/B2) |

Notes:
- **Cloudflare R2** and **Backblaze B2** are popular backup targets — S3-compatible and have
  no egress fees, which makes restores cheap.
- **Google Cloud Storage** buckets work too (via `gsutil`/`gcloud` or `rclone`).
- Reflect the choice in the **cost estimate** (storage GB + a small bucket line item) and in
  the generated IaC (a backup bucket + a nightly cron — see `terraform.md` / `ansible.md`).

---

## Filled Form — echo this back before pricing

```
PROVIDER:     <provider>, region <region>
BACKEND:      <framework> (admin: <panel>)
FRONTEND:     <frontend> (<SSR/static>)
DATABASE:     <engine>, managed, ~<size>, HA: <y/n>
CACHE/QUEUE:  Redis <size>, queue: <driver>
STORAGE:      object storage <y/n>, ~<GB>
DOMAINS:      <root>; subdomains: <list>; DNS: <where>; SSL: <type>
SCALE:        ~<concurrent> users, growth <x>, uptime <target>
ENVIRONMENTS: <list> (UAT: <model>)
BACKUP:       DB -> <target> (<offsite y/n>), <freq>, retention <GFS>, encrypt <y/n>, restore drills <cadence>
BUDGET:       <range>, projects: <n>
DEPLOY:       <Forge | Terraform+Ansible>, IaC: <y/n>
ASSUMPTIONS:  <every field marked (assumed)>
```

After the user confirms (or corrects) this summary → proceed to **cost estimate**, then
present the **proposed architecture in chat and get explicit approval (the review gate)**.
Only after that go-ahead generate the **diagram, IaC, and client report files** — never write
any `.drawio` / `.docx` / `.pdf` / Terraform / Ansible before the architecture is approved.
