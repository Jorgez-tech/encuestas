# Guía de Desarrollo

Esta guía está dirigida a desarrolladores que desean contribuir al proyecto o extender sus funcionalidades.

## Tabla de Contenidos

- [Configuración del Entorno de Desarrollo](#configuración-del-entorno-de-desarrollo)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Flujo de Trabajo](#flujo-de-trabajo)
- [Estándares de Código](#estándares-de-código)
- [Testing](#testing)
- [Debugging](#debugging)
- [Contribuir](#contribuir)

## Configuración del Entorno de Desarrollo

### 1. Fork y Clone

```bash
# Fork el repositorio en GitHub
# Luego clona tu fork
git clone https://github.com/TU-USUARIO/encuestas.git
cd encuestas

# Agrega el repositorio original como upstream
git remote add upstream https://github.com/Jorgez-tech/encuestas.git
```

### 2. Configurar Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Instalar dependencias de desarrollo
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Si existe
```

### 3. Instalar Pre-commit Hooks (Recomendado)

```bash
pip install pre-commit
pre-commit install
```

### 4. Configurar Variables de Entorno

```bash
# Crear archivo .env
cp .env.example .env  # Si existe template

# Editar .env con tus valores
nano .env
```

**Ejemplo .env**:
```env
DEBUG=True
SECRET_KEY=tu-secret-key-de-desarrollo
BLOCKCHAIN_MOCK_MODE=True
WEB3_PROVIDER_URL=http://127.0.0.1:8545
```

### 5. Inicializar Base de Datos

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata initial_data  # Si existe
```

## Estructura del Proyecto

```
encuestas/
├── blockchain/                 # Smart contracts y config Hardhat
│   ├── contracts/             # Contratos Solidity
│   │   └── VotingContract.sol
│   ├── ignition/              # Módulos de deployment
│   ├── scripts/               # Scripts de deployment
│   ├── test/                  # Tests de contratos
│   └── hardhat.config.ts      # Configuración Hardhat
│
├── encuestas/                 # Configuración Django
│   ├── settings.py           # Settings principales
│   ├── urls.py               # URLs principales
│   ├── wsgi.py               # WSGI config
│   └── asgi.py               # ASGI config
│
├── polls/                     # App principal de votaciones
│   ├── blockchain/           # Integración blockchain
│   │   ├── models.py         # Modelos blockchain-aware
│   │   ├── services.py       # BlockchainVotingService
│   │   ├── admin.py          # Admin customizado
│   │   └── management/       # Comandos de gestión
│   │       └── commands/
│   │           └── blockchain_sync.py
│   ├── migrations/           # Migraciones de DB
│   ├── static/               # CSS, JS, imágenes
│   ├── templates/            # Templates HTML
│   ├── models.py             # Modelos Django tradicionales
│   ├── views.py              # Views
│   ├── admin.py              # Admin básico
│   ├── urls.py               # URLs de la app
│   └── tests.py              # Tests
│
├── static/                    # Static files globales
├── docs/                      # Documentación
│   ├── ARCHITECTURE.md
│   ├── INSTALLATION.md
│   ├── BLOCKCHAIN.md
│   ├── DEVELOPMENT.md
│   └── DEPLOYMENT.md
│
├── manage.py                  # Django management script
├── requirements.txt           # Dependencias Python
├── .env                       # Variables de entorno (no commitear)
├── .gitignore
└── README.md
```

## Flujo de Trabajo

### Branching Strategy

Seguimos Git Flow:

```
main                    # Producción estable
  └── develop          # Desarrollo principal
      ├── feature/*    # Nuevas características
      ├── bugfix/*     # Corrección de bugs
      └── hotfix/*     # Fixes urgentes para producción
```

### Crear una Nueva Feature

```bash
# Actualizar develop
git checkout develop
git pull upstream develop

# Crear branch de feature
git checkout -b feature/nombre-descriptivo

# Hacer cambios y commits
git add .
git commit -m "feat: descripción del cambio"

# Push a tu fork
git push origin feature/nombre-descriptivo

# Crear Pull Request en GitHub
```

### Commits Convencionales

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Formato
<tipo>(<scope>): <descripción>

[cuerpo opcional]

[footer opcional]
```

**Tipos**:
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Cambios de formato (no afectan código)
- `refactor`: Refactorización de código
- `test`: Agregar o modificar tests
- `chore`: Tareas de mantenimiento

**Ejemplos**:
```bash
feat(blockchain): add vote verification endpoint
fix(admin): correct sync status display
docs(readme): update installation instructions
test(polls): add tests for vote model
```

## Estándares de Código

### Python (Django)

Seguimos [PEP 8](https://pep8.org/) con algunas excepciones:

**1. Formato**:
```python
# Usar 4 espacios para indentación
# Líneas de máximo 100 caracteres (no 79)
# Imports organizados: stdlib, third-party, local
```

**2. Naming Conventions**:
```python
# Variables y funciones: snake_case
def calculate_total_votes(question_id):
    total_votes = 0
    return total_votes

# Clases: PascalCase
class BlockchainQuestion(models.Model):
    pass

# Constantes: UPPER_SNAKE_CASE
MAX_CHOICES_PER_QUESTION = 10
```

**3. Docstrings**:
```python
def create_question(question_text: str, choices: List[str]) -> Dict:
    """
    Crea una pregunta en blockchain.
    
    Args:
        question_text: Texto de la pregunta
        choices: Lista de opciones de respuesta
        
    Returns:
        Dict con resultado de la operación:
        - success (bool): Si la operación fue exitosa
        - transaction_hash (str): Hash de la transacción
        - blockchain_id (int): ID en blockchain
        
    Raises:
        ValueError: Si question_text está vacío
        ConnectionError: Si no hay conexión blockchain
    """
    pass
```

**4. Type Hints**:
```python
from typing import List, Dict, Optional, Union

def get_results(question_id: int) -> Optional[Dict[str, Union[int, str]]]:
    return {'total_votes': 10, 'status': 'active'}
```

### JavaScript/TypeScript (Smart Contracts)

**1. Solidity Style Guide**:
```solidity
// Seguir: https://docs.soliditylang.org/en/latest/style-guide.html

// Order: SPDX, pragma, imports, contract
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import "@openzeppelin/contracts/access/Ownable.sol";

contract VotingContract is Ownable {
    // Order: state variables, events, modifiers, constructor, functions
    
    // State variables
    uint256 public questionCount;
    
    // Events
    event QuestionCreated(uint256 indexed questionId);
    
    // Constructor
    constructor(address initialOwner) Ownable(initialOwner) {}
    
    // Functions: external, public, internal, private
}
```

**2. TypeScript (Hardhat)**:
```typescript
// Use camelCase for variables and functions
const deployedContract = await ethers.deployContract("VotingContract");

// Use PascalCase for types and interfaces
interface QuestionData {
  text: string;
  choices: string[];
}
```

### Herramientas de Linting

**Python**:
```bash
# Instalar
pip install flake8 black isort mypy

# Ejecutar
flake8 polls/
black polls/
isort polls/
mypy polls/
```

**Configuración en `setup.cfg`**:
```ini
[flake8]
max-line-length = 100
exclude = migrations,__pycache__,venv

[isort]
profile = black
line_length = 100

[mypy]
ignore_missing_imports = True
```

**Solidity**:
```bash
# Instalar
npm install --save-dev prettier prettier-plugin-solidity

# Ejecutar
npx prettier --write 'contracts/**/*.sol'
```

## Testing

### Tests de Django

**Estructura**:
```
polls/
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_admin.py
│   └── test_blockchain_integration.py
```

**Ejemplo de Test**:
```python
from django.test import TestCase
from polls.models import Question
from polls.blockchain.models import BlockchainQuestion

class BlockchainQuestionTestCase(TestCase):
    def setUp(self):
        """Se ejecuta antes de cada test"""
        self.question = BlockchainQuestion.objects.create(
            question_text="Test Question",
            pub_date=timezone.now()
        )
    
    def test_question_creation(self):
        """Test que verifica creación de pregunta"""
        self.assertEqual(self.question.question_text, "Test Question")
        self.assertFalse(self.question.is_synced)
    
    def test_sync_to_blockchain_mock(self):
        """Test de sincronización en modo mock"""
        result = self.question.sync_to_blockchain(mock=True)
        self.assertTrue(result['success'])
        
        # Refrescar desde DB
        self.question.refresh_from_db()
        self.assertTrue(self.question.is_synced)
        self.assertIsNotNone(self.question.blockchain_id)
    
    def tearDown(self):
        """Se ejecuta después de cada test"""
        self.question.delete()
```

**Ejecutar Tests**:
```bash
# Todos los tests
python manage.py test

# Tests de una app
python manage.py test polls

# Tests de un archivo específico
python manage.py test polls.tests.test_models

# Test específico
python manage.py test polls.tests.test_models.BlockchainQuestionTestCase.test_question_creation

# Con verbosidad
python manage.py test --verbosity=2

# Con coverage
coverage run --source='polls' manage.py test
coverage report
coverage html  # Genera reporte HTML
```

### Tests de Smart Contracts

**Ubicación**: `blockchain/test/`

**Ejemplo**:
```typescript
import { expect } from "chai";
import { ethers } from "hardhat";

describe("VotingContract", function () {
  it("Should create a question", async function () {
    const VotingContract = await ethers.getContractFactory("VotingContract");
    const contract = await VotingContract.deploy();
    
    const tx = await contract.createQuestion(
      "Test Question",
      ["Option 1", "Option 2"]
    );
    
    await tx.wait();
    
    const questionCount = await contract.questionCount();
    expect(questionCount).to.equal(1);
  });
  
  it("Should allow voting", async function () {
    // ... test implementation
  });
  
  it("Should prevent double voting", async function () {
    // ... test implementation
  });
});
```

**Ejecutar Tests de Hardhat**:
```bash
cd blockchain

# Todos los tests
npx hardhat test

# Test específico
npx hardhat test test/VotingContract.test.ts

# Con gas reporting
REPORT_GAS=true npx hardhat test

# Con coverage
npx hardhat coverage
```

### Integration Tests

```python
# test_integration.py
from django.test import TransactionTestCase
from polls.blockchain.services import BlockchainVotingService
from polls.blockchain.models import BlockchainQuestion

class BlockchainIntegrationTest(TransactionTestCase):
    def setUp(self):
        # Usar modo mock para tests
        self.service = BlockchainVotingService(mock_mode=True)
    
    def test_full_voting_flow(self):
        """Test del flujo completo: crear pregunta -> votar -> obtener resultados"""
        # 1. Crear pregunta
        result = self.service.create_question(
            "Integration Test",
            ["A", "B", "C"]
        )
        self.assertTrue(result['success'])
        
        blockchain_id = result['blockchain_id']
        
        # 2. Votar
        vote_result = self.service.vote(
            blockchain_id, 
            0, 
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertTrue(vote_result['success'])
        
        # 3. Verificar que ya votó
        has_voted = self.service.has_voted(
            blockchain_id,
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertTrue(has_voted)
        
        # 4. Obtener resultados
        results = self.service.get_results(blockchain_id)
        self.assertEqual(results['results'][0], 1)
```

## Debugging

### Debug Django

**1. Django Debug Toolbar**:
```bash
pip install django-debug-toolbar

# settings.py
INSTALLED_APPS = [
    # ...
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # ...
]

INTERNAL_IPS = ['127.0.0.1']
```

**2. Python Debugger (pdb)**:
```python
# Agregar breakpoint en código
import pdb; pdb.set_trace()

# O en Python 3.7+
breakpoint()

# Comandos útiles:
# n (next) - siguiente línea
# s (step) - entrar en función
# c (continue) - continuar ejecución
# l (list) - mostrar código
# p variable - imprimir variable
# q (quit) - salir
```

**3. VS Code Launch Configuration**:
```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Django",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/manage.py",
            "args": ["runserver", "8000"],
            "django": true
        }
    ]
}
```

### Debug Smart Contracts

**1. Console.log en Solidity**:
```solidity
import "hardhat/console.sol";

function vote(uint256 _questionId, uint256 _choiceIndex) public {
    console.log("Voting on question:", _questionId);
    console.log("Choice index:", _choiceIndex);
    // ... resto del código
}
```

**2. Hardhat Console**:
```bash
npx hardhat console --network localhost

# En la consola:
const Contract = await ethers.getContractFactory("VotingContract");
const contract = await Contract.attach("0x5FbDB2...");
const result = await contract.getQuestion(1);
console.log(result);
```

### Logging

**Configurar logging en Django**:
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'polls.blockchain': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    },
}
```

**Usar en código**:
```python
import logging

logger = logging.getLogger('polls.blockchain')

def create_question(self, text, choices):
    logger.debug(f"Creating question: {text}")
    logger.info(f"Question created with {len(choices)} choices")
    logger.warning("Connection is slow")
    logger.error("Failed to create question")
```

## Contribuir

### Proceso de Pull Request

1. **Crear Issue** (opcional pero recomendado)
   - Describe el problema o feature
   - Discute el approach antes de codear

2. **Fork y Branch**
   ```bash
   git checkout -b feature/mi-feature
   ```

3. **Desarrollar y Testear**
   - Escribe código
   - Agrega tests
   - Asegura que todos los tests pasen

4. **Commit**
   ```bash
   git add .
   git commit -m "feat: mi nueva feature"
   ```

5. **Push**
   ```bash
   git push origin feature/mi-feature
   ```

6. **Crear Pull Request**
   - Descripción clara de cambios
   - Referencias a issues
   - Screenshots si hay cambios UI

7. **Code Review**
   - Responde a comentarios
   - Haz cambios solicitados
   - Mantén PR actualizado con develop

8. **Merge**
   - Maintainer mergeará después de aprobación

### Checklist de PR

- [ ] Código sigue estándares del proyecto
- [ ] Tests agregados y pasando
- [ ] Documentación actualizada
- [ ] No hay cambios no relacionados
- [ ] Commits son claros y descriptivos
- [ ] Branch está actualizado con develop

## Recursos para Desarrolladores

### Documentación Externa

- [Django Documentation](https://docs.djangoproject.com/)
- [Hardhat Documentation](https://hardhat.org/docs)
- [Web3.py Documentation](https://web3py.readthedocs.io/)
- [Solidity Documentation](https://docs.soliditylang.org/)
- [OpenZeppelin Docs](https://docs.openzeppelin.com/)

### Comunidad

- [Django Discord](https://discord.gg/django)
- [Ethereum Stack Exchange](https://ethereum.stackexchange.com/)
- [Hardhat Discord](https://discord.gg/hardhat)

### Herramientas Útiles

- **VS Code Extensions**:
  - Python
  - Solidity (by Juan Blanco)
  - Django Template
  - GitLens
  
- **Browser Extensions**:
  - MetaMask (wallet de prueba)
  - Django Debug Panel

---

**Última Actualización**: Diciembre 2024  
**Autor**: @Jorgez-tech

¿Preguntas? Abre un [issue en GitHub](https://github.com/Jorgez-tech/encuestas/issues).
