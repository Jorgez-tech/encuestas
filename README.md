# Plataforma de Votaciones Descentralizada para Chile

Este proyecto transforma una aplicación de encuestas tradicional basada en Django en una plataforma de votaciones segura, transparente y descentralizada, utilizando tecnologías Web3. El objetivo es ofrecer una solución robusta para procesos de votación en el territorio chileno, garantizando la integridad y la inmutabilidad de los resultados.

## Propósito y Alcance

### Visión
Nuestra visión es crear una plataforma de votaciones electrónicas confiable y accesible para organizaciones en Chile. Al integrar la tecnología blockchain, buscamos eliminar la necesidad de intermediarios, reducir la posibilidad de fraude y aumentar la confianza de los participantes en el proceso electoral.

### Fundamentos de la Transición a Web3
La migración a una arquitectura Web3 responde a la necesidad de mayor seguridad y transparencia en procesos de votación. La tecnología blockchain permite que cada voto sea un registro inmutable y verificable públicamente, sin comprometer la privacidad del votante.

### Objetivos Estratégicos
- **Seguridad:** Utilizar smart contracts para asegurar que las reglas de la votación se cumplan sin posibilidad de manipulación.
- **Transparencia:** Permitir que cualquier participante pueda auditar el proceso de votación y verificar los resultados de forma independiente.
- **Descentralización:** Eliminar puntos únicos de fallo, asegurando la disponibilidad y resistencia a la censura de la plataforma.
- **Accesibilidad:** Facilitar la participación a través de una interfaz de usuario intuitiva y la popular billetera digital Metamask.

## Arquitectura
La plataforma utiliza una arquitectura híbrida que combina la robustez de un backend tradicional con la seguridad de la tecnología blockchain.

### Arquitectura Actual (Legacy)
- **Backend:** Django
- **Base de Datos:** PostgreSQL (o SQLite para desarrollo local)
- **Servidor:** Servidor web tradicional (ej. Gunicorn, Nginx)

### Arquitectura Futura (Web3)
- **Backend:** Django, con integración a través de la librería `Web3.py` para comunicarse con la blockchain.
- **Frontend:** (Por definir, ej. React, Vue), con conexión a Metamask.
- **Blockchain:** Red compatible con Ethereum (ej. Polygon, para menores costos de transacción).
- **Smart Contracts:** `VotingContract.sol`, desarrollado en Solidity y basado en las seguras librerías de OpenZeppelin. Gestiona la lógica de las votaciones.
- **Almacenamiento Descentralizado:** IPFS (InterPlanetary File System) para almacenar datos de votaciones (propuestas, etc.) de forma inmutable.

![Arquitectura Híbrida](https://i.imgur.com/diagrama_conceptual.png)  *Diagrama conceptual de la arquitectura.*

## Roadmap de Migración

El proceso de transformación se divide en las siguientes fases:

### Fase 1: Desarrollo del Smart Contract (Completada)
- ✅ Diseño y desarrollo del `VotingContract.sol` con Solidity.
- ✅ Implementación de funcionalidades clave: creación de votaciones, registro de votos, y conteo de resultados.
- ✅ Uso de OpenZeppelin para garantizar la seguridad del contrato.
- ✅ Despliegue y pruebas en una red local de Hardhat.

### Fase 2: Integración con el Backend
- ⏳ Integrar `Web3.py` en el backend de Django.
- ⏳ Desarrollar una API para que el frontend pueda interactuar con el smart contract a través del backend.
- ⏳ Sincronizar el estado de las votaciones entre la base de datos de Django y la blockchain.

### Fase 3: Desarrollo del Frontend Web3
- ⏳ Crear una interfaz de usuario que permita a los usuarios conectar sus billeteras de Metamask.
- ⏳ Desarrollar los componentes para visualizar las votaciones, emitir votos y ver los resultados.

### Fase 4: Despliegue en Testnet y Mainnet
- ⏳ Desplegar el smart contract en una red de prueba (Testnet, ej. Sepolia) para realizar pruebas en un entorno realista.
- ⏳ Realizar una auditoría de seguridad del smart contract.
- ⏳ Desplegar la aplicación completa en una red principal (Mainnet) y hacerla accesible al público.

## Instrucciones de Instalación

Para ejecutar este proyecto, necesitarás dos entornos: uno para el backend de Django y otro para el desarrollo de blockchain con Hardhat.

### Backend (Django)
1. Clona el repositorio:
   ```bash
   git clone <URL-del-repositorio>
   cd nombre-del-repositorio
   ```
2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Linux/macOS
   # o
   venv\Scripts\activate    # En Windows
   ```
3. Instala las dependencias de Python:
   ```bash
   pip install -r requirements.txt
   ```
4. Aplica las migraciones y arranca el servidor:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

### Blockchain (Hardhat)
1. Navega al directorio de blockchain:
   ```bash
   cd blockchain
   ```
2. Instala las dependencias de Node.js:
   ```bash
   npm install
   ```
3. Compila el smart contract:
   ```bash
   npx hardhat compile
   ```
4. Para más detalles sobre cómo desplegar y probar el contrato, consulta el archivo `blockchain/README.md`.

## Contribuciones
Este es un proyecto en evolución. Para contribuir, por favor consulta el archivo `INSTRUCCIONES_DESARROLLADORES.md`.
