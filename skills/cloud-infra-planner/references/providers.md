# Provider Coverage Reference ("any hosting")

The skill defaults to **DigitalOcean** and has detailed pricing for DO and AWS
(`references/digitalocean.md`, `references/aws.md`). But it must support **any hosting
provider** the user picks. This file is the playbook for everything else.

---

## When the provider is DO or AWS

Use the dedicated reference file. Done.

## When the provider is anything else

Follow this process — never invent prices:

1. **Look up live pricing.** Use the provider's official pricing page / calculator. If web
   access is available, fetch current numbers; otherwise ask the user to confirm the
   plan prices, and label everything "approximate — verify on calculator".
2. **Map the same component model.** Every plan reuses the same rows: App/compute, Managed
   DB, Managed Redis, Object storage, Load balancer, Bandwidth/CDN. If the provider lacks
   a managed equivalent (e.g. no managed Redis), provision a small server and let Ansible
   install it — and note the added ops burden.
3. **Reuse the table format** from the DO/AWS references: per-service breakdown, three
   tiers (Low / Recommended / HA), combined total, disclaimer + calculator link.
4. **Generate IaC** via the provider mapping in `references/terraform.md`. If the provider
   isn't in that table, find its Terraform provider on the Terraform Registry and map each
   abstract component to the nearest resource.

---

## Quick orientation for common providers

| Provider | Calculator / pricing | Notes |
|---|---|---|
| DigitalOcean | digitalocean.com/pricing/calculator | Default. Flat monthly, simple. Forge-friendly. |
| AWS | calculator.aws | Widest managed range; complex per-usage; best for compliance. |
| GCP | cloud.google.com/products/calculator | Strong managed DB (Cloud SQL) + k8s (GKE). Sustained-use discounts. |
| Azure | azure.com/pricing/calculator | Common in enterprise/Microsoft shops. |
| Hetzner | hetzner.com/cloud | Cheapest compute in EU; **no managed DB/Redis** → self-host via Ansible. |
| Linode / Akamai | linode.com/pricing | Flat pricing like DO; managed DB available. |
| Vultr | vultr.com/pricing | Flat pricing; managed DB + object storage available. |

---

## Forge availability note

Laravel Forge can manage servers on most major providers (DO, AWS, Linode, Hetzner,
Vultr, or any custom server via SSH). So the **Laravel + Forge "high-level steps" path
applies regardless of provider** — Terraform provisions the box and managed services,
Forge handles PHP/Nginx/queues/deploys. See the Forge sections in
`references/terraform.md` and `references/ansible.md`.

---

## Always

- State the provider + region chosen in the Filled Form.
- Keep the **pricing disclaimer + calculator link** on every cost section.
- Prefer managed services; flag where the chosen provider forces self-hosting.
