# Instrucciones para Desarrolladores

Este documento establece las buenas prácticas, el flujo de trabajo y las convenciones a seguir para contribuir a este proyecto. El objetivo es mantener un código limpio, consistente y mantenible.

## Filosofía del Proyecto

1.  **Seguridad Primero:** Especialmente en todo lo relacionado con la blockchain. Cualquier cambio en los smart contracts debe ser revisado exhaustivamente.
2.  **Claridad sobre Complejidad:** El código debe ser fácil de entender. Añade comentarios solo cuando sea necesario para explicar lógica compleja.
3.  **Documentación Continua:** Mantén la documentación actualizada a medida que realizas cambios en el código.

## Flujo de Trabajo con Git

Utilizamos un flujo de trabajo basado en ramas de características (`feature branches`) para mantener la rama `main` estable.

### Estrategia de Ramas
-   **`main`:** Contiene la versión de producción más reciente. No se debe hacer push directamente a esta rama.
-   **`develop`:** Es la rama de integración principal. Todas las nuevas características se fusionan aquí antes de pasar a `main`.
-   **`feature/<nombre-caracteristica>`:** Cada nueva funcionalidad se desarrolla en su propia rama, creada a partir de `develop`. Por ejemplo, `feature/integracion-web3py`.
-   **`fix/<nombre-arreglo>`:** Para correcciones de bugs.

### Proceso de Contribución
1.  **Sincroniza tu rama `develop`:**
    ```bash
    git checkout develop
    git pull origin develop
    ```
2.  **Crea una nueva rama de característica:**
    ```bash
    git checkout -b feature/mi-nueva-caracteristica
    ```
3.  **Desarrolla y haz commits:**
    -   Realiza cambios atómicos y haz commits con frecuencia.
    -   Escribe mensajes de commit claros y descriptivos, siguiendo el estándar de [Conventional Commits](https://www.conventionalcommits.org/).
        -   **`feat:`** para nuevas funcionalidades.
        -   **`fix:`** para correcciones de bugs.
        -   **`docs:`** para cambios en la documentación.
        -   **`style:`** para cambios de formato (espacios, puntos y comas, etc.).
        -   **`refactor:`** para cambios en el código que no arreglan un bug ni añaden una funcionalidad.
        -   **`test:`** para añadir o modificar pruebas.
    -   Ejemplo de un buen mensaje de commit:
        ```
        feat: Añadir endpoint para obtener resultados de votación

        Se ha creado el endpoint GET /api/votaciones/{id}/resultados/ que consulta
        el smart contract para devolver los resultados en tiempo real.
        ```

4.  **Mantén tu rama actualizada:**
    Regularmente, fusiona los cambios de `develop` en tu rama para evitar conflictos grandes al final.
    ```bash
    git fetch origin
    git rebase origin/develop
    ```

5.  **Abre un Pull Request (PR):**
    -   Cuando tu característica esté completa, haz push de tu rama a GitHub:
        ```bash
        git push -u origin feature/mi-nueva-caracteristica
        ```
    -   Abre un Pull Request desde tu rama hacia `develop`.
    -   En la descripción del PR, explica qué cambios has hecho y por qué. Si resuelves un issue, menciónalo (ej. `Cierra #123`).

6.  **Revisión de Código:**
    -   Al menos otro desarrollador (o un agente de IA) debe revisar tu PR.
    -   Atiende a los comentarios y realiza los cambios necesarios.

7.  **Fusión (Merge):**
    -   Una vez que el PR sea aprobado, será fusionado en `develop`.

## Convenciones de Código

### Backend (Python/Django)
-   Sigue el estándar **PEP 8**. Utiliza herramientas como `flake8` o `black` para formatear tu código automáticamente.
-   Nombra las variables y funciones en `snake_case`.
-   Nombra las clases en `CamelCase`.
-   Escribe docstrings para todos los módulos, clases y funciones.

### Smart Contracts (Solidity)
-   Sigue la [Guía de Estilo de Solidity](https://docs.soliditylang.org/en/v0.8.20/style-guide.html).
-   Utiliza el patrón **Checks-Effects-Interactions** para prevenir vulnerabilidades de re-entrada.
-   Nombra las funciones y variables en `camelCase`.
-   Nombra los contratos en `CamelCase`.

### Frontend (JavaScript/React)
-   Utiliza un formateador de código como `Prettier` para mantener un estilo consistente.
-   Nombra los componentes en `PascalCase` (ej. `VotingList.js`).
-   Utiliza hooks de React y componentes funcionales en lugar de componentes de clase.

## Pruebas (Testing)

-   **Backend:** Escribe pruebas unitarias para toda la lógica de negocio. Utiliza el framework de pruebas de Django.
-   **Smart Contracts:** Escribe pruebas exhaustivas con Hardhat. Prueba tanto los casos de éxito como los de fallo.
-   **Frontend:** Escribe pruebas unitarias para los componentes y pruebas de integración para los flujos de usuario.

Cualquier nueva funcionalidad debe ir acompañada de sus correspondientes pruebas.
