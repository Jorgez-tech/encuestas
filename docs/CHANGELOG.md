# Changelog

Historial de cambios importantes del proyecto.

---

## [Clean Architecture Migration] - 30 Enero 2026

### 🎯 Migración Exitosa a Clean Architecture

**Implementación completada por Jules AI (Google Labs)**

#### ✅ Cambios Principales

**Nueva Estructura de Capas:**
```
core/
├── domain/          # Capa de dominio (entities + interfaces)
│   ├── entities.py  # Question, Choice, Vote (dataclasses)
│   └── interfaces.py # IQuestionRepository, IVoteRepository, IBlockchainGateway
├── use_cases/       # Lógica de negocio
│   ├── sync.py      # SyncVotesUseCase (blockchain → DB)
│   └── voting.py    # GetQuestionResultsUseCase
└── tests/           # Tests unitarios (sin DB/blockchain)
    └── test_use_cases.py # 12 tests (100% passing)

polls/adapters/      # Adaptadores a frameworks
├── blockchain.py    # Web3BlockchainGateway + MockBlockchainGateway
└── repositories.py  # DjangoQuestionRepository, DjangoVoteRepository
```

#### 🔧 Mejoras Implementadas

1. **MockBlockchainGateway**: Desarrollo local sin nodo Ethereum
2. **Transacciones Atómicas**: `@transaction.atomic` en repositories
3. **Idempotencia**: Sincronización con `tx_hash + log_index` únicos
4. **Suite de Tests**: 12 tests unitarios rápidos (< 0.01s)
5. **Configuración**: `.env.example` con variables requeridas
6. **Documentación**: `docs/ARCHITECTURE.md` actualizada con Clean Architecture

#### 📊 Resultados de Tests

```bash
$ python manage.py test core.tests.test_use_cases -v 2
Found 12 test(s).
Ran 12 tests in 0.008s
OK ✅
```

**Tests por Componente:**
- ✅ SyncVotesUseCase: 6 tests (básico, idempotencia, múltiples eventos, bloques específicos)
- ✅ GetQuestionResultsUseCase: 3 tests (sin votos, con votos, pregunta inexistente)
- ✅ MockBlockchainGateway: 4 tests (crear, eventos, reset)

#### 🎓 Beneficios de Clean Architecture

- **Testeable**: Tests sin base de datos ni blockchain (100x más rápido)
- **Independiente**: Dominio desacoplado de Django/Web3
- **Mantenible**: Cambios localizados por capas
- **Flexible**: Fácil migrar DB o blockchain sin romper lógica

#### 📝 Comandos Nuevos

```bash
# Sincronizar votos desde blockchain
python manage.py run_reconciliation --from-block=0

# Ejecutar tests unitarios
python manage.py test core.tests.test_use_cases -v 2
```

#### 🔗 Referencias

- PR Branch: `web3-clean-architecture-3330853478375242557` (merged)
- Commit: `876679e` (Pre-merge modifications)
- Documentación: [docs/ARCHITECTURE.md](ARCHITECTURE.md)

#### 👥 Créditos

- **Implementación**: Jules AI (Google Labs) - Clean Architecture refactoring
- **Revisión y Mejoras**: GitHub Copilot - MockGateway, tests, documentación
- **Proyecto**: Jorge ([@Jorgez-tech](https://github.com/Jorgez-tech))

---

## [v0.3.0] - Diciembre 2025

### Integración Blockchain Completada

- Smart contracts desplegados (VotingContract.sol)
- Sincronización Django <-> Blockchain
- Panel de administración blockchain
- Comandos de gestión (`blockchain_sync`)

---

## [v0.2.0] - Noviembre 2025

### Desarrollo Smart Contracts

- Solidity 0.8.28 con OpenZeppelin
- Hardhat environment setup
- Tests con Hardhat + TypeScript

---

## [v0.1.0] - Octubre 2025

### Versión Inicial

- Aplicación Django básica de votaciones
- Admin panel tradicional
- Modelos: Question, Choice
