# Backend de la Plataforma de Votaciones

Este directorio contiene todo el código fuente y la configuración para el backend de la plataforma, desarrollado con Django.

## Arquitectura del Backend

El backend sigue una arquitectura híbrida:

1.  **Componente Tradicional (Django):**
    *   **Gestión de Usuarios:** (Futuro) Manejará la autenticación y autorización de usuarios que administran las votaciones.
    *   **Panel de Administración:** Proporciona una interfaz para crear, gestionar y supervisar las votaciones.
    *   **API REST:** Ofrece endpoints para que el frontend interactúe con la lógica de negocio que no está en la blockchain.

2.  **Componente de Integración Web3 (Web3.py):**
    *   **Conexión con la Blockchain:** Utiliza la librería `Web3.py` para comunicarse con un nodo de Ethereum (local, de prueba o principal).
    *   **Interacción con el Smart Contract:** Envía transacciones al `VotingContract` para realizar acciones como:
        *   Crear nuevas propuestas de votación.
        *   Activar o desactivar una votación.
        *   Consultar el estado y los resultados de las votaciones.
    *   **Gestión de Eventos:** Escucha los eventos emitidos por el smart contract para mantener la base de datos de Django sincronizada con la blockchain.

## Tecnologías Utilizadas

*   **Framework:** Django 4.2.15
*   **Base de Datos:** SQLite (para desarrollo), PostgreSQL (para producción)
*   **Integración Blockchain:** Web3.py
*   **Servidor de Desarrollo:** Django Development Server
*   **Servidor de Producción:** Gunicorn + Nginx (recomendado)

## Configuración del Entorno

Sigue estos pasos para configurar el entorno de desarrollo del backend:

1.  **Clona el repositorio** (si aún no lo has hecho):
    ```bash
    git clone <URL-del-repositorio>
    cd nombre-del-repositorio
    ```

2.  **Crea y activa un entorno virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Linux/macOS
    # o
    venv\Scripts\activate    # En Windows
    ```

3.  **Instala las dependencias:**
    El archivo `requirements.txt` contiene todas las librerías de Python necesarias.
    ```bash
    pip install -r requirements.txt
    ```
    Para la integración con Web3, se añadirá `web3.py` a este archivo.

4.  **Configura las variables de entorno:**
    Crea un archivo `.env` en el directorio raíz del proyecto para almacenar las variables sensibles, como:
    ```
    DEBUG=True
    SECRET_KEY='tu-secret-key'
    DATABASE_URL='sqlite:///db.sqlite3'
    ETHEREUM_NODE_URL='http://127.0.0.1:8545'  # URL del nodo Hardhat local
    CONTRACT_ADDRESS='0x5FbDB2315678afecb367f032d93F642f64180aa3' # Dirección del contrato desplegado
    ```

5.  **Aplica las migraciones de la base de datos:**
    ```bash
    python manage.py migrate
    ```

6.  **Crea un superusuario** para acceder al panel de administración:
    ```bash
    python manage.py createsuperuser
    ```

7.  **Inicia el servidor de desarrollo:**
    ```bash
    python manage.py runserver
    ```
    El backend estará disponible en `http://127.0.0.1:8000`.

## API Endpoints

(Esta sección se completará a medida que se desarrolle la API)

A continuación se describen los endpoints que el backend expondrá para la comunicación con el frontend:

*   **`GET /api/votaciones/`**
    *   **Descripción:** Obtiene la lista de todas las votaciones disponibles.
    *   **Respuesta:** Un array de objetos, cada uno con información de una votación (ID, título, descripción, estado).

*   **`GET /api/votaciones/<id>/`**
    *   **Descripción:** Obtiene los detalles de una votación específica, incluyendo los resultados desde la blockchain.
    *   **Respuesta:** Un objeto con los detalles de la votación.

*   **`POST /api/votaciones/`**
    *   **Descripción:** (Protegido) Crea una nueva votación. Esta acción llama a la función correspondiente en el smart contract.
    *   **Cuerpo de la Petición:** `{ "titulo": "...", "descripcion": "...", "opciones": [...] }`

## Integración con el Smart Contract

La conexión con la blockchain se gestionará en un módulo dedicado de Django (ej. `blockchain_integration.py`). Este módulo será responsable de:

*   Inicializar la conexión con el nodo de Ethereum.
*   Cargar la ABI (Interface Binaria de la Aplicación) y la dirección del `VotingContract`.
*   Abstraer las llamadas al smart contract en funciones de Python fáciles de usar.

Un ejemplo de cómo se podría ver una función de consulta:
```python
from web3 import Web3

def obtener_resultados(votacion_id):
    # Conectar al nodo
    w3 = Web3(Web3.HTTPProvider(ETHEREUM_NODE_URL))
    # Cargar el contrato
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    # Llamar a la función del contrato
    resultados = contract.functions.obtenerResultados(votacion_id).call()
    return resultados
```
