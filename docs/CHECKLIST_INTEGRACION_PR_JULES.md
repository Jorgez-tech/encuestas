# Checklist de Integración: PR Clean Architecture Jules

## 📋 Pre-Merge Checklist

### Revisión de Código

- [ ] **Revisar entities.py**
  - [ ] Entidades son inmutables (dataclasses)
  - [ ] Sin dependencias de Django
  - [ ] Tipado correcto

- [ ] **Revisar interfaces.py**
  - [ ] Todos los métodos abstractos
  - [ ] Contratos claros y documentados
  - [ ] Uso correcto de ABC

- [ ] **Revisar use_cases/**
  - [ ] Lógica de negocio pura
  - [ ] Sin dependencias de frameworks
  - [ ] Logging apropiado
  - [ ] Manejo de errores

- [ ] **Revisar adapters/**
  - [ ] Implementan interfaces correctamente
  - [ ] Conversión Entity ↔ Model correcta
  - [ ] Manejo de excepciones Django

### Modificaciones Requeridas

#### 1. Agregar MockBlockchainGateway

- [ ] Crear `MockBlockchainGateway` en `polls/adapters/blockchain.py`
- [ ] Implementar todos los métodos de `IBlockchainGateway`
- [ ] Agregar método para simular eventos
- [ ] Documentar uso en tests

**Código a agregar:**
```python
# polls/adapters/blockchain.py

class MockBlockchainGateway(IBlockchainGateway):
    """Gateway simulado para testing sin blockchain real"""
    
    def __init__(self):
        self._mock_events: List[Dict[str, Any]] = []
        self._mock_questions: Dict[int, Dict[str, Any]] = {}
        self._current_block = 0
    
    def fetch_vote_events(self, from_block: int) -> List[Dict[str, Any]]:
        """Retorna eventos simulados desde el bloque especificado"""
        return [e for e in self._mock_events if e['block_number'] >= from_block]
    
    def create_question(self, text: str, choices: List[str]) -> Dict[str, Any]:
        """Simula creación de pregunta en blockchain"""
        import hashlib
        import time
        
        mock_id = len(self._mock_questions)
        mock_tx = "0x" + hashlib.sha256(
            f"{text}{time.time()}".encode()
        ).hexdigest()
        
        self._mock_questions[mock_id] = {
            'text': text,
            'choices': choices,
            'created_at': time.time()
        }
        
        logger.info(f"[MOCK] Created question {mock_id}: {text}")
        
        return {
            "success": True,
            "question_id": mock_id,
            "transaction_hash": mock_tx
        }
    
    def get_current_block_number(self) -> int:
        """Retorna número de bloque simulado"""
        return self._current_block
    
    # Métodos helper para testing
    def add_mock_vote_event(self, question_id: int, choice_index: int, 
                           voter: str, tx_hash: str = None):
        """Agrega evento de voto simulado"""
        if tx_hash is None:
            import hashlib, time
            tx_hash = "0x" + hashlib.sha256(
                f"{question_id}{choice_index}{voter}{time.time()}".encode()
            ).hexdigest()
        
        self._current_block += 1
        
        self._mock_events.append({
            'question_id': question_id,
            'choice_index': choice_index,
            'voter': voter,
            'tx_hash': tx_hash,
            'block_number': self._current_block,
            'log_index': len(self._mock_events)
        })
    
    def reset(self):
        """Resetea estado del mock"""
        self._mock_events.clear()
        self._mock_questions.clear()
        self._current_block = 0
```

#### 2. Agregar Transacciones Atómicas

- [ ] Agregar `@transaction.atomic` en `DjangoVoteRepository.save()`
- [ ] Agregar `@transaction.atomic` en `DjangoQuestionRepository.save()`
- [ ] Importar `from django.db import transaction`

**Código a modificar:**
```python
# polls/adapters/repositories.py

from django.db import transaction  # ← AGREGAR

class DjangoVoteRepository(IVoteRepository):
    @transaction.atomic  # ← AGREGAR
    def save(self, vote: VoteEntity) -> VoteEntity:
        try:
            question = BlockchainQuestion.objects.get(pk=vote.question_id)
        except BlockchainQuestion.DoesNotExist:
            raise ValueError(f"Question {vote.question_id} not found")
        
        BlockchainVote.objects.create(
            question=question,
            choice_index=vote.choice_index,
            voter_address=vote.voter_address,
            transaction_hash=vote.transaction_hash,
            block_number=vote.block_number,
            log_index=vote.log_index
        )
        return vote

class DjangoQuestionRepository(IQuestionRepository):
    @transaction.atomic  # ← AGREGAR
    def save(self, question: QuestionEntity) -> QuestionEntity:
        # ... código existente ...
```

#### 3. Actualizar requirements.txt

- [ ] Agregar `python-dotenv==1.0.0`
- [ ] Verificar versiones compatibles

**Comando:**
```bash
echo "python-dotenv==1.0.0" >> requirements.txt
```

#### 4. Crear .env.example

- [ ] Crear archivo `.env.example` en raíz
- [ ] Documentar todas las variables necesarias
- [ ] Agregar a `.gitignore` (`.env`)

**Contenido:**
```bash
# .env.example - Configuración del proyecto

# Blockchain Configuration
BLOCKCHAIN_PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
BLOCKCHAIN_CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
BLOCKCHAIN_RPC_URL=http://127.0.0.1:8545

# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (opcional, para producción)
# DATABASE_URL=postgresql://user:password@localhost/dbname
```

#### 5. Actualizar .gitignore

- [ ] Verificar que `.env` esté en `.gitignore`

**Agregar si no existe:**
```
# Environment variables
.env
.env.local
.env.*.local
```

#### 6. Actualizar Documentación

- [ ] Agregar sección "Clean Architecture" en `ARCHITECTURE.md`
- [ ] Actualizar `README.md` con nuevos comandos
- [ ] Documentar flujo de sincronización

**Sección a agregar en ARCHITECTURE.md:**
```markdown
## Clean Architecture Implementation

### Capas del Sistema

#### 1. Domain Layer (core/domain/)

**Entidades:**
- `Question`: Pregunta de votación con opciones
- `Choice`: Opción de respuesta
- `Vote`: Voto registrado en blockchain

**Interfaces:**
- `IQuestionRepository`: Persistencia de preguntas
- `IVoteRepository`: Persistencia de votos
- `IBlockchainGateway`: Comunicación con blockchain

**Características:**
- Sin dependencias externas
- Reglas de negocio puras
- Inmutable (dataclasses)

#### 2. Application Layer (core/use_cases/)

**Use Cases:**
- `SyncVotesUseCase`: Sincroniza votos desde blockchain
  - Implementa idempotencia con `tx_hash + log_index`
  - Valida existencia de preguntas
  - Registra errores con logging
  
- `GetQuestionResultsUseCase`: Calcula resultados
  - Agrega votos por opción
  - Calcula porcentajes
  - Retorna formato para presentación

**Características:**
- Orquesta entidades y repositorios
- Lógica de aplicación pura
- Testeable sin frameworks

#### 3. Infrastructure Layer (polls/adapters/)

**Adapters:**
- `DjangoQuestionRepository`: Implementa persistencia con Django ORM
- `DjangoVoteRepository`: Persistencia de votos
- `Web3BlockchainGateway`: Comunicación con smart contracts
- `MockBlockchainGateway`: Simulación para testing

**Características:**
- Implementan interfaces del dominio
- Conversión Entity ↔ Model
- Manejo de excepciones específicas

### Flujo de Datos

#### Sincronización Blockchain → DB

```
Blockchain Events → Gateway → Use Case → Repository → Database
```

1. `Web3BlockchainGateway.fetch_vote_events()` lee eventos
2. `SyncVotesUseCase.execute()` procesa eventos
3. Verifica idempotencia con `VoteRepository.exists()`
4. Guarda votos con `VoteRepository.save()`

#### Votación (futuro)

```
User → View → Use Case → Repository → Gateway → Blockchain
```

### Dependency Injection

```python
# En views
question_repo = DjangoQuestionRepository()
vote_repo = DjangoVoteRepository()
use_case = GetQuestionResultsUseCase(question_repo, vote_repo)
results = use_case.execute(question_id)
```

### Testing

```python
# Test unitario de use case
def test_sync_votes_use_case():
    # Arrange
    mock_gateway = MockBlockchainGateway()
    mock_gateway.add_mock_vote_event(1, 0, "0xabc...")
    
    question_repo = InMemoryQuestionRepository()
    vote_repo = InMemoryVoteRepository()
    
    use_case = SyncVotesUseCase(vote_repo, question_repo, mock_gateway)
    
    # Act
    count = use_case.execute(from_block=0)
    
    # Assert
    assert count == 1
    assert vote_repo.exists("0x...", 0)
```
```

#### 7. Crear Tests Básicos

- [ ] Test para `SyncVotesUseCase`
- [ ] Test para `GetQuestionResultsUseCase`
- [ ] Test para `MockBlockchainGateway`
- [ ] Test de integración básico

**Crear archivo:** `core/tests/__init__.py` y `core/tests/test_use_cases.py`

```python
# core/tests/test_use_cases.py

import pytest
from datetime import datetime
from core.domain.entities import Question, Choice, Vote
from core.use_cases.sync import SyncVotesUseCase
from polls.adapters.blockchain import MockBlockchainGateway


class InMemoryQuestionRepository:
    def __init__(self):
        self.questions = {}
    
    def get_by_blockchain_id(self, blockchain_id: int):
        return self.questions.get(blockchain_id)
    
    def save(self, question):
        self.questions[question.blockchain_id] = question
        return question


class InMemoryVoteRepository:
    def __init__(self):
        self.votes = []
    
    def exists(self, tx_hash: str, log_index: int):
        return any(
            v.transaction_hash == tx_hash and v.log_index == log_index 
            for v in self.votes
        )
    
    def save(self, vote):
        self.votes.append(vote)
        return vote


def test_sync_votes_use_case_basic():
    """Test sincronización básica de votos"""
    # Arrange
    mock_gateway = MockBlockchainGateway()
    question_repo = InMemoryQuestionRepository()
    vote_repo = InMemoryVoteRepository()
    
    # Crear pregunta
    question = Question(
        id=1,
        text="Test Question",
        pub_date=datetime.now(),
        blockchain_id=10,
        is_synced=True
    )
    question_repo.save(question)
    
    # Agregar evento mock
    mock_gateway.add_mock_vote_event(
        question_id=10,
        choice_index=0,
        voter="0xabc123"
    )
    
    use_case = SyncVotesUseCase(vote_repo, question_repo, mock_gateway)
    
    # Act
    count = use_case.execute(from_block=0)
    
    # Assert
    assert count == 1
    assert len(vote_repo.votes) == 1
    assert vote_repo.votes[0].voter_address == "0xabc123"


def test_sync_votes_idempotency():
    """Test que la sincronización no duplica votos"""
    # Arrange
    mock_gateway = MockBlockchainGateway()
    question_repo = InMemoryQuestionRepository()
    vote_repo = InMemoryVoteRepository()
    
    question = Question(
        id=1, text="Test", pub_date=datetime.now(),
        blockchain_id=10, is_synced=True
    )
    question_repo.save(question)
    
    mock_gateway.add_mock_vote_event(10, 0, "0xabc", tx_hash="0x123")
    
    use_case = SyncVotesUseCase(vote_repo, question_repo, mock_gateway)
    
    # Act - ejecutar dos veces
    count1 = use_case.execute(from_block=0)
    count2 = use_case.execute(from_block=0)
    
    # Assert
    assert count1 == 1
    assert count2 == 0  # No debe duplicar
    assert len(vote_repo.votes) == 1


def test_sync_votes_missing_question():
    """Test que maneja preguntas no encontradas"""
    # Arrange
    mock_gateway = MockBlockchainGateway()
    question_repo = InMemoryQuestionRepository()
    vote_repo = InMemoryVoteRepository()
    
    # No agregar pregunta
    mock_gateway.add_mock_vote_event(999, 0, "0xabc")
    
    use_case = SyncVotesUseCase(vote_repo, question_repo, mock_gateway)
    
    # Act
    count = use_case.execute(from_block=0)
    
    # Assert
    assert count == 0  # No debe crear voto sin pregunta
    assert len(vote_repo.votes) == 0
```

### Validación Final Pre-Merge

- [ ] **Código compila sin errores**
  ```bash
  python manage.py check
  ```

- [ ] **Tests pasan**
  ```bash
  python manage.py test
  ```

- [ ] **Migraciones generan correctamente**
  ```bash
  python manage.py makemigrations --dry-run
  ```

- [ ] **No hay dependencias circulares**
  ```bash
  # Verificar importaciones
  ```

- [ ] **Documentación completa**
  - [ ] README.md actualizado
  - [ ] ARCHITECTURE.md con nueva sección
  - [ ] Docstrings en código nuevo

---

## 🔀 Merge Process

### 1. Preparar Branch

```bash
# Actualizar branch con main
git checkout web3-clean-architecture-3330853478375242557
git rebase origin/main  # O merge si se prefiere

# Resolver conflictos si hay

# Push cambios
git push origin web3-clean-architecture-3330853478375242557 --force-with-lease
```

### 2. Revisar Cambios Finales

```bash
# Ver estadísticas de cambios
git diff origin/main..web3-clean-architecture-3330853478375242557 --stat

# Ver archivos modificados
git diff origin/main..web3-clean-architecture-3330853478375242557 --name-only
```

### 3. Ejecutar Merge

```bash
# Checkout main
git checkout main

# Merge (sin fast-forward para mantener historia)
git merge --no-ff web3-clean-architecture-3330853478375242557 \
  -m "feat: implement clean architecture for blockchain voting system

- Add core domain layer with entities and interfaces
- Implement SyncVotesUseCase for idempotent vote reconciliation
- Create infrastructure adapters for Django and Web3
- Add MockBlockchainGateway for testing
- Update models with log_index for idempotency
- Add run_reconciliation management command
- Create web3 views with clean architecture
- Secure configuration with environment variables

Co-authored-by: google-labs-jules[bot] <161369871+google-labs-jules[bot]@users.noreply.github.com>
Co-authored-by: Jorgez-tech <152639290+Jorgez-tech@users.noreply.github.com>"

# Push a origin
git push origin main
```

---

## 📦 Post-Merge Setup

### 1. Instalar Dependencias

```bash
# Actualizar dependencias
pip install -r requirements.txt

# O específicamente
pip install python-dotenv==1.0.0
```

### 2. Configurar Variables de Entorno

```bash
# Copiar ejemplo
cp .env.example .env

# Editar con valores reales
nano .env  # o tu editor preferido
```

**Variables a configurar:**
```
BLOCKCHAIN_PRIVATE_KEY=<tu_private_key>
BLOCKCHAIN_CONTRACT_ADDRESS=<tu_contract_address>
```

### 3. Ejecutar Migraciones

```bash
# Aplicar migración de log_index
python manage.py migrate

# Verificar
python manage.py showmigrations polls
```

**Salida esperada:**
```
polls
 [X] 0001_initial
 [X] 0002_blockchainchoice_blockchainquestion_blockchainvote
 [X] 0003_blockchainvote_log_index_and_more  # ← Nueva
```

### 4. Probar Comando de Reconciliación

```bash
# Ejecutar sincronización
python manage.py run_reconciliation --from-block=0

# Verificar en admin
python manage.py runserver
# Ir a: http://localhost:8000/admin/polls/blockchainvote/
```

### 5. Probar Vistas Web3

```bash
# Iniciar servidor
python manage.py runserver

# Visitar:
# http://localhost:8000/polls/web3/1/
# http://localhost:8000/polls/web3/1/results/
```

### 6. Ejecutar Tests

```bash
# Tests unitarios
python manage.py test core

# Tests de integración
python manage.py test polls.tests

# Todos los tests
python manage.py test

# Con coverage
coverage run --source='.' manage.py test
coverage report
```

---

## 📝 Post-Merge Documentation

### 1. Actualizar README.md

- [ ] Agregar sección "Arquitectura Limpia"
- [ ] Documentar comando `run_reconciliation`
- [ ] Actualizar instrucciones de setup

### 2. Crear Guía de Migración

- [ ] Documentar cómo migrar código antiguo
- [ ] Ejemplos de antes/después
- [ ] Timeline de deprecación

### 3. Comunicar Cambios

- [ ] Email/mensaje al equipo
- [ ] Demo en reunión de equipo
- [ ] Sesión de Q&A

**Template de comunicación:**
```
Subject: [IMPORTANTE] Nueva arquitectura Clean Architecture integrada

Hola equipo,

Hemos integrado una refactorización importante del sistema hacia Clean Architecture.

📋 Cambios principales:
- Nueva estructura de capas: core/domain, core/use_cases, polls/adapters
- Mejor separación de responsabilidades
- Mayor testabilidad
- Comando de reconciliación: python manage.py run_reconciliation

📚 Documentación:
- docs/ARCHITECTURE.md (actualizado)
- docs/PR_ANALYSIS_JULES_CLEAN_ARCHITECTURE.md
- docs/PR_JULES_RESUMEN_EJECUTIVO.md

⚠️ Acción requerida:
1. Pull latest main
2. pip install -r requirements.txt
3. Configurar .env (ver .env.example)
4. python manage.py migrate
5. Leer documentación

💬 Preguntas: Disponible para Q&A en [fecha/hora]

Saludos,
[Tu nombre]
```

---

## 🔄 Roadmap de Migración

### Sprint 1 (Semanas 1-2)

- [ ] **Familiarización**
  - [ ] Equipo lee documentación
  - [ ] Sesión de capacitación
  - [ ] Pair programming

- [ ] **Tests**
  - [ ] Agregar tests para SyncVotesUseCase
  - [ ] Agregar tests para GetQuestionResultsUseCase
  - [ ] Agregar tests de integración

- [ ] **Documentación**
  - [ ] Completar docstrings
  - [ ] Ejemplos de uso
  - [ ] Troubleshooting guide

### Sprint 2 (Semanas 3-4)

- [ ] **Migración de Vistas**
  - [ ] Identificar vistas a migrar
  - [ ] Migrar `index` view
  - [ ] Migrar `detail` view
  - [ ] Migrar `vote` view

- [ ] **Deprecación**
  - [ ] Marcar `BlockchainVotingService` como deprecated
  - [ ] Agregar warnings
  - [ ] Documentar alternativas

### Sprint 3 (Semanas 5-6)

- [ ] **Nuevas Features**
  - [ ] Implementar sincronización automática
  - [ ] Agregar Celery task
  - [ ] Configurar cron/scheduler

- [ ] **Optimización**
  - [ ] Profiling de performance
  - [ ] Agregar cache si necesario
  - [ ] Optimizar queries

### Sprint 4+ (Meses 2-3)

- [ ] **Limpieza Final**
  - [ ] Eliminar código deprecated
  - [ ] Consolidar tests
  - [ ] Auditoría de seguridad

- [ ] **Mejoras Avanzadas**
  - [ ] Manejo de reorgs blockchain
  - [ ] Sistema de confirmaciones
  - [ ] Monitoreo y alertas

---

## ✅ Checklist de Validación Post-Merge

### Funcionalidad

- [ ] Crear pregunta blockchain funciona
- [ ] Votación Web3 funciona
- [ ] Resultados se muestran correctamente
- [ ] Sincronización manual funciona
- [ ] Admin panel accesible
- [ ] No hay errores 500

### Performance

- [ ] Tiempo de respuesta < 500ms
- [ ] Queries N+1 resueltas
- [ ] No memory leaks

### Seguridad

- [ ] Private keys no en código
- [ ] Variables de entorno configuradas
- [ ] CSRF protection activo
- [ ] SQL injection protected

### Calidad de Código

- [ ] Tests passing
- [ ] Coverage > 70%
- [ ] Linter passing
- [ ] No warnings críticos

---

## 🚨 Rollback Plan (si algo falla)

### Opción 1: Revert Commit

```bash
# Si problemas críticos inmediatos
git revert HEAD
git push origin main
```

### Opción 2: Feature Flag

```python
# settings.py
USE_CLEAN_ARCHITECTURE = os.getenv('USE_CLEAN_ARCHITECTURE', 'false').lower() == 'true'

# views.py
if settings.USE_CLEAN_ARCHITECTURE:
    # Usar nuevos use cases
else:
    # Usar código viejo
```

### Opción 3: Rollback Parcial

```bash
# Revertir solo archivos específicos
git checkout HEAD~1 -- polls/views.py
git commit -m "rollback: revert views to previous version"
```

---

## 📞 Contactos y Soporte

- **Arquitecto:** [Nombre]
- **Tech Lead:** [Nombre]
- **Documentación:** docs/
- **Issues:** GitHub Issues
- **Chat:** [Canal de Slack/Discord]

---

**Última actualización:** 30 de enero de 2026  
**Versión:** 1.0  
**Mantenedor:** [Tu nombre/equipo]
