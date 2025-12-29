# Guía de Instalación Completa

Esta guía describe el proceso completo de instalación del sistema de votación blockchain con Django, incluyendo tanto el backend Django como la integración blockchain.

## Tabla de Contenidos

- [Prerrequisitos](#prerrequisitos)
- [Instalación Básica (Solo Django)](#instalación-básica-solo-django)
- [Instalación Completa (Django + Blockchain)](#instalación-completa-django--blockchain)
- [Configuración Avanzada](#configuración-avanzada)
- [Verificación de la Instalación](#verificación-de-la-instalación)
- [Solución de Problemas](#solución-de-problemas)

## Prerrequisitos

### Requisitos de Software

#### Para Instalación Básica:
- **Python**: 3.8 o superior
- **pip**: Gestor de paquetes de Python
- **Git**: Para clonar el repositorio
- **Virtualenv**: Recomendado para aislar dependencias

#### Para Instalación Completa (adicionales):
- **Node.js**: 22.0 o superior (requerido por Hardhat 3.x)
- **npm**: Incluido con Node.js
- **Hardhat**: Framework de desarrollo Ethereum

### Verificar Versiones

```bash
# Verificar Python
python --version  # Debería mostrar Python 3.8+

# Verificar pip
pip --version

# Verificar Git
git --version

# Para instalación blockchain:
# Verificar Node.js
node --version  # Debería mostrar v22.0+

# Verificar npm
npm --version
```

### Actualizar Node.js (si es necesario)

Si tienes una versión antigua de Node.js:

**En Linux/macOS:**
```bash
# Usando nvm (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 22
nvm use 22
```

**En Windows:**
- Descargar el instalador desde [nodejs.org](https://nodejs.org/)
- Ejecutar el instalador y seguir las instrucciones

## Instalación Básica (Solo Django)

Esta instalación te permite usar el sistema sin funcionalidades blockchain.

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Jorgez-tech/encuestas.git
cd encuestas
```

### 2. Crear Entorno Virtual

**En Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**En Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

Deberías ver `(venv)` al inicio de tu línea de comando.

### 3. Instalar Dependencias de Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Dependencias instaladas:**
- Django>=4.2.15
- web3>=6.11.0
- eth-account>=0.13.0
- python-dotenv>=0.16.0

### 4. Configurar Base de Datos

```bash
# Aplicar migraciones
python manage.py migrate

# Crear superusuario para el admin
python manage.py createsuperuser
```

Sigue las instrucciones para crear tu usuario administrador:
- Username: [tu nombre de usuario]
- Email: [tu email]
- Password: [tu contraseña segura]

### 5. Iniciar el Servidor de Desarrollo

```bash
python manage.py runserver
```

### 6. Acceder a la Aplicación

- **App principal**: http://127.0.0.1:8000/polls/
- **Panel de administración**: http://127.0.0.1:8000/admin/
  - Usa las credenciales del superusuario creado en el paso 4

### 7. Modo Mock (Opcional)

El sistema incluye un modo mock que simula blockchain sin necesidad de conexión real.

Para forzar el modo mock, crea un archivo `.env` en la raíz del proyecto:

```bash
# .env
BLOCKCHAIN_MOCK_MODE=True
```

## Instalación Completa (Django + Blockchain)

Esta instalación incluye todas las funcionalidades blockchain.

### 1. Completar Instalación Básica

Primero completa todos los pasos de la [Instalación Básica](#instalación-básica-solo-django).

### 2. Instalar Dependencias de Node.js

Navega al directorio blockchain:

```bash
cd blockchain
```

Instala las dependencias:

```bash
npm install
```

**Dependencias principales:**
- hardhat: ^3.0.7
- @openzeppelin/contracts: ^5.2.0
- ethers: ^6.x
- @nomicfoundation/hardhat-toolbox: ^5.0.0

### 3. Configurar Hardhat

El proyecto ya incluye un archivo `hardhat.config.ts` configurado. Revísalo:

```bash
cat hardhat.config.ts
```

### 4. Compilar Smart Contracts

```bash
npx hardhat compile
```

**Salida esperada:**
```
Compiled 2 Solidity files with solc 0.8.28 successfully
```

### 5. Iniciar Red Blockchain Local

Abre una nueva terminal y ejecuta:

```bash
cd blockchain
npx hardhat node
```

Esto iniciará una red Ethereum local en `http://127.0.0.1:8545`. 

**Importante**: Deja esta terminal abierta mientras trabajas con blockchain.

**Salida esperada:**
```
Started HTTP and WebSocket JSON-RPC server at http://127.0.0.1:8545/
Accounts:
Account #0: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 (10000 ETH)
...
```

### 6. Desplegar Smart Contract

En una nueva terminal (manteniendo la red Hardhat activa):

```bash
cd blockchain
npx hardhat ignition deploy ignition/modules/VotingContract.ts --network localhost
```

**Salida esperada:**
```
✅ VotingContract deployed to: 0x5FbDB2315678afecb367f032d93F642f64180aa3
```

**Importante**: Guarda la dirección del contrato desplegado.

### 7. Configurar Variables de Entorno

Crea o edita el archivo `.env` en la raíz del proyecto:

```bash
# .env
WEB3_PROVIDER_URL=http://127.0.0.1:8545
BLOCKCHAIN_CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
BLOCKCHAIN_CHAIN_ID=31337
BLOCKCHAIN_MOCK_MODE=False
```

**Reemplaza** `BLOCKCHAIN_CONTRACT_ADDRESS` con la dirección que obtuviste en el paso 6.

### 8. Actualizar Configuración de Django

Si no estás usando `.env`, puedes configurar directamente en `encuestas/settings.py`:

```python
# encuestas/settings.py
BLOCKCHAIN_CONFIG = {
    'WEB3_PROVIDER_URL': 'http://127.0.0.1:8545',
    'CONTRACT_ADDRESS': '0x5FbDB2315678afecb367f032d93F642f64180aa3',  # Tu dirección
    'CHAIN_ID': 31337,
    'MOCK_MODE': False,
}
```

### 9. Verificar Conexión Blockchain

```bash
# En la raíz del proyecto (con venv activado)
python manage.py blockchain_sync status
```

**Salida esperada:**
```
✅ Blockchain Connection: ACTIVE
✅ Contract Address: 0x5FbDB2315678afecb367f032d93F642f64180aa3
✅ Network: Hardhat Local (Chain ID: 31337)
```

### 10. Sincronizar Preguntas con Blockchain

```bash
# Sincronizar todas las preguntas
python manage.py blockchain_sync sync_all

# O sincronizar una pregunta específica
python manage.py blockchain_sync sync_question --question-id 1
```

### 11. Acceder al Dashboard Blockchain

Inicia el servidor Django:

```bash
python manage.py runserver
```

Accede a:
- **Dashboard Blockchain**: http://127.0.0.1:8000/admin/polls/blockchainquestion/blockchain-dashboard/

## Configuración Avanzada

### Configurar Cuenta del Owner

El contrato tiene un "owner" que es la única cuenta que puede crear preguntas. Por defecto, es la primera cuenta de Hardhat.

**Ver cuentas disponibles en Hardhat:**
```bash
npx hardhat node
# Verás una lista de cuentas con sus claves privadas
```

**Configurar en Django (opcional):**
```python
# encuestas/settings.py
BLOCKCHAIN_CONFIG = {
    # ... otras configuraciones
    'OWNER_PRIVATE_KEY': '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80',
}
```

⚠️ **NUNCA** commities claves privadas reales a git. Usa variables de entorno en producción.

### Configurar PostgreSQL (Producción)

Para producción, es recomendable usar PostgreSQL en lugar de SQLite.

**1. Instalar PostgreSQL y dependencias:**
```bash
pip install psycopg2-binary
```

**2. Crear base de datos:**
```sql
CREATE DATABASE encuestas_db;
CREATE USER encuestas_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE encuestas_db TO encuestas_user;
```

**3. Actualizar settings.py:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'encuestas_db',
        'USER': 'encuestas_user',
        'PASSWORD': 'tu_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

**4. Migrar:**
```bash
python manage.py migrate
```

### Configurar Redis para Caché (Opcional)

```bash
# Instalar dependencias
pip install django-redis redis

# En settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

## Verificación de la Instalación

### Checklist de Verificación

#### Instalación Básica:
- [ ] Django se inicia sin errores
- [ ] Puedes acceder a http://127.0.0.1:8000/polls/
- [ ] Puedes acceder al admin http://127.0.0.1:8000/admin/
- [ ] Puedes crear preguntas en el admin
- [ ] Puedes votar en la interfaz pública

#### Instalación Blockchain:
- [ ] Hardhat node se ejecuta sin errores
- [ ] Smart contract desplegado exitosamente
- [ ] `blockchain_sync status` muestra conexión activa
- [ ] Puedes sincronizar preguntas con blockchain
- [ ] Dashboard blockchain muestra estadísticas correctas
- [ ] Puedes crear votos que se registran en blockchain

### Comandos de Diagnóstico

```bash
# Verificar estado del sistema
python manage.py blockchain_sync status

# Verificar preguntas sincronizadas
python manage.py blockchain_sync sync_all --verbose

# Verificar deployment del contrato
cd blockchain
npx hardhat run scripts/deploy.js --network localhost

# Ver logs de Django
python manage.py runserver --verbosity 2
```

### Tests

Ejecuta los tests para verificar que todo funciona:

```bash
# Tests básicos de Django
python manage.py test polls

# Tests de integración blockchain
python manage.py test polls.blockchain

# Tests específicos
python test_django_basic.py
python test_hybrid_models.py
python test_web3_integration.py
```

## Solución de Problemas

### Problema: "Module not found" al importar web3

**Solución:**
```bash
pip install --upgrade web3 eth-account
```

### Problema: Hardhat no se instala (Node.js viejo)

**Error**: `hardhat requires Node.js 22 or higher`

**Solución**: Actualizar Node.js a versión 22+
```bash
nvm install 22
nvm use 22
npm install
```

### Problema: Smart contract no se despliega

**Error**: `Error: could not detect network`

**Solución**: Verifica que Hardhat node esté corriendo
```bash
# En una terminal separada
cd blockchain
npx hardhat node
```

### Problema: Django no conecta con blockchain

**Error**: `Connection refused to http://127.0.0.1:8545`

**Soluciones**:
1. Verifica que Hardhat node esté corriendo
2. Verifica la URL en `.env` o `settings.py`
3. Usa modo mock para desarrollo:
   ```bash
   echo "BLOCKCHAIN_MOCK_MODE=True" >> .env
   ```

### Problema: "Transaction reverted" al votar

**Posibles causas**:
1. Ya votaste con esa dirección (un voto por wallet)
2. La pregunta no existe en blockchain
3. Índice de opción inválido

**Solución**: Verifica en el dashboard de blockchain si la pregunta está sincronizada.

### Problema: Migraciones fallan

**Error**: `django.db.utils.OperationalError`

**Soluciones**:
```bash
# Eliminar base de datos y recrear
rm db.sqlite3
python manage.py migrate

# O resetear migraciones específicas
python manage.py migrate polls zero
python manage.py migrate
```

### Problema: Puerto 8545 ya en uso

**Error**: `Error: listen EADDRINUSE: address already in use 127.0.0.1:8545`

**Solución**:
```bash
# En Linux/macOS
lsof -i :8545
kill -9 [PID]

# En Windows
netstat -ano | findstr :8545
taskkill /PID [PID] /F

# O usa otro puerto
npx hardhat node --port 8546
```

### Problema: Permisos en Linux

**Error**: `Permission denied` al instalar paquetes

**Solución**:
```bash
# Usar pip con --user
pip install --user -r requirements.txt

# O arreglar permisos del venv
sudo chown -R $USER:$USER venv/
```

## Próximos Pasos

Después de completar la instalación:

1. **Lee la [Guía de Desarrollo](DEVELOPMENT.md)** para aprender a desarrollar nuevas features
2. **Explora la [Arquitectura](ARCHITECTURE.md)** para entender el sistema en profundidad
3. **Revisa la [Documentación de Blockchain](BLOCKCHAIN.md)** para detalles técnicos
4. **Consulta la [Guía de Despliegue](DEPLOYMENT.md)** cuando estés listo para producción

## Recursos Adicionales

- [Documentación de Django](https://docs.djangoproject.com/)
- [Documentación de Hardhat](https://hardhat.org/docs)
- [Web3.py Documentation](https://web3py.readthedocs.io/)
- [Solidity Documentation](https://docs.soliditylang.org/)
- [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts/)

---

**Última Actualización**: Diciembre 2025  
**Autor**: @Jorgez-tech

Si encuentras problemas no cubiertos en esta guía, por favor [abre un issue](https://github.com/Jorgez-tech/encuestas/issues) en GitHub.
