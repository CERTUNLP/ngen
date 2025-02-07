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

### Start the app in Docker on production

This uses image on dockerhub.

```bash
$ cd docker
$ cp .env/ngen.prod.env.example .env/ngen.prod.env # Edit the .env file
$ docker compose up
```

## ✨ Default credentials

```
ngen:ngen
```
