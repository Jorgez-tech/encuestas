# Frontend de la Plataforma de Votaciones

Este directorio contendrá todo el código fuente y la configuración para el frontend de la plataforma de votaciones.

## Arquitectura del Frontend

El frontend será una **Aplicación de Página Única (SPA)**, desarrollada con un framework moderno de JavaScript como **React** o **Vue**. Su principal responsabilidad será ofrecer una interfaz de usuario clara y sencilla para interactuar con la plataforma de votaciones.

La arquitectura se basará en los siguientes componentes clave:

1.  **Componentes de la Interfaz:**
    *   **Vista de Votaciones:** Mostrará una lista de las votaciones activas y pasadas.
    *   **Detalle de Votación:** Presentará la información completa de una votación, incluyendo las opciones y los resultados en tiempo real.
    *   **Componente de Voto:** Permitirá a los usuarios emitir su voto de forma segura.

2.  **Integración con Web3:**
    *   **Conexión con la Billetera:** Utilizará librerías como `ethers.js` o `web3.js` para conectar la aplicación con la billetera de Metamask del usuario.
    *   **Interacción con la API del Backend:** Se comunicará con los endpoints expuestos por el backend de Django para obtener información de las votaciones y enviar solicitudes que requieran interacción con el smart contract.
    *   **Firma de Transacciones:** Cuando un usuario emita un voto, el frontend preparará la transacción y solicitará al usuario que la firme a través de Metamask.

## Tecnologías Recomendadas

*   **Framework:** React (con Create React App) o Vue.js (con Vue CLI).
*   **Librería Web3:** Ethers.js (preferida por su simplicidad y robustez) o Web3.js.
*   **Gestión de Estado:** Redux (para React) o Vuex (para Vue), para manejar el estado de la aplicación de forma consistente.
*   **Estilos:** CSS Modules, Styled Components, o un framework como Tailwind CSS.

## Configuración del Entorno de Desarrollo (Ejemplo con React)

A continuación se presenta una guía de cómo se podría configurar el entorno de desarrollo:

1.  **Navega a este directorio:**
    ```bash
    cd frontend
    ```

2.  **Crea una nueva aplicación de React:**
    ```bash
    npx create-react-app .
    ```

3.  **Instala las dependencias necesarias:**
    ```bash
    npm install ethers
    ```

4.  **Inicia el servidor de desarrollo:**
    ```bash
    npm start
    ```
    La aplicación estará disponible en `http://localhost:3000`.

## Flujo de Interacción del Usuario

1.  **Conectar Billetera:**
    *   El usuario hace clic en un botón "Conectar Metamask".
    *   La aplicación solicita al usuario que apruebe la conexión a través de la extensión de Metamask.
    *   Una vez conectado, la aplicación muestra la dirección de la billetera del usuario.

2.  **Visualizar Votaciones:**
    *   El frontend realiza una llamada al endpoint `GET /api/votaciones/` del backend para obtener la lista de votaciones.
    *   La lista se muestra en la interfaz.

3.  **Emitir un Voto:**
    *   El usuario selecciona una opción en una votación activa.
    *   Al hacer clic en "Votar", el frontend construye una transacción para llamar a la función `vote` del `VotingContract`.
    *   El frontend solicita al backend la información necesaria para la transacción (si es necesario).
    *   Se abre una ventana de Metamask pidiendo al usuario que confirme y firme la transacción.
    *   Una vez que la transacción es confirmada en la blockchain, la interfaz se actualiza para reflejar el voto.

4.  **Ver Resultados:**
    *   El frontend consulta el endpoint `GET /api/votaciones/<id>/` para obtener los resultados actualizados, que el backend a su vez ha obtenido de la blockchain.
    *   Los resultados se muestran en un gráfico o una tabla.

## Componentes Clave a Desarrollar

*   **`ConnectWalletButton.js`:** Un componente reutilizable para gestionar la conexión con Metamask.
*   **`VotingList.js`:** Muestra la lista de votaciones obtenidas del backend.
*   **`VotingDetail.js`:** Muestra los detalles y opciones de una votación.
*   **`VoteModal.js`:** Un componente que se abre para que el usuario confirme su voto antes de enviar la transacción.
*   **`ResultsChart.js`:** Visualiza los resultados de la votación.
