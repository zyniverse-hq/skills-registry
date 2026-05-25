# AWS Reference

**Pricing Calculator**: https://calculator.aws/pricing/2/homescreen
**Full Pricing Page**: https://aws.amazon.com/pricing/

> ⚠️ Prices below are approximate as of mid-2025 (us-east-1 region). AWS pricing varies by region. Always verify on the calculator above before quoting.

---

## EC2 (App Servers)

Recommended instance families for web apps:

### t3 / t4g — Burstable (good for staging, low-traffic)
| Instance   | vCPU | RAM  | $/mo (On-Demand) |
|------------|------|------|-----------------|
| t3.small   | 2    | 2GB  | ~$15            |
| t3.medium  | 2    | 4GB  | ~$30            |
| t3.large   | 2    | 8GB  | ~$60            |
| t3.xlarge  | 4    | 16GB | ~$120           |

### m7i — General Purpose (recommended for production)
| Instance    | vCPU | RAM  | $/mo (On-Demand) |
|-------------|------|------|-----------------|
| m7i.large   | 2    | 8GB  | ~$82            |
| m7i.xlarge  | 4    | 16GB | ~$164           |
| m7i.2xlarge | 8    | 32GB | ~$328           |

> 💡 Reserved Instances (1-year) reduce costs by ~30–40%. Worth recommending for long-term client projects.

---

## RDS (Managed Database)

### PostgreSQL / MySQL on RDS
| Instance Class   | vCPU | RAM  | $/mo (Single-AZ) |
|------------------|------|------|-----------------|
| db.t3.micro      | 2    | 1GB  | ~$13            |
| db.t3.small      | 2    | 2GB  | ~$26            |
| db.t3.medium     | 2    | 4GB  | ~$52            |
| db.m7g.large     | 2    | 8GB  | ~$120           |
| db.m7g.xlarge    | 4    | 16GB | ~$240           |

- Multi-AZ (high availability): ~2x cost
- Storage: $0.115/GB/month (gp2 SSD), minimum 20GB
- Automated backups included

---

## ElastiCache (Managed Redis)

### Valkey/Redis on ElastiCache
| Node Type       | RAM   | $/mo  |
|-----------------|-------|-------|
| cache.t3.micro  | 0.5GB | ~$12  |
| cache.t3.small  | 1.4GB | ~$24  |
| cache.t3.medium | 3.1GB | ~$48  |
| cache.m7g.large | 13GB  | ~$120 |

---

## S3 (Object Storage)

- **Storage**: $0.023/GB/month (first 50TB)
- **Data transfer out**: $0.09/GB (first 10TB/month)
- **Requests**: ~$0.005 per 1,000 PUT; ~$0.0004 per 1,000 GET
- Typical small project: **~$5–15/mo** for storage + transfers

### CloudFront CDN (for S3 / Next.js static assets)
- $0.0085–$0.02/GB transfer (varies by region)
- $0.01 per 10,000 HTTPS requests
- Typical small project: **~$5–20/mo** depending on traffic

---

## Elastic Load Balancer (ALB)

- **ALB**: ~$16/mo base + $0.008 per LCU hour
- Handles SSL termination, path-based routing, WebSocket support
- Recommended for production multi-instance setups

---

## Elastic Beanstalk / App Runner (PaaS alternatives)

Use when the team wants managed deployments without managing EC2 directly:

- **Elastic Beanstalk**: Free (pay only for underlying EC2/RDS resources)
- **App Runner**: $0.064/vCPU-hr + $0.007/GB-hr (good for containerized Node/NestJS)

---

## Fargate / ECS (Containerized — for Docker-based deployments)

- **Fargate**: $0.04048/vCPU-hr + $0.004445/GB-hr
- Example: 1 vCPU / 2GB task running 24/7 ≈ **~$37/mo**
- Suitable when team uses Docker and wants to avoid EC2 management

---

## Typical Stack Bundles

### Small Laravel Project on AWS (up to ~500 concurrent users)
| Component        | Service                    | $/mo  |
|------------------|----------------------------|-------|
| App Server       | EC2 t3.medium (2vCPU/4GB)  | $30   |
| DB               | RDS t3.medium PG           | $52   |
| Redis            | ElastiCache t3.small       | $24   |
| Storage          | S3 (50GB) + CloudFront     | $15   |
| Load Balancer    | ALB                        | $16   |
| **Total**        |                            | **~$137/mo** |

### Medium NestJS + Next.js Project on AWS
| Component        | Service                     | $/mo  |
|------------------|-----------------------------|-------|
| API Server       | EC2 m7i.large (2vCPU/8GB)   | $82   |
| Next.js          | EC2 t3.medium or App Runner | $30   |
| DB               | RDS m7g.large PG            | $120  |
| Redis            | ElastiCache t3.medium       | $48   |
| Storage          | S3 + CloudFront             | $20   |
| Load Balancer    | ALB                         | $16   |
| **Total**        |                             | **~$316/mo** |

### Staging
Use t3.micro or t3.small instances, single-AZ RDS, skip load balancer.
Budget roughly 30–40% of prod cost.

---

## AWS vs DigitalOcean — Quick Guide

| Factor                  | DigitalOcean         | AWS                          |
|-------------------------|----------------------|------------------------------|
| Pricing simplicity      | ✅ Flat monthly       | ⚠️ Complex, per-usage        |
| Managed services        | Good for most needs  | Wider range                  |
| Compliance (SOC2, HIPAA)| Basic                | ✅ Strong                    |
| Client familiarity      | Less common          | Very common                  |
| Setup complexity        | Low                  | Medium–High                  |
| Best for                | Most client projects | Enterprise / compliance-heavy|