# DigitalOcean Reference

**Pricing Calculator**: https://www.digitalocean.com/pricing/calculator
**Full Pricing Page**: https://www.digitalocean.com/pricing

> ⚠️ Prices below are approximate as of mid-2025. Always verify on the calculator above before quoting.

---

## Droplets (VPS / App Servers)

### Basic Droplets (shared CPU — good for staging, low-traffic apps)
| Spec             | $/mo  |
|------------------|-------|
| 1 vCPU / 1GB RAM | $6    |
| 1 vCPU / 2GB RAM | $12   |
| 2 vCPU / 2GB RAM | $18   |
| 2 vCPU / 4GB RAM | $24   |
| 4 vCPU / 8GB RAM | $48   |

### General Purpose Droplets (dedicated CPU — recommended for production)
| Spec              | $/mo  |
|-------------------|-------|
| 2 vCPU / 8GB RAM  | $63   |
| 4 vCPU / 16GB RAM | $126  |
| 8 vCPU / 32GB RAM | $252  |

### CPU-Optimized (for compute-heavy workloads like Python ML)
| Spec              | $/mo  |
|-------------------|-------|
| 2 vCPU / 4GB RAM  | $42   |
| 4 vCPU / 8GB RAM  | $84   |

---

## Managed Databases

### Managed PostgreSQL / MySQL
| Plan     | Spec              | $/mo  |
|----------|-------------------|-------|
| Basic    | 1 vCPU / 1GB RAM  | $15   |
| Basic    | 1 vCPU / 2GB RAM  | $30   |
| Standard | 2 vCPU / 4GB RAM  | $60   |
| Standard | 4 vCPU / 8GB RAM  | $120  |

Includes: automated backups, failover option, connection pooling (PgBouncer for PG).

### Managed Redis
| Plan  | Memory | $/mo |
|-------|--------|------|
| Basic | 1GB    | $15  |
| Basic | 2GB    | $30  |
| Basic | 4GB    | $60  |

---

## Spaces (Object Storage — S3-compatible)

- **$21/mo** flat for 250GB storage + 1TB outbound transfer
- Additional storage: $0.02/GB
- Additional transfer: $0.01/GB
- Includes CDN edge caching (Spaces CDN)
- Use for: Laravel file uploads, Next.js static assets, backups

---

## App Platform (Managed PaaS — alternative to raw Droplets)

Good for Next.js or simple Node/NestJS APIs without heavy infra needs.

| Plan        | $/mo      | Notes                        |
|-------------|-----------|------------------------------|
| Basic (512MB) | $5      | Static sites / simple apps   |
| Basic (1GB)   | $12     | Small Node/Next apps         |
| Pro (2GB)     | $25     | Production-grade             |
| Pro (4GB)     | $50     | High-traffic apps            |

Includes: auto-deploy from GitHub, managed SSL, built-in CDN for static.

---

## Load Balancers

- **$12/mo** per load balancer
- Handles SSL termination, health checks, distributes across multiple Droplets
- Recommended when running 2+ app server Droplets

---

## Kubernetes (DOKS) — for larger / containerized projects

- **$12/mo** per node (control plane is free)
- Node pools sized same as Droplets above
- Recommended when team is already using Docker and expects horizontal scaling

---

## Networking

- **Floating IP**: Free (one per Droplet)
- **Reserved IP**: Free while assigned
- **Private networking**: Free between Droplets in same region
- **Bandwidth**: 1TB outbound included per Droplet, then $0.01/GB

---

## Typical Stack Bundles

### Small Laravel Project (up to ~100 concurrent users)
| Component         | Product                   | $/mo |
|-------------------|---------------------------|------|
| App Server        | Basic Droplet 2vCPU/4GB   | $24  |
| DB                | Managed PG 1vCPU/2GB      | $30  |
| Redis             | Managed Redis 1GB         | $15  |
| Storage           | Spaces 250GB              | $21  |
| **Total**         |                           | **~$90/mo** |

### Medium NestJS + Next.js Project
| Component         | Product                    | $/mo  |
|-------------------|----------------------------|-------|
| API Server        | General Purpose 2vCPU/8GB  | $63   |
| Next.js App       | App Platform Pro 2GB       | $25   |
| DB                | Managed PG 2vCPU/4GB       | $60   |
| Redis             | Managed Redis 2GB          | $30   |
| Storage           | Spaces 250GB               | $21   |
| Load Balancer     | Load Balancer              | $12   |
| **Total**         |                            | **~$211/mo** |

### Staging (roughly 40–50% of prod cost)
Use one step down in DB and Redis tiers, Basic Droplets for app servers.