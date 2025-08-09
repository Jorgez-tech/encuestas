# Guía de Preparación para Producción y Despliegue en GitHub Pages

Este documento describe el proceso profesional para preparar, optimizar y desplegar una aplicación web en GitHub Pages usando GitHub Actions. Sigue este checklist y las recomendaciones para asegurar un flujo robusto y automatizado.

---

## 1. Preparación para Producción

- [ ] Verificar que el build de la aplicación se complete sin errores
- [ ] Configurar correctamente las rutas relativas para assets y recursos estáticos
- [ ] Optimizar imágenes, CSS y JS (minificación, compresión, eliminación de código muerto)
- [ ] Limpiar el repositorio: eliminar archivos temporales, backups y carpetas innecesarias
- [ ] Usar un archivo `.gitignore` adecuado para excluir archivos no relevantes (por ejemplo, entornos virtuales, archivos de configuración locales, bases de datos temporales)
- [ ] Revisar y actualizar las dependencias en `requirements.txt` o `package.json`, eliminando las que no se usen
- [ ] Documentar cualquier variable de entorno o configuración especial necesaria para producción

---

## 2. Configuración de Despliegue (GitHub Actions + GitHub Pages)

- [ ] Crear un workflow en `.github/workflows/deploy.yml` para automatizar el build y despliegue
- [ ] Si usas frontend (React, Vue, etc.), configurar el campo `homepage` en `package.json`:
  ```json
  "homepage": "https://<usuario>.github.io/<repositorio>"
  ```
- [ ] Usar la acción `peaceiris/actions-gh-pages` para publicar el contenido estático:
  ```yaml
  - name: Deploy to GitHub Pages
    uses: peaceiris/actions-gh-pages@v3
    with:
      github_token: ${{ secrets.GITHUB_TOKEN }}
      publish_dir: ./build  # o ./staticfiles, según corresponda
  ```
- [ ] En Settings > Pages del repositorio, seleccionar la rama y carpeta fuente (por ejemplo, `gh-pages` o `/docs`)
- [ ] Proteger la rama de despliegue si es necesario

---

## 3. Checklist de Validación

- [ ] Revisar los logs de GitHub Actions para asegurar que el workflow se ejecutó correctamente
- [ ] Verificar el estado del despliegue en Settings > Pages (debe mostrar la URL pública activa)
- [ ] Probar la aplicación en la URL pública de GitHub Pages
- [ ] Revisar la consola del navegador para detectar errores de carga de recursos o rutas
- [ ] Validar que los assets (CSS, JS, imágenes) se sirvan correctamente

---

## 4. Consejos Adicionales

- [ ] Configurar el manejo de caché en el workflow para acelerar builds repetidos
- [ ] Mantener una estructura de carpetas clara: separar código fuente, archivos estáticos y documentación
- [ ] Usar ramas dedicadas para staging/pruebas antes de fusionar a producción
- [ ] Documentar el proceso de despliegue en el README o en un archivo específico
- [ ] Para escalar el sitio, considerar el uso de un CDN o migrar a un servicio de hosting especializado si se requieren funcionalidades backend

---

### Recursos útiles
- [Documentación oficial de GitHub Pages](https://docs.github.com/en/pages)
- [peaceiris/actions-gh-pages](https://github.com/peaceiris/actions-gh-pages)
- [Ejemplo de workflow de despliegue](https://github.com/peaceiris/actions-gh-pages#%EF%B8%8F-static-site-generators)

---

_Asegúrate de adaptar este checklist a las necesidades específicas de tu proyecto y mantenerlo actualizado._
