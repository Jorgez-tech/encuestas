# Historial de Despliegues - Proyecto Original

Este documento registra los despliegues exitosos del proyecto original de encuestas Django, antes de su evolución hacia Web3/Blockchain.

## Contexto

El proyecto "Encuestas Django" tuvo varias fases de desarrollo y despliegue:

1. **Fase 1**: Desarrollo inicial en GitHub (repositorio original)
2. **Fase 2**: Despliegues exitosos desde GitHub (GitHub Pages, DigitalOcean, Supabase)
3. **Fase 3**: Copia de respaldo en GitLab (preservación del primer proyecto exitoso)
4. **Fase 4**: Evolución a proyecto Web3 en GitHub (repositorio actual)

> **Nota**: El proyecto actual es una evolución completamente aislada enfocada en blockchain/Web3. Los despliegues documentados aquí corresponden a la versión tradicional del proyecto, realizados cuando el proyecto aún no había evolucionado.

---

## GitHub (Repositorio Original)

El proyecto nació y se desarrolló en GitHub. Todos los despliegues exitosos se realizaron desde este repositorio.

- **Repositorio**: https://github.com/Jorgez-tech/encuestas
- **Estado**: Evolucionado a Web3 (mismo repositorio)

---

## GitLab (Copia de Respaldo)

Se guardó una copia del proyecto en GitLab como respaldo del primer proyecto exitoso del autor, preservando el estado original antes de la transformación Web3.

- **Propósito**: Preservación histórica
- **Contenido**: Versión Django tradicional (sin blockchain)

### Configuración CI/CD de Referencia

**.gitlab-ci.yml** (ejemplo de configuración):
```yaml
stages:
  - test
  - deploy

test:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - python manage.py test

deploy_production:
  stage: deploy
  only:
    - main
  script:
    - apt-get update -qy
    - apt-get install -y ruby-dev
    - gem install dpl
    - dpl --provider=heroku --app=$HEROKU_APP_NAME --api-key=$HEROKU_API_KEY
```

---

## GitHub Pages

Se desplegó una demo estática del frontend en GitHub Pages desde el repositorio original.

- **Rama**: `gh-pages`
- **Contenido**: Archivos estáticos HTML/CSS/JS para demostración
- **Desplegado desde**: GitHub (repositorio original)
- **Estado**: Archivado

### Notas
La rama `gh-pages` aún existe en el repositorio pero corresponde al proyecto anterior (pre-Web3).

---

## DigitalOcean App Platform

Despliegue exitoso de la aplicación Django completa desde GitHub.

- **URL**: `https://sea-turtle-app-f4lnd.ondigitalocean.app/polls/`
- **Desplegado desde**: GitHub (repositorio original)
- **Estado**: Desplegado exitosamente (proyecto anterior)

### Configuración Utilizada

```yaml
name: encuestas-voting
services:
  - name: web
    github:
      repo: Jorgez-tech/encuestas
      branch: main
    run_command: gunicorn encuestas.wsgi:application
    environment_slug: python
    instance_count: 1
    instance_size_slug: basic-xxs
    routes:
      - path: /
```

### GitHub Actions para DigitalOcean

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to DigitalOcean
        uses: digitalocean/app_action@main
        with:
          app_name: encuestas-voting
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}
```

### Costos (DigitalOcean)

| Servicio | Costo Mensual |
|----------|---------------|
| App Platform Basic | $5-12 |
| PostgreSQL DB | $15 |
| Redis (opcional) | $15 |
| **Total** | ~$35-45/mes |

---

## Supabase

Se utilizó Supabase como alternativa de base de datos PostgreSQL gestionada.

- **Uso**: Base de datos PostgreSQL
- **Integración**: Django con `dj-database-url`
- **Desplegado desde**: GitHub (repositorio original)
- **Estado**: Despliegue exitoso

### Configuración Django para Supabase

```python
# settings.py
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
    )
}
```

---

## Lecciones Aprendidas

1. **GitHub como origen**: Todos los despliegues se realizaron desde GitHub
2. **DigitalOcean App Platform**: Excelente para Django, fácil integración con GitHub
3. **Supabase**: Buena alternativa gratuita para PostgreSQL en proyectos pequeños
4. **GitHub Pages**: Útil para contenido estático y demos
5. **GitLab como backup**: Ideal para preservar versiones históricas de proyectos exitosos

---

## Estado Actual

El proyecto ha evolucionado hacia una **DApp (Aplicación Descentralizada)** con:
- Smart contracts en Solidity
- Integración Web3.py con Django
- Votación inmutable en blockchain

Para información sobre el proyecto actual, consulta:
- [README.md](../../README.md)
- [ARCHITECTURE.md](../ARCHITECTURE.md)
- [BLOCKCHAIN.md](../BLOCKCHAIN.md)

---

**Última Actualización**: Enero 2026
**Autor**: @Jorgez-tech
