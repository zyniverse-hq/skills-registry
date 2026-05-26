# Ansible Generation Reference

Generate **ready-to-run** Ansible that configures the servers Terraform provisioned and
deploys the app. Ansible owns the **OS + app layer**; Terraform owns the **infra layer**
(`references/terraform.md`).

> **When to generate Ansible**
> - **Node.js / NestJS / Python / generic Docker stacks** → generate full playbooks
>   (base hardening, runtime, Nginx, app deploy, SSL).
> - **Laravel via Forge** → **do NOT generate app playbooks.** Forge owns PHP-FPM, Nginx,
>   queues, cron, deploys. Emit only the high-level Forge steps (see end of this file and
>   the Forge section in `references/terraform.md`). At most, a tiny base-hardening play if
>   the client is attaching a raw server to Forge themselves.

---

## Folder layout to emit

```
ansible/
├── ansible.cfg
├── inventory/
│   └── hosts.ini            # populated from Terraform outputs (app_ip, etc.)
├── group_vars/
│   ├── all.yml              # non-secret vars (domain, node version, repo url)
│   └── vault.yml            # secrets, encrypted with ansible-vault
├── site.yml                 # top-level play importing roles
├── roles/
│   ├── common/              # users, packages, UFW, fail2ban, timezone, swap
│   ├── nginx/               # reverse proxy + vhosts per sub-domain
│   ├── nodejs/              # nvm/node + pm2  (or python/, docker/ as needed)
│   ├── app_deploy/          # clone/pull, install deps, build, env file, restart
│   └── certbot/             # Let's Encrypt issuance + auto-renew
└── README.md                # run steps, vault usage, prerequisites
```

Swap the runtime role per stack: `nodejs/` (PM2), `python/` (gunicorn + systemd),
`docker/` (compose up). Keep `common`, `nginx`, `certbot` for all.

---

{% raw %}
## Templates

### `ansible.cfg`

```ini
[defaults]
inventory = inventory/hosts.ini
host_key_checking = False
retry_files_enabled = False
roles_path = roles
[privilege_escalation]
become = True
```

### `inventory/hosts.ini` (fill `<app_ip>` from `terraform output app_ip`)

```ini
[app]
<app_ip> ansible_user=root ansible_ssh_private_key_file=~/.ssh/id_rsa

[app:vars]
ansible_python_interpreter=/usr/bin/python3
```

### `group_vars/all.yml`

```yaml
project: myproject
environment: prod
domain: app.example.com
subdomains:
  - app.example.com
  - api.example.com
node_version: "20"
repo_url: "git@github.com:org/repo.git"
repo_branch: main
app_dir: /var/www/{{ project }}
deploy_user: deploy
```

Secrets (`db_password`, `redis_url`, `app_key`, registry creds) go in
`group_vars/vault.yml`, encrypted: `ansible-vault encrypt group_vars/vault.yml`.

### `site.yml`

```yaml
- hosts: app
  become: true
  roles:
    - common
    - nginx
    - nodejs        # or python / docker
    - app_deploy
    - certbot
```

### `roles/common/tasks/main.yml` (base hardening — idempotent)

```yaml
- name: Set timezone
  ansible.builtin.timezone:
    name: UTC

- name: Install base packages
  ansible.builtin.apt:
    name: [ufw, fail2ban, git, curl, unzip, build-essential]
    update_cache: true
    state: present

- name: Create deploy user
  ansible.builtin.user:
    name: "{{ deploy_user }}"
    groups: sudo
    shell: /bin/bash

- name: UFW default deny incoming
  community.general.ufw:
    direction: incoming
    policy: deny

- name: UFW allow OpenSSH, HTTP, HTTPS
  community.general.ufw:
    rule: allow
    name: "{{ item }}"
  loop: [OpenSSH, "Nginx Full"]

- name: Enable UFW
  community.general.ufw:
    state: enabled
```

### `roles/nodejs/tasks/main.yml`

```yaml
- name: Install Node.js {{ node_version }}
  ansible.builtin.shell: |
    curl -fsSL https://deb.nodesource.com/setup_{{ node_version }}.x | bash -
    apt-get install -y nodejs
  args:
    creates: /usr/bin/node

- name: Install pm2 globally
  community.general.npm:
    name: pm2
    global: true
```

### `roles/app_deploy/tasks/main.yml`

```yaml
- name: Clone/pull repository
  ansible.builtin.git:
    repo: "{{ repo_url }}"
    dest: "{{ app_dir }}"
    version: "{{ repo_branch }}"
    accept_hostkey: true
  become_user: "{{ deploy_user }}"

- name: Render .env from template
  ansible.builtin.template:
    src: env.j2
    dest: "{{ app_dir }}/.env"
    mode: "0640"

- name: Install dependencies & build
  ansible.builtin.shell: |
    cd {{ app_dir }}
    npm ci
    npm run build
  become_user: "{{ deploy_user }}"

- name: Start/reload via pm2
  ansible.builtin.shell: |
    cd {{ app_dir }}
    pm2 startOrReload ecosystem.config.js --env {{ environment }}
    pm2 save
  become_user: "{{ deploy_user }}"
```

### `roles/nginx/templates/site.conf.j2`

