# Órdenes de ejecución

Tareas que esta sesión de Claude no puede correr porque el proxy de red bloquea el destino
(archive.org, apollo.io, los sitios de las agencias, LinkedIn). Cada orden es
autocontenida: quien la ejecuta no necesita contexto del proyecto ni tomar decisiones.

| # | Orden | Bloqueo | Devuelve |
|---|---|---|---|
| 01 | `01-barrido-wayback.md` | archive.org | `salidas-detectadas.csv` + `cobertura-equipos.csv` |

Regla: el ejecutor corre y devuelve datos crudos. El análisis, el scoring y los mensajes
los hago yo cuando vuelven.
