# Historial de Despliegues - Proyecto Original

Este documento registra los despliegues exitosos del proyecto original de encuestas Django, antes de su evolución hacia Web3/Blockchain.

## Contexto

El proyecto "Encuestas Django" tuvo varias fases de desarrollo y despliegue:

1. **Fase 1**: Desarrollo inicial en GitLab
2. **Fase 2**: Despliegues en múltiples plataformas (GitHub Pages, DigitalOcean, Supabase)
3. **Fase 3**: Evolución a proyecto Web3 (repositorio actual)

> **Nota**: El proyecto actual es una evolución completamente aislada enfocada en blockchain/Web3. Los despliegues documentados aquí corresponden a la versión tradicional del proyecto.

---

## GitLab (Repositorio Original)

El proyecto fue desarrollado originalmente en GitLab antes de migrar a GitHub para la versión Web3.

### Configuración CI/CD Original

**.gitlab-ci.yml**:
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

Se desplegó una demo estática del frontend en GitHub Pages.

- **URL**: (demo estática - ya no disponible)
- **Rama**: `gh-pages`
- **Contenido**: Archivos estáticos HTML/CSS/JS para demostración
- **Estado**: Archivado

### Notas
La rama `gh-pages` aún existe en el repositorio pero corresponde al proyecto anterior, no a la versión Web3.

---

## DigitalOcean App Platform

Despliegue exitoso de la aplicación Django completa.

- **URL**: `https://sea-turtle-app-f4lnd.ondigitalocean.app/polls/`
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

1. **DigitalOcean App Platform**: Excelente para Django, fácil configuración con GitHub
2. **Supabase**: Buena alternativa gratuita para PostgreSQL en proyectos pequeños
3. **GitHub Pages**: Solo útil para contenido estático, no para aplicaciones Django
4. **GitLab CI/CD**: Robusto pero migrado a GitHub Actions para mejor integración

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
