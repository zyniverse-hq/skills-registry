# Terraform Generation Reference

Generate **ready-to-apply** Terraform that provisions the planned infrastructure on the
chosen provider. The form (`references/intake-form.md`) supplies every value; emit a
complete folder the user can `terraform init && terraform apply` after filling secrets.

> **Golden rules**
> - Terraform provisions **infrastructure only** (compute, DB, cache, storage, network,
>   DNS, firewall). App-level config belongs to Ansible (`references/ansible.md`) — or to
>   **Laravel Forge** when the stack is Laravel (see "Laravel + Forge" below).
> - Never hardcode secrets. Use variables + `terraform.tfvars` (git-ignored) + an example.
> - Tag/label every resource with `project` and `environment`.
> - One config, multiple environments via **tfvars per environment** (simplest) or
>   workspaces. Default to per-env tfvars.

---

## Folder layout to emit

```
terraform/
├── main.tf                  # provider block + resources (or module calls)
├── variables.tf             # all inputs, typed, with descriptions + defaults
├── outputs.tf               # IPs, DB host, nameservers, etc. (sensitive where needed)
├── versions.tf              # required_providers + terraform version pin
├── dns.tf                   # domain + sub-domain records (Section G of the form)
├── firewall.tf              # inbound rules (22 restricted, 80/443 open)
├── terraform.tfvars.example # every var with a sample value + comments
├── .gitignore               # *.tfstate*, *.tfvars (keep .example), .terraform/
└── README.md                # apply steps, prerequisites, what to fill in
```

For multi-environment, add `environments/prod.tfvars`, `environments/dev.tfvars`,
`environments/uat.tfvars` and document `terraform apply -var-file=environments/prod.tfvars`.

Use a **remote backend** when the client has one (S3+DynamoDB, DO Spaces, Terraform
Cloud). Otherwise note local state and recommend a remote backend before team use.

---

## Provider mapping (this is how we support "any hosting")

Pick the row matching the form's provider; the **abstract component** column is what the
architecture needs, the provider columns are the Terraform resources to emit.

| Abstract component | DigitalOcean | AWS | GCP | Hetzner | Linode | Vultr |
|---|---|---|---|---|---|---|
| App/compute | `digitalocean_droplet` | `aws_instance` | `google_compute_instance` | `hcloud_server` | `linode_instance` | `vultr_instance` |
| Managed DB | `digitalocean_database_cluster` | `aws_db_instance` | `google_sql_database_instance` | (use managed add-on / self-host) | `linode_database_mysql/postgresql` | `vultr_database` |
| Managed Redis | `digitalocean_database_cluster` (redis) | `aws_elasticache_cluster` | `google_redis_instance` | self-host | `linode_database` (n/a → self-host) | `vultr_database` (redis) |
| Object storage | `digitalocean_spaces_bucket` | `aws_s3_bucket` | `google_storage_bucket` | `hcloud` (n/a → S3-compat) | `linode_object_storage_bucket` | `vultr_object_storage` |
| Load balancer | `digitalocean_loadbalancer` | `aws_lb` (ALB) | `google_compute_forwarding_rule` | `hcloud_load_balancer` | `linode_nodebalancer` | `vultr_load_balancer` |
| Firewall | `digitalocean_firewall` | `aws_security_group` | `google_compute_firewall` | `hcloud_firewall` | `linode_firewall` | (instance fw) |
| DNS zone/record | `digitalocean_record` | `aws_route53_record` | `google_dns_record_set` | `hcloud` (n/a) | `linode_domain_record` | `vultr_dns_record` |
| Reserved/Float IP | `digitalocean_reserved_ip` | `aws_eip` | `google_compute_address` | `hcloud_floating_ip` | (instance IP) | `vultr_reserved_ip` |
| Provider auth var | `do_token` | AWS creds/profile | `credentials` JSON + project | `hcloud_token` | `linode_token` | `vultr_api_key` |

