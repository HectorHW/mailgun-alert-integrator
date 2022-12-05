# Mailgun alert integrator

This repository contains code for integration service responsible for stitching alertmanager's webhooks and mailgun HTTP api. This service may be useful if your cloud provider/isp/firewall blocks ports used by SMTP (eg. 587) thus making alertmanager's own SMTP integration unusable.

## Installation & Runnnig

Install dependencies using pip (virtualenv is recommended):

```bash
pip install -r requirements.txt
```

After installing dependencies, adjust configuration and simply run the script with python:

```bash
python main.py
```

## Configuration

| Parameter | Default | Description |
| ---- | ---- | ---- |
| MAILGUN_DOMAIN_NAME | `-` | (REQUIRED) domain name registered with mailgun (eg. `sandbox32foo.mailgun.org`) |
| MAILGUN_API_KEY | `-` | (REQUIRED) api key used for authentication with mailgun |
| MAILGUN_TARGET_EMAILS | `-` | (REQUIRED) list of emails to send emails separated with commas |
| FROM_USER | `alerts` | name (eg. Alert System) used in email |
| FROM_USER_EMAIL | `alerts` | actual email address that will take place of username in `username@domain` for sending emails from |
| BIND_ADDRESS | `0.0.0.0` | interface to bind to |
| BIND_PORT | `8080` | port to bind to |

To connect this service with alertmanager, add appropriate route and receiver entries in `alertmanager.yml`:

```yaml
receivers:

  # your other receivers

  - name: 'email'
    webhook_configs:
      - url: 'http://localhost:8080'

```
