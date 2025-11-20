# Guía de Migración a Web3

Este documento ofrece una guía técnica detallada sobre el proceso de transformación de la aplicación de encuestas Django a una plataforma de votaciones descentralizada (DApp).

## 1. Fundamentos de la Decisión

### ¿Por qué una Arquitectura Híbrida?
Se optó por una arquitectura híbrida (Django + Blockchain) para maximizar las fortalezas de ambas tecnologías:
- **Django:** Proporciona un panel de administración robusto, gestión de usuarios (futuro), y la capacidad de realizar análisis de datos complejos.
- **Blockchain:** Garantiza la transparencia, inmutabilidad y seguridad del proceso de votación, que es la parte más crítica de la aplicación.
Esta aproximación permite una migración progresiva sin desechar la lógica de negocio ya existente y probada.

### Selección del Stack Tecnológico
- **Smart Contracts:** **Solidity** es el lenguaje estándar para la EVM (Ethereum Virtual Machine). Se eligió **OpenZeppelin Contracts** por sus implementaciones de interfaces y componentes de seguridad auditados, lo cual es crucial para evitar vulnerabilidades.
- **Framework de Desarrollo:** **Hardhat** fue seleccionado sobre otras alternativas (como Truffle o Brownie) por su moderno entorno de desarrollo, su excelente soporte para TypeScript, y su robusta red local para pruebas (`Hardhat Network`).
- **Integración con Backend:** **Web3.py** es la librería de elección para conectar el backend de Python con la blockchain, por su madurez y completo soporte del API de Ethereum.

## 2. Arquitectura del Smart Contract (`VotingContract.sol`)

El corazón de la DApp es el `VotingContract.sol`, que se encuentra en `blockchain/contracts/`.

### Estructura de Datos
- **`Pregunta` (struct):** Almacena la información de cada votación, incluyendo el texto de la pregunta, las opciones, el contador de votos para cada opción, y su estado (activa/inactiva).
- **`preguntas` (array):** Un array público de `Pregunta` que guarda todas las votaciones creadas.
- **`hasVoted` (mapping):** Un mapeo `(address => mapping(uint => bool))` que registra si una dirección ya ha votado en una pregunta específica, para prevenir el voto duplicado.

### Funciones Principales
- **`crearPregunta(string, string[])`:** Permite al "dueño" del contrato (`owner`) crear una nueva votación. Es una función privilegiada gracias al modificador `onlyOwner` de OpenZeppelin.
- **`votar(uint, uint)`:** La función principal para los usuarios. Permite a cualquier dirección emitir un voto. Incluye las siguientes protecciones:
    - `require(pregunta.activa, ...)`: Solo se puede votar en preguntas activas.
    - `require(!hasVoted[msg.sender][...], ...)`: Previene el voto duplicado.
    - `nonReentrant`: Modificador de OpenZeppelin para prevenir ataques de re-entrada.
- **`desactivarPregunta(uint)`:** Permite al `owner` cerrar una votación.

### Seguridad
- **Control de Acceso:** El contrato hereda de `Ownable.sol` de OpenZeppelin, asegurando que solo la dirección que desplegó el contrato pueda realizar acciones administrativas.
- **Prevención de Re-entrada:** El uso de `ReentrancyGuard.sol` protege las funciones de posibles vulnerabilidades que permitan llamadas múltiples maliciosas.

## 3. Proceso de Desarrollo y Despliegue

### Configuración del Entorno (Hardhat)
1.  **Instalación:** Dentro de la carpeta `blockchain/`, ejecutar `npm install` para instalar Hardhat y sus dependencias.
2.  **Compilación:**
    ```bash
    npx hardhat compile
    ```
    Este comando compila los contratos de Solidity y genera los artefactos (ABI y bytecode) necesarios para el despliegue y la interacción.

### Pruebas (Testing)
Las pruebas son un paso crucial. Se deben crear en el directorio `blockchain/test/`. Un buen conjunto de pruebas debe verificar:
- Que solo el `owner` pueda crear y desactivar preguntas.
- Que los usuarios puedan votar correctamente y que los votos se cuenten.
- Que se impida el voto doble.
- Que no se pueda votar en preguntas inactivas.
```bash
npx hardhat test
```

### Despliegue
Hardhat Ignition es el sistema recomendado para el despliegue.
1.  **Módulo de Despliegue:** Se define en `blockchain/ignition/modules/VotingContract.ts`.
2.  **Ejecución:**
    ```bash
    # Para desplegar en la red local de Hardhat
    npx hardhat ignition deploy ignition/modules/VotingContract.ts --network localhost

    # Para desplegar en una testnet (ej. Sepolia)
    npx hardhat ignition deploy ignition/modules/VotingContract.ts --network sepolia
    ```
    Tras el despliegue, se obtiene la dirección del contrato, que es fundamental para la integración con el backend y el frontend.

## 4. Integración con Django

La integración se realiza mediante la librería `Web3.py`.

### Pasos
1.  **Añadir Dependencia:** Agregar `web3` al archivo `requirements.txt` e instalarla (`pip install -r requirements.txt`).
2.  **Configurar Conexión:** En el `settings.py` de Django (o a través de variables de entorno), definir:
    - `ETHEREUM_NODE_URL`: La URL del nodo Ethereum (ej. `http://127.0.0.1:8545` para la red local de Hardhat).
    - `CONTRACT_ADDRESS`: La dirección del contrato desplegado.
    - `CONTRACT_ABI`: La ABI del contrato, que se puede obtener del archivo JSON generado por Hardhat en `blockchain/artifacts/contracts/VotingContract.sol/VotingContract.json`.
3.  **Crear un Módulo de Servicio:** Es una buena práctica crear un módulo (ej. `core/blockchain_service.py`) que encapsule toda la lógica de interacción con Web3.py.
    ```python
    from web3 import Web3
    from django.conf import settings

    def get_contract():
        w3 = Web3(Web3.HTTPProvider(settings.ETHEREUM_NODE_URL))
        contract = w3.eth.contract(
            address=settings.CONTRACT_ADDRESS,
            abi=settings.CONTRACT_ABI
        )
        return contract

    def get_question_details(question_id):
        contract = get_contract()
        # Las funciones de solo lectura se llaman con .call()
        return contract.functions.preguntas(question_id).call()
    ```
4.  **Integrar en las Vistas de Django:** Las vistas de la API de Django utilizarán este servicio para interactuar con la blockchain. Las transacciones que modifican el estado (como crear una pregunta) requerirán que el backend gestione una clave privada o delegue la firma al frontend.

## 5. Roadmap Técnico

La migración se está realizando de forma incremental:

-   [x] **Fase 1: Smart Contract:** Desarrollo, pruebas y despliegue local del `VotingContract.sol`.
-   [ ] **Fase 2: Integración Backend:** Conectar Django con el contrato a través de `Web3.py`. Crear los endpoints de la API necesarios.
-   [ ] **Fase 3: Desarrollo Frontend:** Construir la interfaz de usuario para conectar Metamask e interactuar con la plataforma.
-   [ ] **Fase 4: Despliegue a Testnet:** Desplegar el contrato y la aplicación en una red de prueba pública para realizar pruebas E2E.
-   [ ] **Fase 5: Auditoría y Mainnet:** Realizar una auditoría de seguridad del contrato antes del despliegue final en la red principal.