For a provider not listed: find its official Terraform provider on the Terraform Registry,
map each abstract component to its nearest resource, and keep the same file layout. If a
managed equivalent doesn't exist (e.g. Hetzner managed Redis), provision a small server
and let **Ansible** install it — note this trade-off to the user.

---

## Templates

### `versions.tf`

```hcl
terraform {
  required_version = ">= 1.5"
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}
```

### `variables.tf` (core set — extend per provider)

```hcl
variable "do_token" {
  type        = string
  description = "DigitalOcean API token"
  sensitive   = true
}

variable "project" {
  type        = string
  description = "Project name, used for naming and tags"
}

variable "environment" {
  type        = string
  description = "prod | uat | dev"
}

variable "region" {
  type    = string
  default = "blr1"
}

variable "app_size" {
  type        = string
  description = "Droplet/instance size slug"
  default     = "s-2vcpu-4gb"
}

variable "db_size" {
  type    = string
  default = "db-s-1vcpu-2gb"
}

variable "root_domain" {
  type        = string
  description = "Root domain, e.g. example.com"
}

variable "subdomains" {
  type        = list(string)
  description = "Sub-domains to create A records for"
  default     = ["app", "api"]
}

variable "ssh_keys" {
  type        = list(string)
  description = "Fingerprints/IDs of SSH keys to inject"
}

variable "admin_ip" {
  type        = string
  description = "CIDR allowed to SSH (e.g. 1.2.3.4/32)"
}
```

### `main.tf` (DigitalOcean example — adapt via the mapping table)

```hcl
provider "digitalocean" {
  token = var.do_token
}

resource "digitalocean_droplet" "app" {
  name     = "${var.project}-${var.environment}-app"
  region   = var.region
  size     = var.app_size
  image    = "ubuntu-24-04-x64"
  ssh_keys = var.ssh_keys
  tags     = ["${var.project}", "${var.environment}"]
}

resource "digitalocean_database_cluster" "db" {
  name       = "${var.project}-${var.environment}-db"
  engine     = "mysql"          # or "pg"
  version    = "8"
  size       = var.db_size
  region     = var.region
  node_count = 1                 # 2 for HA tier
  tags       = ["${var.project}", "${var.environment}"]
}

resource "digitalocean_database_cluster" "redis" {
  name       = "${var.project}-${var.environment}-redis"
  engine     = "redis"
  version    = "7"
  size       = "db-s-1vcpu-1gb"
  region     = var.region
  node_count = 1
}

resource "digitalocean_spaces_bucket" "storage" {
  count  = var.enable_storage ? 1 : 0
  name   = "${var.project}-${var.environment}-storage"
  region = var.region
  acl    = "private"
}
```

Add `digitalocean_loadbalancer` only for multi-node / HA tiers.

### `dns.tf` (sub-domains from form Section G)

```hcl
resource "digitalocean_domain" "root" {
  name = var.root_domain
}

resource "digitalocean_record" "subs" {
  for_each = toset(var.subdomains)
  domain   = digitalocean_domain.root.name
  type     = "A"
  name     = each.value          # "app" -> app.example.com
  value    = digitalocean_droplet.app.ipv4_address
  ttl      = 300
}

resource "digitalocean_record" "apex" {
  domain = digitalocean_domain.root.name
  type   = "A"
  name   = "@"
  value  = digitalocean_droplet.app.ipv4_address
  ttl    = 300
}
```

When DNS is managed at Cloudflare/registrar instead of the provider, **omit these
resources** and instead `output` the IPs/nameservers with instructions to add records
manually.

### `firewall.tf`

```hcl
resource "digitalocean_firewall" "app" {
  name        = "${var.project}-${var.environment}-fw"
  droplet_ids = [digitalocean_droplet.app.id]

  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = [var.admin_ip]   # SSH restricted
  }
  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }
  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }
  outbound_rule {
    protocol              = "tcp"
    port_range            = "all"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}
```

### `outputs.tf`

