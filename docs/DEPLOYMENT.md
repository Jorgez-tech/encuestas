# Guía de Despliegue

Esta guía describe cómo desplegar el sistema de votación blockchain con Django en diferentes entornos y plataformas.

## Tabla de Contenidos

- [Consideraciones Previas](#consideraciones-previas)
- [Despliegue en Desarrollo](#despliegue-en-desarrollo)
- [Despliegue en Testnet](#despliegue-en-testnet)
- [Despliegue en Producción](#despliegue-en-producción)
- [Plataformas de Hosting](#plataformas-de-hosting)
- [CI/CD](#cicd)
- [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)

## Consideraciones Previas

### Checklist Pre-Despliegue

- [ ] Todos los tests pasan
- [ ] Smart contracts auditados (para producción)
- [ ] Variables de entorno configuradas
- [ ] Base de datos de producción lista
- [ ] Backup strategy definida
- [ ] Monitoring configurado
- [ ] SSL/TLS configurado
- [ ] Dominio y DNS configurados

### Ambientes

```
Development  → Local, mock mode, SQLite
    ↓
Staging      → Similar a producción, testnet, PostgreSQL
    ↓
Production   → Mainnet, PostgreSQL, Redis, monitoring completo
```

## Despliegue en Desarrollo

### Local con Hardhat Network

**1. Backend Django**:
```bash
# Activar entorno virtual
source venv/bin/activate

# Variables de entorno
export DEBUG=True
export BLOCKCHAIN_MOCK_MODE=False

# Iniciar servidor
python manage.py runserver 0.0.0.0:8000
```

**2. Blockchain Local**:
```bash
# Terminal 1: Iniciar Hardhat Network
cd blockchain
npx hardhat node

# Terminal 2: Desplegar contrato
npx hardhat ignition deploy ignition/modules/VotingContract.ts --network localhost
```

**3. Verificar**:
```bash
python manage.py blockchain_sync status
python manage.py blockchain_sync sync_all
```

## Despliegue en Testnet

### Sepolia Testnet

#### 1. Preparación

**Obtener Sepolia ETH**:
- Faucet 1: https://sepoliafaucet.com/
- Faucet 2: https://sepolia-faucet.pk910.de/

**Crear Wallet**:
```bash
# Generar nueva wallet
npx hardhat run scripts/generate-wallet.js
# Guarda la private key de forma segura
```

#### 2. Configurar Hardhat para Sepolia

```typescript
// hardhat.config.ts
import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import * as dotenv from "dotenv";

dotenv.config();

const config: HardhatUserConfig = {
  solidity: "0.8.28",
  networks: {
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL || "https://rpc.sepolia.org",
      accounts: [process.env.SEPOLIA_PRIVATE_KEY!],
      chainId: 11155111,
    },
  },
  etherscan: {
    apiKey: process.env.ETHERSCAN_API_KEY,
  },
};

export default config;
```

**Archivo .env**:
```env
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR-PROJECT-ID
SEPOLIA_PRIVATE_KEY=0xYOUR_PRIVATE_KEY
ETHERSCAN_API_KEY=YOUR_ETHERSCAN_API_KEY
```

⚠️ **NUNCA** commitear el archivo `.env` con claves reales.

#### 3. Desplegar Smart Contract en Sepolia

```bash
cd blockchain

# Compilar
npx hardhat compile

# Desplegar
npx hardhat ignition deploy ignition/modules/VotingContract.ts --network sepolia

# Verificar en Etherscan (opcional)
npx hardhat verify --network sepolia <CONTRACT_ADDRESS>
```

**Salida esperada**:
```
✅ VotingContract deployed to: 0x1234567890abcdef...
Gas used: 2,500,000
Transaction hash: 0xabcdef...
```

#### 4. Configurar Django para Sepolia

```python
# settings.py (o .env)
BLOCKCHAIN_CONFIG = {
    'WEB3_PROVIDER_URL': 'https://sepolia.infura.io/v3/YOUR-PROJECT-ID',
    'CONTRACT_ADDRESS': '0x1234567890abcdef...',  # Tu contrato desplegado
    'CHAIN_ID': 11155111,
    'MOCK_MODE': False,
    'OWNER_PRIVATE_KEY': os.getenv('SEPOLIA_PRIVATE_KEY'),  # Para crear preguntas
}
```

#### 5. Verificar Conexión

```bash
python manage.py blockchain_sync status
```

**Salida esperada**:
```
✅ Blockchain Connection: ACTIVE
Network: Sepolia Testnet
Chain ID: 11155111
Contract Address: 0x1234...
```

## Despliegue en Producción

### Preparación para Mainnet

⚠️ **ADVERTENCIA**: Mainnet usa ETH real. Cada transacción tiene un costo monetario.

#### Checklist de Seguridad

- [ ] **Auditoría de Smart Contracts**: Contratar auditoría profesional
- [ ] **Testing exhaustivo**: Probar en testnet durante semanas
- [ ] **Bug Bounty**: Considerar programa de recompensas
- [ ] **Insurance**: Evaluar Nexus Mutual u otros
- [ ] **Multi-sig Wallet**: Usar para owner del contrato
- [ ] **Rate Limiting**: Implementar en Django
- [ ] **Monitoring**: Sistema de alertas 24/7

#### 1. Smart Contract en Mainnet

**NO DESPLEGUES EN MAINNET SIN AUDITORÍA**

```typescript
// hardhat.config.ts
networks: {
  mainnet: {
    url: process.env.MAINNET_RPC_URL || "https://mainnet.infura.io/v3/YOUR-PROJECT-ID",
    accounts: [process.env.MAINNET_PRIVATE_KEY!],
    chainId: 1,
    gasPrice: "auto",  // O especifica un valor
  },
}
```

```bash
# Desplegar (DESPUÉS de auditoría)
npx hardhat ignition deploy ignition/modules/VotingContract.ts --network mainnet

# Verificar en Etherscan
npx hardhat verify --network mainnet <CONTRACT_ADDRESS>
```

#### 2. Django en Producción

**Configuración de Seguridad**:

```python
# settings.py para producción

DEBUG = False

ALLOWED_HOSTS = ['tudominio.com', 'www.tudominio.com']

# Seguridad
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Base de datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': '5432',
    }
}

# Cache con Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Blockchain (Mainnet)
BLOCKCHAIN_CONFIG = {
    'WEB3_PROVIDER_URL': os.getenv('MAINNET_RPC_URL'),
    'CONTRACT_ADDRESS': os.getenv('CONTRACT_ADDRESS'),
    'CHAIN_ID': 1,  # Mainnet
    'MOCK_MODE': False,
    'OWNER_PRIVATE_KEY': os.getenv('MAINNET_PRIVATE_KEY'),
    'GAS_LIMIT': 500000,
    'GAS_PRICE_GWEI': 50,  # Ajustar según condiciones de red
}

# Static files
STATIC_ROOT = '/var/www/static/'
STATIC_URL = '/static/'

# Media files
MEDIA_ROOT = '/var/www/media/'
MEDIA_URL = '/media/'
```

#### 3. Variables de Entorno en Producción

**Usar herramienta de secrets management**:
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault
- Google Secret Manager

**Ejemplo con docker-compose**:
```yaml
version: '3.8'

services:
  web:
    build: .
    environment:
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - MAINNET_RPC_URL=${MAINNET_RPC_URL}
      - CONTRACT_ADDRESS=${CONTRACT_ADDRESS}
      - MAINNET_PRIVATE_KEY=${MAINNET_PRIVATE_KEY}
    env_file:
      - .env.production
```

## Plataformas de Hosting

### DigitalOcean (Actual)

**Documentado en README**: https://sea-turtle-app-f4lnd.ondigitalocean.app/polls/

#### Deployment con App Platform

1. **Conectar Repositorio**:
   - Login a DigitalOcean
   - App Platform → Create App
   - Seleccionar GitHub repository

2. **Configurar App**:
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

3. **Variables de Entorno**:
   - Configurar en App Platform → Settings → Environment Variables
   - Agregar todas las variables necesarias

4. **Base de Datos**:
   - Agregar PostgreSQL Database
   - Conectar automáticamente

5. **Desplegar**:
   - Click en "Deploy"
   - Monitorear logs

### Heroku

```bash
# Instalar Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Crear app
heroku create tu-app-name

# Agregar PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Agregar Redis (opcional)
heroku addons:create heroku-redis:hobby-dev

# Configurar variables
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=tu-secret-key
heroku config:set BLOCKCHAIN_MOCK_MODE=False
# ... más variables

# Desplegar
git push heroku main

# Migrar base de datos
heroku run python manage.py migrate

# Crear superusuario
heroku run python manage.py createsuperuser
```

**Procfile**:
```
web: gunicorn encuestas.wsgi:application
release: python manage.py migrate
```

**runtime.txt**:
```
python-3.11.0
```

### AWS (Amazon Web Services)

#### Opción 1: Elastic Beanstalk

```bash
# Instalar EB CLI
pip install awsebcli

# Inicializar
eb init -p python-3.11 tu-app-name

# Crear entorno
eb create production-env

# Desplegar
eb deploy

# Ver logs
eb logs
```

#### Opción 2: ECS (Elastic Container Service)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "encuestas.wsgi:application"]
```

```bash
# Build y push a ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker build -t tu-app .
docker tag tu-app:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/tu-app:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/tu-app:latest
```

### Google Cloud Platform

```bash
# Instalar gcloud CLI
curl https://sdk.cloud.google.com | bash

# Login
gcloud auth login

# Crear proyecto
gcloud projects create tu-proyecto-id

# Desplegar con App Engine
gcloud app deploy

# Ver logs
gcloud app logs tail -s default
```

**app.yaml**:
```yaml
runtime: python311

entrypoint: gunicorn -b :$PORT encuestas.wsgi:application

env_variables:
  DEBUG: 'False'
  SECRET_KEY: 'tu-secret-key'
  # ... más variables
```

### Docker + Docker Compose

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=encuestas_db
      - POSTGRES_USER=encuestas_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}

  redis:
    image: redis:7-alpine

  web:
    build: .
    command: gunicorn encuestas.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - static_volume:/app/static
      - media_volume:/app/media
    ports:
      - "8000:8000"
    env_file:
      - .env.production
    depends_on:
      - db
      - redis

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/var/www/static
      - media_volume:/var/www/media
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

**Comandos**:
```bash
# Build
docker-compose build

# Iniciar
docker-compose up -d

# Migrar
docker-compose exec web python manage.py migrate

# Collectstatic
docker-compose exec web python manage.py collectstatic --noinput

# Ver logs
docker-compose logs -f web
```

## CI/CD

### GitHub Actions

**.github/workflows/deploy.yml**:
```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          python manage.py test
        env:
          BLOCKCHAIN_MOCK_MODE: True
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to DigitalOcean
        uses: digitalocean/app_action@main
        with:
          app_name: encuestas-voting
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}
```

### GitLab CI/CD

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
  variables:
    BLOCKCHAIN_MOCK_MODE: "True"

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

## Monitoreo y Mantenimiento

### Monitoring con Sentry

```bash
pip install sentry-sdk
```

```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True,
)
```

### Logging

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/app.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
```

### Health Checks

```python
# urls.py
from django.http import JsonResponse
from polls.blockchain.services import BlockchainVotingService

def health_check(request):
    service = BlockchainVotingService()
    blockchain_status = service._check_connection()
    
    return JsonResponse({
        'status': 'healthy',
        'database': 'ok',
        'blockchain': 'connected' if blockchain_status else 'disconnected',
    })

urlpatterns = [
    path('health/', health_check),
    # ...
]
```

### Backups

```bash
# Backup PostgreSQL
pg_dump -U encuestas_user -h localhost encuestas_db > backup_$(date +%Y%m%d).sql

# Backup con compresión
pg_dump -U encuestas_user -h localhost encuestas_db | gzip > backup_$(date +%Y%m%d).sql.gz

# Restaurar
psql -U encuestas_user -h localhost encuestas_db < backup_20241229.sql
```

**Automatizar con cron**:
```bash
# Abrir crontab
crontab -e

# Backup diario a las 2 AM
0 2 * * * /home/user/scripts/backup.sh
```

### Monitoreo de Blockchain

```python
# Crear tarea periódica con Celery
from celery import shared_task
from polls.blockchain.services import BlockchainVotingService

@shared_task
def monitor_blockchain():
    service = BlockchainVotingService()
    
    if not service._check_connection():
        # Enviar alerta
        send_alert("Blockchain connection lost!")
    
    # Verificar gas prices
    gas_price = service.web3.eth.gas_price
    if gas_price > threshold:
        send_alert(f"High gas price: {gas_price} Gwei")
```

## Troubleshooting en Producción

### Problema: 502 Bad Gateway

**Posibles causas**:
1. Gunicorn no está corriendo
2. Puerto incorrecto
3. Permisos de socket

**Solución**:
```bash
# Verificar gunicorn
ps aux | grep gunicorn

# Reiniciar
sudo systemctl restart gunicorn
sudo systemctl status gunicorn
```

### Problema: Static files no cargan

**Solución**:
```bash
# Collectstatic
python manage.py collectstatic --noinput

# Verificar STATIC_ROOT en settings.py
# Verificar configuración de nginx/apache
```

### Problema: Blockchain timeout

**Solución**:
```python
# Aumentar timeout en Web3
from web3 import Web3
from web3.middleware import geth_poa_middleware

w3 = Web3(Web3.HTTPProvider(
    provider_url,
    request_kwargs={'timeout': 60}  # Aumentar a 60 segundos
))
```

## Costos Estimados

### Infrastructure (DigitalOcean)

- **App Platform Basic**: $5-12/mes
- **PostgreSQL DB**: $15/mes
- **Redis**: $15/mes (opcional)
- **Bandwidth**: Variable

**Total**: ~$35-45/mes

### Blockchain (Mainnet)

- **Gas para deployment**: ~$100-500 USD (una vez)
- **Gas por crear pregunta**: ~$5-20 USD
- **Gas por voto**: ~$1-5 USD

⚠️ Los costos de gas varían según congestión de red.

## Recursos Adicionales

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Security Best Practices](https://docs.djangoproject.com/en/stable/topics/security/)
- [Ethereum Gas Tracker](https://etherscan.io/gastracker)
- [Web3.py Provider](https://web3py.readthedocs.io/en/stable/providers.html)

---

**Última Actualización**: Diciembre 2024  
**Autor**: @Jorgez-tech

**⚠️ IMPORTANTE**: Para deployment en mainnet con fondos reales, se recomienda contratar consultoría especializada y auditoría de seguridad.
