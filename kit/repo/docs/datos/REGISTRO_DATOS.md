# REGISTRO_DATOS — archivos de datos de {{NOMBRE}}

Los archivos de datos viven fuera de git (`data/` en {{DISPOSITIVO}} y `{{DESCARGAS}}` en la laptop).
Este registro sí está en git y es la única lista de qué archivo existe, dónde está y si ya se usó.
Origen (Trama): un archivo generado en el Project nunca se registró ni se copió al dispositivo y se
perdió de vista dos sesiones.

## Reglas
1. **El Project registra todo archivo de datos que genera, en la misma sesión:** nombre exacto,
   SHA-256, contenido, estado `entregado`. Va en el cierre de sesión junto con la BITACORA.
2. **{{LIDER}} lo copia a `data/`** y verifica el hash con `sha256sum`. Estado → `en equipo`.
3. **Toda tarea que carga datos** verifica en FASE 0 que el hash coincide. Si no coincide o falta:
   STOP. Al cargar, Code pasa el estado a `cargado (T-NNN)` en el commit de cierre.
4. **Ninguna sesión cierra** con un archivo en `entregado` sin listarlo en la BITACORA §3.
5. Versiones sustituidas se marcan `retirado`; no se borran de esta tabla.
6. Datos personales de terceros: solo los que permite el ADR de datos del proyecto.

## Archivos
| Archivo | SHA-256 (primeros 16) | Contenido | Estado |
|---|---|---|---|