```hcl
output "app_ip" {
  value = digitalocean_droplet.app.ipv4_address
}

output "db_host" {
  value     = digitalocean_database_cluster.db.host
  sensitive = true
}

output "db_connection" {
  value     = digitalocean_database_cluster.db.uri
  sensitive = true
}

output "nameservers" {
  value = ["ns1.digitalocean.com", "ns2.digitalocean.com", "ns3.digitalocean.com"]
}
```

These outputs feed the **Ansible inventory** (`references/ansible.md`).

---

## Backup target bucket (Database DR)

The form's Section K picks where DB backups land. **Provision the backup bucket in
Terraform** — ideally on a different provider/region than the DB for true DR.

- **S3 / S3-compatible (R2, B2, Spaces):** create a bucket + a lifecycle rule for GFS expiry.
  Cloudflare R2 uses the `cloudflare` provider (`cloudflare_r2_bucket`); Backblaze uses the
  `b2` provider (`b2_bucket`); AWS uses `aws_s3_bucket` + `aws_s3_bucket_lifecycle_configuration`.
- **Google Cloud Storage:** `google_storage_bucket` with a `lifecycle_rule` (age-based delete).
- Output the bucket name/endpoint + create a scoped access key for the backup job; pass these
  to Ansible (`vault.yml`) or the Forge `.env`.

```hcl
resource "aws_s3_bucket" "db_backups" {
  bucket = "${var.project}-db-backups"
}

resource "aws_s3_bucket_lifecycle_configuration" "db_backups" {
  bucket = aws_s3_bucket.db_backups.id
  rule {
    id     = "gfs-expiry"
    status = "Enabled"
    expiration { days = 200 }   # tune to retention policy
  }
}
```

> When backups go to a *different* provider than the DB (e.g. DB on DO, backups on R2),
> add that provider block too. Restores from R2/B2 are egress-free — call this out as a plus.

---

## Laravel + Forge — provision only, then high-level steps

When the stack is **Laravel deployed via Forge**, do **not** generate Ansible app config
and do **not** model PHP/Nginx in Terraform. Generate Terraform that provisions just the
infra, then emit these high-level Forge steps in the README:

1. `terraform apply` to create the droplet, managed DB, Redis, Spaces, firewall, DNS.
2. In **Forge**: connect the DO account → **add the provisioned droplet as a custom/Forge
   server** (or let Forge create the server and import its IP into Terraform DNS instead).
3. Create the site for each sub-domain in Forge; set the web root and PHP version.
4. Add DB + Redis credentials (from Terraform outputs) to the site's `.env`.
5. Enable Let's Encrypt SSL in Forge for each domain.
6. Configure the Forge deploy script, queue worker (Horizon), and scheduler cron.
7. Point the repo + enable auto-deploy (or GitHub Actions → Forge deploy webhook).
8. Enable managed DB automated backups and add a Forge scheduled job for the offsite dump
   to the backup bucket Terraform created (S3/R2/GCS); set GFS lifecycle on the bucket.

> Decide ownership of the server up front: either Terraform creates the droplet and you
> attach it to Forge as a custom server, **or** Forge creates the server and Terraform
> only manages DB/Redis/Spaces/DNS. Don't let both try to own the droplet. Recommend the
> latter when the team lives in Forge day-to-day.

---

## README.md to emit (checklist)

- Prerequisites: terraform ≥ 1.5, a provider API token, an SSH key uploaded to the provider.
- `cp terraform.tfvars.example terraform.tfvars` and fill values.
- `terraform init`, `terraform plan -var-file=environments/<env>.tfvars`, then `apply`.
- Where outputs go (feed Ansible inventory / Forge `.env`).
- How to destroy (`terraform destroy`) and the cost reminder + provider calculator link.
- State a clear **provider calculator link** and the standard pricing disclaimer.

## Validation before presenting

- Every `variable` is either defaulted or present in `terraform.tfvars.example`.
- No secret values committed; `.gitignore` excludes `*.tfvars` and state.
- Resource names interpolate `project`/`environment` (no collisions across envs).
- DNS records exist for every sub-domain the form listed.
- SSH restricted to `admin_ip`; only 80/443 open to the world.
