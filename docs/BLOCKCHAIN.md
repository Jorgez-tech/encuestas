# Integración Blockchain - Documentación Técnica

Este documento describe en detalle la integración blockchain del sistema de votación con Django, incluyendo aspectos técnicos, decisiones de diseño y guías de uso avanzado.

## Tabla de Contenidos

- [Visión General](#visión-general)
- [Smart Contract](#smart-contract)
- [Servicio de Integración](#servicio-de-integración)
- [Modelos de Datos](#modelos-de-datos)
- [Comandos de Gestión](#comandos-de-gestión)
- [Admin Interface](#admin-interface)
- [Modo Mock](#modo-mock)
- [Seguridad](#seguridad)
- [Gas y Costos](#gas-y-costos)
- [Testing](#testing)

## Visión General

### ¿Qué hace la integración blockchain?

La integración blockchain añade una capa de transparencia e inmutabilidad a las votaciones:

1. **Transparencia**: Todos los votos son públicamente verificables en blockchain
2. **Inmutabilidad**: Los votos no pueden ser alterados una vez registrados
3. **Descentralización**: No dependemos de un servidor central para validar votos
4. **Prevención de fraude**: Una wallet solo puede votar una vez por pregunta

### Arquitectura de la Integración

```
Django Backend ←→ Web3.py ←→ Ethereum Network
     ↓                             ↓
  Database                   Smart Contract
  (Local Cache)              (Source of Truth)
```

## Smart Contract

### VotingContract.sol

Ubicación: `blockchain/contracts/VotingContract.sol`

#### Estructura Principal

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

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
    uint256 public questionCount;
    
    event QuestionCreated(uint256 indexed questionId, string text, uint256 choiceCount);
    event VoteCast(uint256 indexed questionId, uint256 choiceIndex, address voter);
    event QuestionStatusChanged(uint256 indexed questionId, bool isActive);
}
```

#### Funciones Principales

##### 1. createQuestion

```solidity
function createQuestion(
    string memory _text, 
    string[] memory _choices
) public onlyOwner returns (uint256)
```

**Descripción**: Crea una nueva pregunta en el smart contract.

**Parámetros**:
- `_text`: Texto de la pregunta
- `_choices`: Array de opciones de respuesta

**Retorna**: ID de la pregunta creada

**Restricciones**:
- Solo el owner puede llamar esta función
- Debe tener al menos 2 opciones
- Texto no puede estar vacío

**Eventos emitidos**:
- `QuestionCreated(questionId, text, choiceCount)`

**Ejemplo de uso**:
```javascript
const tx = await contract.createQuestion(
    "¿Cuál es tu color favorito?",
    ["Rojo", "Azul", "Verde"]
);
```

##### 2. vote

```solidity
function vote(
    uint256 _questionId, 
    uint256 _choiceIndex
) public nonReentrant
```

**Descripción**: Registra un voto para una pregunta específica.

**Parámetros**:
- `_questionId`: ID de la pregunta
- `_choiceIndex`: Índice de la opción elegida (0-based)

**Restricciones**:
- La pregunta debe existir
- La pregunta debe estar activa (`isActive = true`)
- La dirección no debe haber votado antes
- El índice debe ser válido

**Eventos emitidos**:
- `VoteCast(questionId, choiceIndex, msg.sender)`

**Protección**: `nonReentrant` previene ataques de reentrada

**Ejemplo de uso**:
```javascript
const tx = await contract.vote(1, 0); // Votar por la primera opción
```

##### 3. getResults

```solidity
function getResults(
    uint256 _questionId
) public view returns (uint256[] memory)
```

**Descripción**: Obtiene los resultados de una pregunta.

**Parámetros**:
- `_questionId`: ID de la pregunta

**Retorna**: Array de uint256 con los votos por cada opción

**Restricciones**: Ninguna (función view)

**Ejemplo de uso**:
```javascript
const results = await contract.getResults(1);
console.log(results); // [5, 3, 7] - votos por opción
```

##### 4. getQuestion

```solidity
function getQuestion(
    uint256 _questionId
) public view returns (
    string memory text,
    string[] memory choices,
    uint256[] memory voteCounts,
    bool isActive,
    uint256 createdAt
)
```

**Descripción**: Obtiene toda la información de una pregunta.

**Ejemplo de uso**:
```javascript
const [text, choices, votes, active, timestamp] = await contract.getQuestion(1);
```

##### 5. setQuestionActive

```solidity
function setQuestionActive(
    uint256 _questionId, 
    bool _isActive
) public onlyOwner
```

**Descripción**: Activa o desactiva una pregunta.

**Restricciones**: Solo el owner puede llamarla

**Eventos emitidos**:
- `QuestionStatusChanged(questionId, isActive)`

#### Eventos del Contrato

```solidity
event QuestionCreated(
    uint256 indexed questionId, 
    string text, 
    uint256 choiceCount
);

event VoteCast(
    uint256 indexed questionId, 
    uint256 choiceIndex, 
    address voter
);

event QuestionStatusChanged(
    uint256 indexed questionId, 
    bool isActive
);
```

**Uso de eventos**:
- Permiten escuchar cambios en tiempo real
- Facilitan la sincronización Django ↔ Blockchain
- Reducen necesidad de polling

### Seguridad del Smart Contract

#### 1. OpenZeppelin Ownable

```solidity
import "@openzeppelin/contracts/access/Ownable.sol";
```

**Propósito**: Control de acceso

**Funcionalidad**:
- Solo el owner puede crear preguntas
- Owner puede transferir ownership
- Protege funciones administrativas

**Uso**:
```solidity
function createQuestion(...) public onlyOwner { }
```

#### 2. OpenZeppelin ReentrancyGuard

```solidity
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
```

**Propósito**: Prevenir ataques de reentrada

**Funcionalidad**:
- Bloquea la función durante su ejecución
- Previene llamadas recursivas maliciosas

**Uso**:
```solidity
function vote(...) public nonReentrant { }
```

#### 3. Prevención de Votos Duplicados

```solidity
mapping(address => mapping(uint256 => bool)) public hasVoted;

function vote(uint256 _questionId, uint256 _choiceIndex) public {
    require(!hasVoted[msg.sender][_questionId], "Ya votaste");
    hasVoted[msg.sender][_questionId] = true;
    // ... registrar voto
}
```

**Garantía**: Una dirección solo puede votar una vez por pregunta

#### 4. Validaciones de Input

```solidity
require(_questionId < questionCount, "Pregunta no existe");
require(questions[_questionId].isActive, "Pregunta inactiva");
require(_choiceIndex < questions[_questionId].choices.length, "Opcion invalida");
```

## Servicio de Integración

### BlockchainVotingService

Ubicación: `polls/blockchain/services.py`

#### Inicialización

```python
from polls.blockchain.services import BlockchainVotingService

# Modo real (requiere blockchain activo)
service = BlockchainVotingService(mock_mode=False)

# Modo mock (simulación)
service = BlockchainVotingService(mock_mode=True)
```

#### Métodos Principales

##### create_question()

```python
def create_question(
    self, 
    question_text: str, 
    choices: List[str]
) -> Dict[str, Any]:
    """
    Crea una pregunta en blockchain.
    
    Returns:
        {
            'success': True,
            'transaction_hash': '0x...',
            'blockchain_id': 1,
            'gas_used': 250000
        }
    """
```

**Uso**:
```python
result = service.create_question(
    "¿Cuál es tu framework favorito?",
    ["Django", "Flask", "FastAPI"]
)

if result['success']:
    print(f"Pregunta creada con ID: {result['blockchain_id']}")
    print(f"TX Hash: {result['transaction_hash']}")
```

##### vote()

```python
def vote(
    self,
    question_id: int,
    choice_index: int,
    voter_address: str
) -> Dict[str, Any]:
    """
    Registra un voto en blockchain.
    
    Returns:
        {
            'success': True,
            'transaction_hash': '0x...',
            'block_number': 12345,
            'gas_used': 100000
        }
    """
```

**Uso**:
```python
result = service.vote(
    question_id=1,
    choice_index=0,
    voter_address="0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
)

if result['success']:
    print(f"Voto registrado en bloque: {result['block_number']}")
```

##### get_results()

```python
def get_results(self, question_id: int) -> Dict[str, Any]:
    """
    Obtiene resultados desde blockchain.
    
    Returns:
        {
            'success': True,
            'results': [5, 3, 7],  # Votos por opción
            'total_votes': 15
        }
    """
```

##### has_voted()

```python
def has_voted(self, question_id: int, address: str) -> bool:
    """
    Verifica si una dirección ya votó.
    
    Returns:
        True si ya votó, False si no
    """
```

**Uso**:
```python
if service.has_voted(1, "0xf39..."):
    print("Ya votaste en esta pregunta")
else:
    print("Puedes votar")
```

#### Manejo de Errores

El servicio captura y maneja varios tipos de errores:

```python
try:
    result = service.vote(question_id, choice_index, voter_address)
    if not result['success']:
        error = result.get('error', 'Unknown error')
        print(f"Error: {error}")
except Exception as e:
    logger.error(f"Exception: {e}")
```

**Errores comunes**:
- `Connection refused`: Blockchain no está corriendo
- `Already voted`: La dirección ya votó
- `Question not found`: ID inválido
- `Gas too low`: Gas insuficiente para la transacción

## Modelos de Datos

### BlockchainQuestion

```python
class BlockchainQuestion(BaseQuestion):
    blockchain_id = models.IntegerField(null=True, blank=True)
    transaction_hash = models.CharField(max_length=66, null=True, blank=True)
    block_number = models.IntegerField(null=True, blank=True)
    is_synced = models.BooleanField(default=False)
    sync_error = models.TextField(null=True, blank=True)
    last_sync_attempt = models.DateTimeField(null=True, blank=True)
```

**Campos**:
- `blockchain_id`: ID en el smart contract
- `transaction_hash`: Hash de la transacción de creación
- `block_number`: Número de bloque donde se registró
- `is_synced`: ¿Está sincronizado con blockchain?
- `sync_error`: Mensaje de error si falló la sincronización
- `last_sync_attempt`: Última vez que se intentó sincronizar

**Métodos útiles**:
```python
question = BlockchainQuestion.objects.get(id=1)

# Sincronizar con blockchain
question.sync_to_blockchain()

# Verificar si está sincronizado
if question.is_synced:
    print(f"Blockchain ID: {question.blockchain_id}")
```

### BlockchainVote

```python
class BlockchainVote(models.Model):
    question = models.ForeignKey(BlockchainQuestion, on_delete=models.CASCADE)
    choice = models.ForeignKey(BlockchainChoice, on_delete=models.CASCADE)
    voter_address = models.CharField(max_length=42)
    transaction_hash = models.CharField(max_length=66, unique=True)
    block_number = models.IntegerField()
    voted_at = models.DateTimeField(auto_now_add=True)
```

**Propósito**: Cacheo local de votos blockchain

**Uso**:
```python
# Registrar voto local
BlockchainVote.objects.create(
    question=question,
    choice=choice,
    voter_address="0xf39...",
    transaction_hash="0x123...",
    block_number=12345
)

# Consultar votos
votes = BlockchainVote.objects.filter(question=question)
```

## Comandos de Gestión

### blockchain_sync

Ubicación: `polls/management/commands/blockchain_sync.py`

#### Subcomandos Disponibles

##### status

```bash
python manage.py blockchain_sync status
```

**Descripción**: Muestra el estado de la conexión blockchain

**Salida**:
```
🔗 Blockchain Integration Status
================================

Connection Status: ✅ CONNECTED
Network: Hardhat Local Network
Chain ID: 31337
Contract Address: 0x5FbDB2315678afecb367f032d93F642f64180aa3
Block Number: 12345

Database Statistics:
- Total Questions: 13
- Blockchain Questions: 10
- Synced Questions: 5
- Pending Sync: 5
- Blockchain Votes: 25
```

##### sync_all

```bash
python manage.py blockchain_sync sync_all [--force] [--verbose]
```

**Descripción**: Sincroniza todas las preguntas pendientes con blockchain

**Opciones**:
- `--force`: Re-sincroniza incluso preguntas ya sincronizadas
- `--verbose`: Muestra información detallada

**Ejemplo**:
```bash
python manage.py blockchain_sync sync_all --force --verbose
```

**Salida**:
```
🔄 Starting blockchain synchronization...

[1/5] Syncing Question #1: "¿Tu color favorito?"
  ✅ Success - TX: 0x123... | Blockchain ID: 1

[2/5] Syncing Question #2: "¿Tu comida favorita?"
  ✅ Success - TX: 0x456... | Blockchain ID: 2

...

✅ Synchronization complete!
- Successful: 5
- Failed: 0
- Skipped: 5 (already synced)
```

##### sync_question

```bash
python manage.py blockchain_sync sync_question --question-id <ID>
```

**Descripción**: Sincroniza una pregunta específica

**Ejemplo**:
```bash
python manage.py blockchain_sync sync_question --question-id 5
```

##### deploy_check

```bash
python manage.py blockchain_sync deploy_check
```

**Descripción**: Verifica que el smart contract esté desplegado y funcionando

**Salida**:
```
✅ Smart contract is deployed and accessible
Contract address: 0x5FbDB2315678afecb367f032d93F642f64180aa3
Question count: 5
```

##### reset_sync

```bash
python manage.py blockchain_sync reset_sync [--question-id <ID>]
```

**Descripción**: Resetea el estado de sincronización

**Opciones**:
- Sin opciones: Resetea todas las preguntas
- `--question-id`: Resetea solo una pregunta específica

**Uso**:
```bash
# Resetear todas
python manage.py blockchain_sync reset_sync

# Resetear una específica
python manage.py blockchain_sync reset_sync --question-id 5
```

## Admin Interface

### Dashboard Blockchain

**URL**: `/admin/polls/blockchainquestion/blockchain-dashboard/`

#### Secciones del Dashboard

1. **Connection Status**
   - Estado de conexión (Connected/Mock/Disconnected)
   - Información de red
   - Dirección del contrato
   - Número de bloque actual

2. **Statistics**
   - Total de preguntas
   - Preguntas sincronizadas
   - Votos en blockchain
   - Gas utilizado total

3. **Recent Activity**
   - Últimas sincronizaciones
   - Últimos votos registrados
   - Errores recientes

4. **Quick Actions**
   - Botones para sincronizar
   - Ver estado detallado
   - Resetear sincronización

#### Admin de BlockchainQuestion

**Características**:
- Lista con estado de sincronización (🔗, ⏳, 💾)
- Acciones bulk: "Sync selected to blockchain"
- Filtros por estado de sincronización
- Búsqueda por texto y blockchain_id

**Campos mostrados**:
- Question text
- Pub date
- Blockchain ID
- Transaction hash (acortado)
- Sync status

#### Admin de BlockchainVote

**Características**:
- Lista de votos blockchain
- Filtros por pregunta, fecha
- Búsqueda por dirección de voter
- Links a transaction hashes

## Modo Mock

### ¿Qué es el Modo Mock?

El modo mock simula operaciones blockchain sin necesidad de conexión real. Útil para:
- Desarrollo sin blockchain
- Testing rápido
- CI/CD pipelines
- Onboarding de nuevos desarrolladores

### Activar Modo Mock

**Opción 1: Variable de entorno**
```bash
# .env
BLOCKCHAIN_MOCK_MODE=True
```

**Opción 2: Configuración Django**
```python
# settings.py
BLOCKCHAIN_CONFIG = {
    'MOCK_MODE': True,
}
```

**Opción 3: Programáticamente**
```python
service = BlockchainVotingService(mock_mode=True)
```

### Comportamiento en Modo Mock

```python
# Modo Mock simula:
- ✅ Transaction hashes (0xmock...)
- ✅ Blockchain IDs (incrementales)
- ✅ Block numbers (simulados)
- ✅ Gas usado (valores realistas)
- ✅ Delays de transacción (simulados)
- ✅ Errores aleatorios (testing)
```

### Detectar Modo Mock

```python
from polls.blockchain.services import BlockchainVotingService

service = BlockchainVotingService()

if service.mock_mode:
    print("⚠️  Running in MOCK mode - blockchain not required")
else:
    print("🔗 Connected to real blockchain")
```

## Seguridad

### Mejores Prácticas

#### 1. Claves Privadas

❌ **NUNCA hacer esto**:
```python
# settings.py - MAL
PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
```

✅ **Hacer esto**:
```python
# .env
BLOCKCHAIN_PRIVATE_KEY=0xac0974...

# settings.py
import os
from dotenv import load_dotenv

load_dotenv()
PRIVATE_KEY = os.getenv('BLOCKCHAIN_PRIVATE_KEY')
```

#### 2. Validación de Direcciones

```python
from web3 import Web3

def is_valid_address(address: str) -> bool:
    return Web3.is_address(address)

# Usar antes de votar
if not is_valid_address(voter_address):
    raise ValueError("Invalid Ethereum address")
```

#### 3. Rate Limiting

Implementar rate limiting para prevenir spam:

```python
# views.py
from django.views.decorators.cache import cache_page

@cache_page(60)  # Cache por 1 minuto
def vote_view(request):
    # ... lógica de votación
```

#### 4. Gas Limits

Configurar límites de gas apropiados:

```python
BLOCKCHAIN_CONFIG = {
    'GAS_LIMIT': 500000,  # Límite máximo
    'GAS_PRICE_GWEI': 20,  # Precio en Gwei
}
```

### Auditoría de Smart Contracts

⚠️ **Importante**: Antes de desplegar en mainnet:

1. **Auditoría profesional** de smart contracts
2. **Testing exhaustivo** en testnet
3. **Bug bounty program** (opcional)
4. **Insurance** (e.g., Nexus Mutual)

**Herramientas de auditoría**:
- Slither (análisis estático)
- Mythril (análisis simbólico)
- Echidna (fuzzing)

```bash
# Instalar Slither
pip install slither-analyzer

# Analizar contrato
slither blockchain/contracts/VotingContract.sol
```

## Gas y Costos

### Estimación de Gas

#### createQuestion
- **Gas estimado**: ~200,000 - 300,000
- **Costo (20 Gwei)**: ~$0.10 - $0.15 USD (depende del precio de ETH)

#### vote
- **Gas estimado**: ~50,000 - 80,000
- **Costo (20 Gwei)**: ~$0.03 - $0.05 USD

### Optimizaciones de Gas

1. **Batch Operations**: Crear múltiples preguntas en una transacción
2. **Efficient Storage**: Usar tipos de datos más pequeños cuando sea posible
3. **Event Logs**: Usar eventos en lugar de storage cuando sea apropiado

### Monitoreo de Costos

```python
# Registrar gas usado
from polls.blockchain.models import GasUsageLog

GasUsageLog.objects.create(
    operation='create_question',
    gas_used=250000,
    gas_price=20,
    total_cost_eth=0.005
)

# Analizar costos
total_spent = GasUsageLog.objects.aggregate(
    total=Sum('total_cost_eth')
)['total']
```

## Testing

### Tests de Smart Contract

Ubicación: `blockchain/test/`

```bash
# Ejecutar tests de Hardhat
cd blockchain
npx hardhat test
```

### Tests de Integración Django

```bash
# Tests de modelos blockchain
python manage.py test polls.blockchain.tests.test_models

# Tests de servicios
python manage.py test polls.blockchain.tests.test_services

# Tests de admin
python manage.py test polls.blockchain.tests.test_admin
```

### Test Manual de Integración

```python
# test_integration.py
from polls.blockchain.services import BlockchainVotingService
from polls.blockchain.models import BlockchainQuestion

# 1. Crear servicio
service = BlockchainVotingService(mock_mode=True)

# 2. Crear pregunta
result = service.create_question(
    "Test Question",
    ["Option A", "Option B"]
)

assert result['success'] == True

# 3. Votar
vote_result = service.vote(
    result['blockchain_id'],
    0,
    "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
)

assert vote_result['success'] == True

# 4. Verificar resultados
results = service.get_results(result['blockchain_id'])
assert results['results'][0] == 1
```

## Recursos Adicionales

- [Web3.py Documentation](https://web3py.readthedocs.io/)
- [Solidity Documentation](https://docs.soliditylang.org/)
- [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts/)
- [Ethereum Gas Tracker](https://etherscan.io/gastracker)
- [Hardhat Documentation](https://hardhat.org/docs)

---

**Última Actualización**: Diciembre 2024  
**Autor**: @Jorgez-tech
