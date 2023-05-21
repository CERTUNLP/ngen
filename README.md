# [Ngen Django Backend](https://github.com/CERTUNLP/ngen)
## ✨ Quick Start in `Docker`

> Get the code

```bash
$ git clone https://github.com/CERTUNLP/ngen.git
$ cd ngen
```

> Start the app in Docker on develop mode

```bash
$ cd docker
$ docker compose up --build 
```

> API server on port `8000`

## ✨ Default credentials
```javascript
ngen:ngen
```

> Start the app in Docker on production

This uses image on dockerhub.
Set `DJANGO_DEBUG=False` in the file `ngen.env` and:

```bash
$ cd docker
$ docker compose -f docker-compose-prod.yml up
```

> Start with elasticsearch

Note: If you want to disable it set `ELASTIC_ENABLED=false` and remove containers (maybe you need to prune).
Set `ELASTIC_ENABLED=true` in the file `ngen.env` and:

```bash
$ cd docker
$ docker compose --profile elastic up
```

> Build and push image to dockerhub

```bash
$ docker build -t certunlp/ngen-django:latest -f docker/Dockerfile .
$ docker push certunlp/ngen-django
```
