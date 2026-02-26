# Ansible playbook for BAR monitoring

> [!WARNING]
> This repo is work in progress, not finished, nothing to see here yet.

This is an [Ansible](https://en.wikipedia.org/wiki/Ansible_(software)) playbook for setting up central BAR monitoring server.

## Features

- **Grafana** - Data visualization and dashboards
- **VictoriaMetrics** - Time-series database for metrics storage
- **Dex** - OpenID Connect identity provider for authentication
- **OAuth2Proxy** - Authentication proxy for secure access
- **Caddy** - Reverse proxy with automatic TLS
- **Automated Backup System** - Comprehensive Grafana database backup and restore

## Backup System

This playbook includes a production-ready automated backup solution for Grafana databases:

### Key Features
- ✅ **Automated daily backups** with systemd timers
- ✅ **zstd compression** (96% compression ratio achieved)
- ✅ **Cloud storage support** via rclone (GCS, S3, etc.)
- ✅ **Comprehensive restore utility** with safety features
- ✅ **Database integrity verification** 
- ✅ **Automatic service management** during operations

### Quick Usage

```bash
# Manual backup
/usr/local/bin/grafana-backup.sh

# Restore from backup
/usr/local/bin/grafana-restore.sh --yes grafana-20260225161455.db.zst

# Check backup status
systemctl status grafana-backup.timer
```

## Local testing

### Setup

We use Incus for local testing. Make sure you have it installed and initialized following [the official getting started docs](https://linuxcontainers.org/incus/docs/main/tutorial/first_steps/).

To create a new container and initialize it via cloud-init, run the following command:

```
touch .incus-integration-on && \
chmod 0600 test.ssh.key && \
incus launch images:debian/trixie/cloud bar-mon-test < test.incus.yml && \
incus exec bar-mon-test -- cloud-init status --wait
```

Then test that it works for ansible:

```
ansible dev -m shell -a 'uname -a'
```

The test container runs a few different services, and depends on a few `*.bar-mon.local` domain names pointing at the incus container so they are independently routable from web browser. Easiest is to add a new entry in `/etc/hosts` like:

```
{incus_container_ip} id.bar-mon.local grafana.bar-mon.local metrics.bar-mon.local
```

you can add/update it with:

```
ansible ,localhost -b -K -m lineinfile -a "path=/etc/hosts regexp='.*bar-mon.*' line='$(ansible-inventory --host test | jq -r '.ansible_host') id.bar-mon.local grafana.bar-mon.local metrics.bar-mon.local'"
```

### Usage

Now you can use all the playbooks and roles as usual, just make sure you are targeting the `dev` inventory group or `test` host. For example:

```
ansible-playbook -l dev play.yml
```

You can ssh into it with something like:

```
ssh -i test.ssh.key ansible@$(ansible-inventory --host test | jq -r '.ansible_host')
```

Or enter directly into root container shell with:

```
incus exec bar-mon-test -- /bin/bash
```

### Cleanup

To stop and remove the container:

```
incus stop bar-mon-test && incus delete bar-mon-test
```