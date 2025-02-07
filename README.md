![Black Logo](https://github.com/certunlp/ngen/blob/main/ngen/static/img/ngenlogo_big_light.png?raw=true)

<h2 align="center">Incident Response Management System</h2>

<p align="center">
<a href="https://github.com/certunlp/ngen/actions"><img alt="Actions Status" src="https://github.com/certunlp/ngen/actions/workflows/backend.yml/badge.svg"></a>
<a href="https://github.com/certunlp/ngen/actions"><img alt="Actions Status" src="https://github.com/certunlp/ngen/actions/workflows/frontend.yml/badge.svg"></a>
<img alt="Version" src="https://img.shields.io/badge/version-0.1.0-brightblue">
<a href="https://www.gnu.org/licenses/gpl-3.0"><img alt="License: GPL v3" src="https://img.shields.io/badge/License-GPLv3-blue.svg"></a>
<a href="https://github.com/certunlp/ngen"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

Ngen is a powerful security incident management system designed specifically for CSIRTs. It streamlines incident
tracking, automates repetitive tasks through integration with tools like IntelMQ, Cortex, Kintun, and MISP, and enhances
team collaboration. With features like artifact management, auditing, secure communication, and report generation, Ngen
empowers CSIRTs to respond swiftly to cyber threats, ensuring detailed documentation and thorough analysis of each
incident.

![Example Preview](https://github.com/certunlp/ngen/blob/main/docs/images/preview1.png?raw=true)

## ✨ Quick Start in `Docker`

### Get the code

```bash
$ git clone https://github.com/CERTUNLP/ngen.git
$ cd ngen
```

### Run with the install script

```bash
$ bash <(wget -qO- https://raw.githubusercontent.com/CERTUNLP/ngen/main/install.sh)
```

### Configure the app

There are four configuration files in the `docker/.env` directory. You can edit them to customize the app.

- `ngen.base.env`: Base configuration for the app, shared by all environments and overriden by other files.
- `ngen.base.db.env`: Database configuration for the app, shared by all environments and overriden by other files.
- `ngen.dev.env`: Development environment configuration for the app.
- `ngen.prod.env`: Production environment configuration for the app.

Important environment variables:

- DJANGO_SECRET_KEY: A secret key for a particular Django installation. This is used to provide cryptographic signing, and should be set to a unique, unpredictable value.
- DJANGO_ALLOWED_HOSTS: Is a list of domain names that API Django site can serve. This is a security measure to prevent HTTP Host header attacks, which are possible even under many seemingly-safe web server configurations. Example: 127.0.0.1,localhost,ngen.yourdomain.com
- DJANGO_CORS_ALLOWED_ORIGINS: A list of origins that are authorized to make cross-site HTTP requests. Keep empty to disable CORS, you can keep it empty for testing purposes. Example: https://ngen.yourdomain.com

- VITE_APP_API_SERVER: The URL of the API Django site, for produccion can be the same as the frontend URL on `/api` path.

- EMAIL_HOST: The host to use for sending email.
- EMAIL_PORT: The port to use for the SMTP server. 


### Start the app in Docker on production

This uses image from Docker Hub. It is useful for production. Please edit the `.env` file before running the command.

```bash
$ cd docker
$ cp .env/ngen.prod.env.example .env/ngen.prod.env # Edit the .env file
$ docker compose up
```

### Start the app in Docker on development

This builds the image locally. It is useful for development and testing.

```bash
$ cd docker
$ cp .env/ngen.dev.env.example .env/ngen.dev.env # Edit the .env file if needed
$ docker compose -f docker-compose.dev.yml up
```

## ✨ Default credentials

```
ngen:ngen
```
