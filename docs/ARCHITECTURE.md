# Arquitectura del Sistema

Este documento describe la arquitectura técnica del sistema de votación blockchain con Django.

## Tabla de Contenidos

- [Visión General](#visión-general)
- [Clean Architecture Implementation](#clean-architecture-implementation)
- [Capas del Sistema](#capas-del-sistema)
- [Componentes Principales](#componentes-principales)
- [Flujo de Datos](#flujo-de-datos)
- [Modelos de Datos](#modelos-de-datos)
- [Decisiones Arquitectónicas](#decisiones-arquitectónicas)

## Visión General

El sistema implementa una **arquitectura híbrida** que combina:
- **Django**: Backend tradicional para gestión, administración y almacenamiento
- **Blockchain Ethereum**: Capa de consenso y verificación para votaciones
- **Web3.py**: Puente de integración entre ambos mundos

### Principios de Diseño

1. **Separación de Responsabilidades**: Django maneja UI/admin, blockchain maneja consenso
2. **Degradación Elegante**: Sistema funcional incluso sin blockchain (modo mock)
3. **Sincronización Eventual**: Los datos se sincronizan de forma asíncrona
4. **Seguridad por Capas**: Validación tanto en Django como en smart contracts

## Clean Architecture Implementation

El proyecto implementa **Clean Architecture** (Uncle Bob) para separar la lógica de negocio de los detalles de implementación. Esto permite:

- **Independencia de frameworks**: La lógica de negocio no depende de Django o Web3
- **Testabilidad**: Casos de uso testeables sin infraestructura
- **Flexibilidad**: Fácil cambiar implementaciones sin afectar el dominio
- **Mantenibilidad**: Código más claro y organizado

### Estructura de Capas Clean Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│              (Django Views, Templates, Admin)                │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   Application Layer                          │
│                (Use Cases / Casos de Uso)                    │
│  • SyncVotesUseCase: Sincronización blockchain → DB         │
│  • GetQuestionResultsUseCase: Cálculo de resultados         │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                     Domain Layer                             │
│              (Entities & Interfaces puras)                   │
│  • Entities: Question, Choice, Vote                         │
│  • Interfaces: IQuestionRepository, IVoteRepository,        │
│                IBlockchainGateway                            │
└─────────────────────────────────────────────────────────────┘
                         ▲
┌────────────────────────┴────────────────────────────────────┐
│                  Infrastructure Layer                        │
│                 (Adapters & Frameworks)                      │
│  • DjangoQuestionRepository: Django ORM                     │
│  • DjangoVoteRepository: Django ORM                         │
│  • Web3BlockchainGateway: Web3.py                           │
│  • MockBlockchainGateway: Testing                           │
└─────────────────────────────────────────────────────────────┘
```

### Domain Layer (`core/domain/`)

**Entidades (Entities):**
```python
@dataclass
class Question:
    id: Optional[int]
    text: str
    pub_date: datetime
    choices: List[Choice]
    blockchain_id: Optional[int] = None
    is_synced: bool = False
    tx_hash: Optional[str] = None

@dataclass
class Vote:
    question_id: int
    choice_index: int
    voter_address: str
    transaction_hash: str
    block_number: int
    log_index: int  # Para idempotencia
    timestamp: Optional[datetime] = None
```

**Características:**
- Sin dependencias externas (solo Python estándar)
- Inmutables (dataclasses)
- Representan conceptos del negocio
- Reglas de negocio puras

**Interfaces (Contracts):**
```python
class IBlockchainGateway(ABC):
    @abstractmethod
    def fetch_vote_events(self, from_block: int) -> List[Dict[str, Any]]:
        """Obtiene eventos de votación desde blockchain"""
        pass
    
    @abstractmethod
    def create_question(self, text: str, choices: List[str]) -> Dict[str, Any]:
        """Crea pregunta en blockchain"""
        pass
```

### Application Layer (`core/use_cases/`)

**Use Case: SyncVotesUseCase**

Sincroniza votos desde blockchain a la base de datos con idempotencia:

```python
class SyncVotesUseCase:
    def execute(self, from_block: int = 0) -> int:
        events = self.blockchain_gateway.fetch_vote_events(from_block)
        new_votes_count = 0
        
        for event in events:
            # Verificar idempotencia
            if self.vote_repo.exists(event['tx_hash'], event['log_index']):
                continue
            
            # Obtener pregunta asociada
            question = self.question_repo.get_by_blockchain_id(
                event['question_id']
            )
            
            if question:
                vote = Vote(...)
                self.vote_repo.save(vote)
                new_votes_count += 1
        
        return new_votes_count
```

**Características:**
- Orquesta entidades y repositorios
- Lógica de aplicación pura
- Sin dependencias de frameworks
- Testeable con mocks in-memory

**Use Case: GetQuestionResultsUseCase**

Calcula y formatea resultados de votación:

```python
class GetQuestionResultsUseCase:
    def execute(self, question_id: int) -> Dict[str, Any]:
        question = self.question_repo.get_by_id(question_id)
        votes = self.vote_repo.get_votes_for_question(question_id)
        
        # Agregar votos por opción
        vote_counts = {i: 0 for i in range(len(question.choices))}
        for vote in votes:
            vote_counts[vote.choice_index] += 1
        
        # Calcular porcentajes y formatear
        return {
            'question_text': question.text,
            'total_votes': len(votes),
            'choices': [...],  # Con votos y porcentajes
            'is_synced': question.is_synced
        }
```

### Infrastructure Layer (`polls/adapters/`)

**Repositorios Django:**

Implementan las interfaces del dominio usando Django ORM:

```python
class DjangoVoteRepository(IVoteRepository):
    @transaction.atomic  # Garantiza atomicidad
    def save(self, vote: VoteEntity) -> VoteEntity:
        question = BlockchainQuestion.objects.get(pk=vote.question_id)
        BlockchainVote.objects.create(
            question=question,
            choice_index=vote.choice_index,
            voter_address=vote.voter_address,
            transaction_hash=vote.transaction_hash,
            block_number=vote.block_number,
            log_index=vote.log_index
        )
        return vote
```

**Características:**
- Conversión Entity ↔ Django Model
- Manejo de transacciones
- Validación de integridad referencial

**Gateway Web3:**

Encapsula comunicación con blockchain:

```python
class Web3BlockchainGateway(IBlockchainGateway):
    def fetch_vote_events(self, from_block: int):
        events = self.contract.events.VoteCast().get_logs(
            fromBlock=from_block
        )
        
        return [{
            'question_id': event['args']['questionId'],
            'choice_index': event['args']['choiceIndex'],
            'voter': event['args']['voter'],
            'tx_hash': event['transactionHash'].hex(),
            'block_number': event['blockNumber'],
            'log_index': event['logIndex']
        } for event in events]
```

**Mock Gateway para Testing:**

```python
class MockBlockchainGateway(IBlockchainGateway):
    """Gateway simulado sin blockchain real"""
    
    def add_mock_vote_event(self, question_id, choice_index, voter):
        """Helper para agregar eventos en tests"""
        self._mock_events.append({...})
    
    def reset(self):
        """Limpia estado entre tests"""
        self._mock_events.clear()
```

### Dependency Injection

Las dependencias se inyectan en las vistas:

```python
# polls/views.py
def web3_results(request, question_id):
    # Crear instancias de repositorios
    question_repo = DjangoQuestionRepository()
    vote_repo = DjangoVoteRepository()
    
    # Inyectar en use case
    use_case = GetQuestionResultsUseCase(question_repo, vote_repo)
    
    # Ejecutar lógica de negocio
    results = use_case.execute(question_id)
    
    return render(request, 'polls/results_web3.html', {'results': results})
```

### Flujo de Sincronización (Clean Architecture)

```
1. Comando CLI
   ↓
   python manage.py run_reconciliation --from-block=0
   ↓
2. Management Command
   ↓
   Crea instancias: DjangoVoteRepository, DjangoQuestionRepository, 
                    Web3BlockchainGateway
   ↓
3. SyncVotesUseCase.execute(from_block=0)
   ↓
4. Gateway.fetch_vote_events(0) → Lee eventos de blockchain
   ↓
5. Para cada evento:
   ├─ VoteRepository.exists(tx_hash, log_index) → Verifica idempotencia
   ├─ QuestionRepository.get_by_blockchain_id(blockchain_id) → Obtiene pregunta
   └─ VoteRepository.save(vote) → Guarda voto con @transaction.atomic
   ↓
6. Retorna cantidad de votos sincronizados
```

### Testing con Clean Architecture

**Test Unitario de Use Case:**

```python
def test_sync_votes_idempotency():
    # Arrange - Usar repositorios in-memory
    mock_gateway = MockBlockchainGateway()
    question_repo = InMemoryQuestionRepository()
    vote_repo = InMemoryVoteRepository()
    
    question = Question(id=1, blockchain_id=10, ...)
    question_repo.save(question)
    
    mock_gateway.add_mock_vote_event(10, 0, "0xabc", tx_hash="0x123")
    
    use_case = SyncVotesUseCase(vote_repo, question_repo, mock_gateway)
    
    # Act - Ejecutar dos veces
    count1 = use_case.execute(from_block=0)
    count2 = use_case.execute(from_block=0)
    
    # Assert - No duplicar votos
    assert count1 == 1
    assert count2 == 0
    assert len(vote_repo.votes) == 1
```

**Ventajas:**
- ✅ No requiere base de datos
- ✅ No requiere blockchain
- ✅ Test rápido (< 1ms)
- ✅ Fácil de mantener

### Migración Gradual

El proyecto mantiene **compatibilidad con código legacy**:

**Sistema Actual (Legacy):**
- `polls/blockchain/services.py` → `BlockchainVotingService`
- Lógica en modelos y vistas

**Sistema Nuevo (Clean Architecture):**
- `core/` → Dominio y Use Cases
- `polls/adapters/` → Implementaciones

**Estrategia de Migración:**
1. ✅ Nuevas features usan Clean Architecture
2. ⚠️ Código legacy marcado como deprecated
3. 📅 Migración gradual en 2-3 meses
4. ❌ Eliminación final de código deprecated

## Capas del Sistema

### 1. Capa de Presentación
```
Frontend Layer
Admin Panel (Django Admin)
Question Management
Vote Monitoring
Blockchain Dashboard
Public Interface
Question List
Voting Interface
Results Display
Web3 Interface (Future)
Wallet Connection (MetaMask)
```

**Responsabilidades:**
- Renderización de interfaces
- Gestión de sesiones de usuario
- Validación de formularios
- Presentación de resultados

### 2. Capa de Lógica de Negocio
```
Business Logic Layer
Django Apps
polls/ (Core app)
models.py (Question, Choice)
views.py (Voting logic)
admin.py (Admin customization)
polls/blockchain/
models.py (BlockchainQuestion, BlockchainChoice, BlockchainVote)
services.py (BlockchainVotingService)
admin.py (Blockchain admin features)
Management Commands
blockchain_sync (Synchronization utilities)
```

**Responsabilidades:**
- Lógica de votación
- Validación de reglas de negocio
- Gestión de usuarios y permisos
- Sincronización con blockchain

### 3. Capa de Integración Blockchain
```
Integration Layer
BlockchainVotingService
Smart Contract Interface
createQuestion()
vote()
getResults()
hasVoted()
Connection Management
Web3 Provider Setup
Contract ABI Loading
Network Detection
Mock Mode
Simulated Transactions
Fake Blockchain Data
Testing Support
Synchronization Engine
Django -> Blockchain Sync
Blockchain -> Django Sync
Status Tracking
```

**Responsabilidades:**
- Comunicación con smart contracts
- Gestión de transacciones
- Manejo de errores de red
- Modo de desarrollo sin blockchain

### 4. Capa de Datos
```
Data Layer
Django ORM (SQLite/PostgreSQL)
User Management
Question/Choice Storage
Vote Records
Blockchain Sync Status
Blockchain Storage (Ethereum)
Smart Contract State
Vote Records (Immutable)
Transaction History
```

**Responsabilidades:**
- Persistencia de datos
- Consultas y agregaciones
- Backup y recuperación
- Auditoría y logging

### 5. Capa Blockchain
```
Blockchain Layer
Smart Contracts (Solidity)
VotingContract.sol
Question Management
Vote Recording
Duplicate Prevention
Result Calculation
OpenZeppelin Libraries
Ownable (Access control)
ReentrancyGuard (Security)
Ethereum Network
Local (Hardhat Network)
Testnet (Sepolia)
Mainnet (Production)
```

**Responsabilidades:**
- Almacenamiento inmutable de votos
- Prevención de fraude
- Consenso distribuido
- Transparencia pública

## Componentes Principales

### 1. Django Models

#### Question (polls/models.py)
```python
class Question(models.Model):
question_text = models.CharField(max_length=200)
pub_date = models.DateTimeField('date published')
```
- Modelo base tradicional de Django
- Almacenamiento en base de datos relacional
- Usado para encuestas sin requerimiento blockchain

#### BlockchainQuestion (polls/blockchain/models.py)
```python
class BlockchainQuestion(BaseQuestion):
blockchain_id = models.IntegerField(null=True, blank=True)
transaction_hash = models.CharField(max_length=66, null=True, blank=True)
is_synced = models.BooleanField(default=False)
sync_error = models.TextField(null=True, blank=True)
```
- Extiende Question con campos blockchain
- Rastrea estado de sincronización
- Almacena referencias a transacciones

#### BlockchainVote (polls/blockchain/models.py)
```python
class BlockchainVote(models.Model):
question = models.ForeignKey(BlockchainQuestion)
choice = models.ForeignKey(BlockchainChoice)
voter_address = models.CharField(max_length=42)
transaction_hash = models.CharField(max_length=66)
block_number = models.IntegerField()
voted_at = models.DateTimeField(auto_now_add=True)
```
- Registra votos realizados en blockchain
- Almacena datos de transacción
- Permite auditoría y verificación

### 2. BlockchainVotingService

Servicio central de integración blockchain ubicado en `polls/blockchain/services.py`:

```python
class BlockchainVotingService:
def __init__(self, mock_mode=False):
"""Inicializa conexión Web3 o modo mock"""
 
def create_question(self, question_text: str, choices: List[str]) -> Dict:
"""Crea pregunta en smart contract"""
 
def vote(self, question_id: int, choice_index: int, voter_address: str) -> Dict:
"""Registra voto en blockchain"""
 
def get_results(self, question_id: int) -> Dict:
"""Obtiene resultados desde blockchain"""
 
def has_voted(self, question_id: int, address: str) -> bool:
"""Verifica si una dirección ya votó"""
```

**Características:**
- Modo mock para desarrollo sin blockchain
- Manejo automático de errores de conexión
- Generación de transacciones simuladas
- Logging detallado de operaciones

### 3. Smart Contract (VotingContract.sol)

```solidity
contract VotingContract is Ownable, ReentrancyGuard {
struct Question {
string text;
string[] choices;
uint256[] voteCounts;
bool isActive;
uint256 createdAt;
}
 
mapping(uint256 => Question) public questions;
mapping(address => mapping(uint256 => bool)) public hasVoted;
 
function createQuestion(string memory _text, string[] memory _choices) 
public onlyOwner returns (uint256);
 
function vote(uint256 _questionId, uint256 _choiceIndex) 
public nonReentrant;
 
function getResults(uint256 _questionId) 
public view returns (uint256[] memory);
}
```

**Características de Seguridad:**
- **Ownable**: Solo el dueño puede crear preguntas
- **ReentrancyGuard**: Protección contra ataques de reentrada
- **hasVoted**: Previene votos duplicados por dirección
- **isActive**: Control de estado de preguntas

## Flujo de Datos

### Flujo de Creación de Pregunta

```
1. Admin Django -> Crea Question en Admin Panel
|
2. Django Signal/Manual Action -> Llama a BlockchainVotingService
|
3. BlockchainVotingService -> Envía transacción a Smart Contract
|
4. Smart Contract -> Almacena pregunta en blockchain
|
5. Transaction Receipt -> Retorna hash y blockchain_id
|
6. Django -> Actualiza BlockchainQuestion con datos de transacción
|
7. Admin Dashboard -> Muestra estado de sincronización
```

### Flujo de Votación

```
1. Usuario -> Selecciona opción en interface
|
2. Django View -> Valida permisos y datos
|
3. BlockchainVotingService -> Verifica si ya votó (hasVoted)
|
4. Smart Contract -> Registra voto (si no ha votado)
|
5. Transaction -> Genera hash y confirmación
|
6. BlockchainVote -> Crea registro local en Django
|
7. Results Update -> Actualiza contadores locales
|
8. UI -> Muestra resultados actualizados
```

### Flujo de Sincronización

```
Management Command: python manage.py blockchain_sync sync_all
|
1. Busca BlockchainQuestions no sincronizadas
|
2. Para cada pregunta:
|
2.1. Extrae texto y opciones
|
2.2. Llama a BlockchainVotingService.create_question()
|
2.3. Espera confirmación de transacción
|
2.4. Actualiza blockchain_id y transaction_hash
|
2.5. Marca is_synced = True
|
3. Genera reporte de sincronización
```

## Modelos de Datos

### Diagrama ER (Entity-Relationship)

```

Question 

id (PK) 
question_text 
pub_date 

^
(Herencia)
 

BlockchainQuestion 

question_ptr (PK, FK) 
blockchain_id 
transaction_hash 
is_synced 
sync_error 
last_sync_attempt 

 
(1:N)
|

BlockchainChoice 

id (PK) 
question (FK) 
choice_text 
blockchain_index 

 
(1:N)
|

BlockchainVote 

id (PK) 
question (FK) 
choice (FK) 
voter_address 
transaction_hash 
block_number 
voted_at 

```

### Schema de Smart Contract

```
VotingContract State:

questions: mapping(uint256 => Question)
Question {
text: string
choices: string[]
voteCounts: uint256[]
isActive: bool
createdAt: uint256
}

hasVoted: mapping(address => mapping(uint256 => bool))
Tracks: "has address X voted on question Y?"

questionCount: uint256
Total number of questions created

owner: address
Contract owner address (from Ownable)
```

## Decisiones Arquitectónicas

### 1. ¿Por qué Arquitectura Híbrida?

**Decisión**: Mantener Django + agregar Blockchain

**Razones**:
- Aprovecha código existente de Django
- Panel de administración robusto y maduro
- Flexibilidad para datos que no requieren blockchain
- Mejor UX (no todo requiere wallet)
- Costos de gas reducidos (solo votos críticos en blockchain)

**Alternativas Consideradas**:
- DApp 100% en blockchain: Caro, lento, UX complicada
- Solo Django: Sin transparencia ni inmutabilidad
- **Híbrido seleccionado**: Balance óptimo

### 2. ¿Por qué Web3.py y no Web3.js?

**Decisión**: Usar Web3.py para integración backend

**Razones**:
- Código Python (coherente con Django)
- Ejecución server-side (más seguro)
- No requiere wallet del usuario para todas las operaciones
- Mejor para automatización y scripts

**Nota**: Web3.js se usará en frontend para wallet connection (futuro)

### 3. ¿Por qué Modo Mock?

**Decisión**: Implementar mock mode completo

**Razones**:
- Desarrollo sin dependencia de blockchain
- Testing más rápido y económico
- Onboarding más fácil para nuevos desarrolladores
- CI/CD sin necesidad de nodos blockchain

**Implementación**:
```python
if self.mock_mode or not self._check_connection():
return self._mock_create_question(question_text, choices)
```

### 4. ¿Por qué OpenZeppelin?

**Decisión**: Usar OpenZeppelin para contratos base

**Razones**:
- Contratos auditados profesionalmente
- Estándar de la industria
- Actualizaciones de seguridad regulares
- Documentación excelente
- Reduce superficie de ataque

### 5. ¿Por qué Hardhat sobre Truffle?

**Decisión**: Usar Hardhat como framework de desarrollo

**Razones**:
- Más moderno y activamente mantenido
- Mejor soporte TypeScript
- Hardhat Network superior para testing
- Plugins y extensibilidad
- Mejor debugging

## Patrones de Diseño Utilizados

### 1. Service Layer Pattern
- `BlockchainVotingService` encapsula toda lógica blockchain
- Separación clara de responsabilidades
- Facilita testing y mocking

### 2. Adapter Pattern
- Web3.py actúa como adapter entre Django y Ethereum
- Abstrae complejidad de blockchain
- Permite cambiar implementación sin afectar Django

### 3. Proxy Pattern
- Django models actúan como proxy de datos blockchain
- Cacheo local de datos inmutables
- Mejora performance de lecturas

### 4. Strategy Pattern
- Mock mode vs Real mode
- Misma interfaz, diferente implementación
- Selección en runtime vía configuración

## Escalabilidad y Performance

### Consideraciones de Escalabilidad

1. **Database Sharding**: Preparado para separar datos por rango de fechas
2. **Read Replicas**: Django soporta múltiples bases de datos
3. **Caching**: Redis puede agregarse fácilmente
4. **Async Operations**: Django 4.2+ soporta views asíncronas
5. **Blockchain Sharding**: Posible migrar a L2 solutions (Polygon, Optimism)

### Optimizaciones Implementadas

- **Batch Operations**: `blockchain_sync sync_all` procesa en lote
- **Lazy Loading**: Datos blockchain solo se cargan cuando se necesitan
- **Index Optimization**: Índices en blockchain_id, transaction_hash
- **Query Optimization**: `select_related()` y `prefetch_related()`

## Seguridad

### Capas de Seguridad

1. **Django Layer**:
- CSRF protection
- SQL injection prevention (ORM)
- XSS protection (template escaping)
- Admin authentication

2. **Smart Contract Layer**:
- Ownable: Access control
- ReentrancyGuard: Prevent reentrancy attacks
- Input validation
- State consistency checks

3. **Integration Layer**:
- Environment variables para claves privadas
- Validación de transacciones
- Error handling robusto
- Logging de operaciones sensibles

### Consideraciones de Seguridad

- **Claves Privadas**: Nunca commitear en git
- **Gas Limits**: Configurar límites apropiados
- **Rate Limiting**: Implementar para prevenir spam
- **Auditoría**: Recomendada antes de producción

## Monitoreo y Observabilidad

### Métricas Clave

1. **Django Metrics**:
- Request/response times
- Database query performance
- Error rates

2. **Blockchain Metrics**:
- Transaction success rate
- Gas costs
- Sync status
- Contract calls per minute

3. **Integration Metrics**:
- Sync latency
- Failed transactions
- Mock mode usage

### Dashboard de Admin

- **URL**: `/admin/polls/blockchainquestion/blockchain-dashboard/`
- **Features**:
- Connection status
- Sync statistics
- Recent transactions
- Error logs

## Referencias

- [Django Documentation](https://docs.djangoproject.com/)
- [Web3.py Documentation](https://web3py.readthedocs.io/)
- [Solidity Documentation](https://docs.soliditylang.org/)
- [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts/)
- [Hardhat Documentation](https://hardhat.org/docs)

---

**Última Actualización**: Diciembre 2025 
**Versión**: 1.0 
**Autor**: @Jorgez-tech