```nginx
server {
    listen 80;
    server_name {{ domain }};
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### `roles/certbot/tasks/main.yml`

```yaml
- name: Install certbot
  ansible.builtin.apt:
    name: [certbot, python3-certbot-nginx]
    state: present

- name: Obtain certificates
  ansible.builtin.shell: >
    certbot --nginx -n --agree-tos -m admin@{{ domain }}
    {{ subdomains | map('regex_replace', '^', '-d ') | join(' ') }}
  args:
    creates: /etc/letsencrypt/live/{{ domain }}
```

---

## Docker variant (`roles/docker/`)

For containerised Node/Nest/Docker stacks: install Docker + Compose plugin, copy
`docker-compose.yml`, render `.env`, `docker compose pull && up -d`. Apply `mem_limit` /
`cpus` per service. (If co-locating with anything Forge-managed, follow the coexistence
rules in `references/architecture.md` — named volumes only, bridge network, Nginx proxy.)

---

## Database backup role (`roles/db_backup/`)

Implements Layer 2 of the backup strategy (`references/architecture.md`): a nightly
encrypted DB dump pushed offsite to the bucket chosen in form Section K (S3 / R2 / GCS /
B2 / …). Uses **`rclone`** so the same role works against any S3-compatible or GCS target.

`roles/db_backup/templates/db-backup.sh.j2`:

```bash
#!/usr/bin/env bash
set -euo pipefail
TS=$(date +%F-%H%M)
FILE="/tmp/{{ project }}-{{ environment }}-$TS.sql.gz"

{% if db_engine == 'mysql' %}
mysqldump --single-transaction -h {{ db_host }} -u {{ db_user }} -p"{{ db_password }}" {{ db_name }} | gzip > "$FILE"
{% else %}
PGPASSWORD="{{ db_password }}" pg_dump -h {{ db_host }} -U {{ db_user }} {{ db_name }} | gzip > "$FILE"
{% endif %}

gpg --batch --yes --passphrase "{{ backup_gpg_passphrase }}" -c "$FILE"   # encrypt at rest
rclone copy "$FILE.gpg" "{{ backup_remote }}:{{ backup_bucket }}/$(date +%Y/%m)/"
rm -f "$FILE" "$FILE.gpg"
```

`roles/db_backup/tasks/main.yml`:

```yaml
- name: Install rclone & gnupg
  ansible.builtin.apt:
    name: [rclone, gnupg]
    state: present

- name: Configure rclone remote (S3/R2/GCS/B2)
  ansible.builtin.template:
    src: rclone.conf.j2
    dest: /root/.config/rclone/rclone.conf
    mode: "0600"

- name: Install backup script
  ansible.builtin.template:
    src: db-backup.sh.j2
    dest: /usr/local/bin/db-backup.sh
    mode: "0750"

- name: Nightly backup cron (02:30)
  ansible.builtin.cron:
    name: "db offsite backup"
    minute: "30"
    hour: "2"
    job: "/usr/local/bin/db-backup.sh >> /var/log/db-backup.log 2>&1"
```

- Bucket name + access keys come from Terraform outputs → `group_vars/vault.yml`
  (`backup_remote`, `backup_bucket`, key/secret, `backup_gpg_passphrase`).
- Apply the GFS **retention** via the bucket's lifecycle rule (set in Terraform), not the script.
- Add a documented **restore command** to the README and run a quarterly restore drill.
{% endraw %}

---

## Laravel + Forge — no Ansible app config

Do not generate runtime/deploy roles for Laravel. Instead emit these high-level steps in
the IaC README (mirrors the Forge section of `references/terraform.md`):

1. Provision infra with Terraform (droplet, managed DB, Redis, Spaces, firewall, DNS).
2. Connect the server to **Forge**; create a site per sub-domain, set PHP version + web root.
3. Paste DB/Redis credentials (Terraform outputs) into the site `.env` in Forge.
4. Enable Let's Encrypt SSL per domain in Forge.
5. Configure Forge deploy script (`composer install --no-dev`, `artisan migrate --force`,
   `config:cache`, `queue:restart`), Horizon daemon, and the scheduler cron.
6. Connect the Git repo and enable auto-deploy (or GitHub Actions → Forge deploy webhook).
7. **Backups:** enable the managed DB's automated backups, **and** add a Forge **scheduled
   job** running the offsite dump script (the `db-backup.sh` above, via `rclone` to
   S3/R2/GCS) — Forge supervises the cron, no Ansible needed. Set bucket lifecycle for GFS
   retention in Terraform, and document the restore command.

---

## README.md to emit (checklist)

- Prerequisites: ansible ≥ 2.15, the required collections (`community.general`), SSH access.
- Fill `inventory/hosts.ini` from `terraform output`.
- `ansible-vault create group_vars/vault.yml` and add secrets.
- Dry run: `ansible-playbook site.yml --check`. Apply: `ansible-playbook site.yml --ask-vault-pass`.
- Re-running is safe (idempotent) — that's the deploy mechanism for updates.

## Validation before presenting

- All roles are idempotent (use `creates:`, state modules, not blind shells where avoidable).
- No plaintext secrets — everything sensitive references `vault.yml`.
- Nginx vhost + certbot cover every sub-domain from the form.
- Inventory placeholders clearly map to Terraform outputs.
