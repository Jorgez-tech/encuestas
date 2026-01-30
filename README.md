# Sistema de Votación Blockchain con Django

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://www.djangoproject.com/)
[![Solidity](https://img.shields.io/badge/Solidity-0.8.28-blue.svg)](https://soliditylang.org/)
[![Hardhat](https://img.shields.io/badge/Hardhat-3.0+-orange.svg)](https://hardhat.org/)

Sistema de votación híbrido que combina la robustez de Django con la transparencia y seguridad de blockchain (Ethereum). Este proyecto ha evolucionado desde una aplicación de encuestas tradicional hacia una DApp (Aplicación Descentralizada) que garantiza transparencia en los procesos de votación.

## Características Principales

### Backend Django
- Panel de administración completo y profesional
- Gestión de preguntas y opciones de votación
- Sistema de usuarios y autenticación
- Visualización de resultados en tiempo real
- API para interacción con frontend

### Integración Blockchain
- Smart contracts en Solidity con OpenZeppelin
- Votación inmutable y transparente en blockchain
- Prevención de votos duplicados mediante wallets
- Sincronización automática Django <-> Blockchain
- Modo mock para desarrollo sin blockchain
- Dashboard de monitoreo blockchain

## Inicio Rápido

### Prerrequisitos
- Python 3.8+
- Node.js 22+ (para desarrollo blockchain)
- Git

### Instalación Básica (Sin Blockchain)

```bash
# Clonar el repositorio
git clone https://github.com/Jorgez-tech/encuestas.git
cd encuestas

# Crear entorno virtual
python -m venv venv
source venv/bin/activate # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver
```

**Acceder a la aplicación:**
- App principal: http://127.0.0.1:8000/polls/
- Panel admin: http://127.0.0.1:8000/admin/
- Dashboard blockchain: http://127.0.0.1:8000/admin/polls/blockchainquestion/blockchain-dashboard/

### Instalación Completa (Con Blockchain)

Para habilitar las funcionalidades blockchain completas, consulta la [Guía de Instalación Completa](docs/INSTALLATION.md).

## Documentación

- **[Arquitectura del Sistema](docs/ARCHITECTURE.md)** - Diseño y componentes del sistema
- **[Instalación Completa](docs/INSTALLATION.md)** - Guía detallada de instalación y configuración
- **[Integración Blockchain](docs/BLOCKCHAIN.md)** - Detalles técnicos de la integración blockchain
- **[Guía de Desarrollo](docs/DEVELOPMENT.md)** - Información para desarrolladores
- **[Despliegue](docs/DEPLOYMENT.md)** - Instrucciones de despliegue en producción

## Arquitectura

Este sistema utiliza una arquitectura híbrida:

```

## Arquitectura

### Clean Architecture (Enero 2026)

El sistema implementa **Clean Architecture** siguiendo los principios de Uncle Bob, con separación clara de capas:

**Estructura de Capas:**
```
┌─────────────────────────────────────────────────────────┐
│  Domain Layer (core/domain/)                            │
│  - Entities: Question, Choice, Vote (dataclasses)       │
│  - Interfaces: Repositories & Gateways (ABC)            │
│  ✓ Sin dependencias de frameworks                       │
└─────────────────────────────────────────────────────────┘
                         ▲
┌─────────────────────────────────────────────────────────┐
│  Use Cases Layer (core/use_cases/)                      │
│  - SyncVotesUseCase: Sincroniza blockchain → DB         │
│  - GetQuestionResultsUseCase: Calcula resultados        │
│  ✓ Lógica de negocio pura, 12 tests unitarios           │
└─────────────────────────────────────────────────────────┘
                         ▲
┌─────────────────────────────────────────────────────────┐
│  Adapters Layer (polls/adapters/)                       │
│  - Django ORM Repositories                              │
│  - Web3 & Mock Blockchain Gateways                      │
└─────────────────────────────────────────────────────────┘
                         ▲
┌─────────────────────────────────────────────────────────┐
│  Infrastructure (Django + Ethereum)                     │
│  - Views, Admin, Models | Smart Contracts               │
└─────────────────────────────────────────────────────────┘
```

**Beneficios:**
- ✅ **Tests sin DB/Blockchain**: 12 tests unitarios rápidos
- ✅ **Código desacoplado**: Cambiar frameworks sin romper lógica
- ✅ **Idempotencia**: Sincronización segura con tx_hash+log_index
- ✅ **MockGateway**: Desarrollo local sin nodo Ethereum

Ver [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) para detalles completos.

### Comandos de Gestión

```bash
# Sincronizar votos desde blockchain
python manage.py run_reconciliation --from-block=0

# Ejecutar suite de tests (12 tests)
python manage.py test core.tests.test_use_cases -v 2

# Crear pregunta en blockchain
python manage.py blockchain_sync create_question <question_id>
```

## Tecnologías Utilizadas

### Backend
- **Django 4.2+**: Framework web principal
- **Web3.py**: Integración con blockchain Ethereum
- **SQLite/PostgreSQL**: Base de datos
- **Python-dotenv**: Gestión de variables de entorno

### Blockchain
- **Solidity 0.8.28**: Lenguaje de smart contracts
- **Hardhat 3.0+**: Framework de desarrollo Ethereum
- **OpenZeppelin**: Librería de contratos seguros
- **Ethereum**: Red blockchain (local/testnet/mainnet)

### Frontend
- **HTML/CSS/JavaScript**: Interface tradicional
- **Web3.js**: Integración con wallets (futuro)
- **Bootstrap**: Framework CSS

## Estado del Proyecto

### ✅ Actualización: Clean Architecture (30 Enero 2026)

**Migración completada exitosamente**:
- ✅ Implementada Clean Architecture con separación de capas (Domain, Use Cases, Adapters)
- ✅ 12 tests unitarios en core/tests/test_use_cases.py (100% passing)
- ✅ MockBlockchainGateway para desarrollo sin nodo Ethereum
- ✅ Sincronización idempotente (tx_hash + log_index)
- ✅ Transacciones atómicas en repositorios (@transaction.atomic)
- ✅ Documentación actualizada en docs/ARCHITECTURE.md

**Fases del Proyecto:**
- **Fase 1**: ✅ Aplicación Django básica de encuestas
- **Fase 2**: ✅ Smart contracts desarrollados y desplegados
- **Fase 3**: ✅ Integración Django <-> Blockchain completada
- **Fase 4**: ✅ Panel de administración blockchain
- **Fase 5**: ✅ Comandos de gestión y sincronización
- **Fase 6**: ✅ Clean Architecture implementada (Enero 2026)
- **Fase 7**: 🔄 Frontend Web3 con wallet connection (en progreso)
- **Fase 8**: 📋 Deploy en testnet/mainnet (planeado)

## Casos de Uso

1. **Votaciones Organizacionales**: Decisiones transparentes en empresas/DAOs
2. **Encuestas Públicas**: Garantizar integridad de resultados
3. **Elecciones Estudiantiles**: Sistema verificable y auditable
4. **Polls Comunitarios**: Votaciones descentralizadas en comunidades

## Enlaces

- **Repositorio GitHub**: https://github.com/Jorgez-tech/encuestas
- **Documentación Completa**: [docs/](docs/)
- **Historial de Despliegues**: [docs/archive/LEGACY_DEPLOYMENTS.md](docs/archive/LEGACY_DEPLOYMENTS.md)

## Contribución

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## Autor

**Jorge** - [@Jorgez-tech](https://github.com/Jorgez-tech)

## Agradecimientos

- Django community por el excelente framework
- OpenZeppelin por los contratos seguros auditados
- Hardhat team por las herramientas de desarrollo
- Comunidad Ethereum por la documentación

---

**Nota**: Este proyecto es para fines educativos y de demostración. Para uso en producción, se recomienda una auditoría de seguridad completa de los smart contracts.
