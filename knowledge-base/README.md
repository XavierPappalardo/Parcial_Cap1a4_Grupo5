# Base de Conocimiento — La librería con despliegue en el VPS

Proyecto correspondiente al Parcial de **Programación III (UTN - Tecnicatura Universitaria en Programación)**.  
Esta base de conocimiento documenta de forma exhaustiva las especificaciones técnicas, el modelo relacional, las reglas de negocio, la arquitectura y los procedimientos de despliegue del sistema.

---

## Índice de Documentos

| # | Archivo | Contenido principal |
|---|---|---|
| 01 | [01_vision_y_objetivos.md](01_vision_y_objetivos.md) | Propósito, objetivos por actor, alcance v1.0, fuera de alcance y métricas de éxito. |
| 02 | [02_descripcion_general.md](02_descripcion_general.md) | Stack tecnológico, arquitectura general en capas/módulos y resumen de endpoints. |
| 03 | [03_actores_y_roles.md](03_actores_y_roles.md) | Actores del sistema, matriz de permisos y contratos funcionales. |
| 04 | [04_modelo_de_datos.md](04_modelo_de_datos.md) | Entidades, ERD, relaciones de agregación/composición/asociación/1:1/N:N y seed data. |
| 05 | [05_reglas_de_negocio.md](05_reglas_de_negocio.md) | Catálogo de las 12 reglas de negocio obligatorias (RN-01 a RN-12) y garantes de código. |
| 06 | [06_funcionalidades.md](06_funcionalidades.md) | Historias de usuario (US-001 a US-008) por épica con criterios de aceptación. |
| 07 | [07_flujos_principales.md](07_flujos_principales.md) | Flujos extremo a extremo: lifespan, alta con relaciones, venta atómica y lecturas sin N+1. |
| 08 | [08_arquitectura_propuesta.md](08_arquitectura_propuesta.md) | Patrones de diseño, estructura modular obligatoria, seguridad y variables de entorno. |
| 09 | [09_decisiones_y_supuestos.md](09_decisiones_y_supuestos.md) | Decisiones arquitectónicas fundamentadas (DD-01 a DD-05) y supuestos técnicos. |
| 10 | [10_preguntas_abiertas.md](10_preguntas_abiertas.md) | Inconsistencias analizadas, resoluciones técnicas y preguntas abiertas priorizadas. |
| 11 | [11_despliegue_y_vps.md](11_despliegue_y_vps.md) | Configuración de Docker Alpine, comandos de despliegue y matriz de casos de prueba C y D. |

---

## Guía Rápida de Navegación

1. **Para entender el dominio y los requisitos**: Leer [01_vision_y_objetivos.md](01_vision_y_objetivos.md) y [03_actores_y_roles.md](03_actores_y_roles.md).
2. **Para entender las entidades y relaciones**: Estudiar [04_modelo_de_datos.md](04_modelo_de_datos.md) y [05_reglas_de_negocio.md](05_reglas_de_negocio.md).
3. **Para entender la arquitectura y código**: Revisar [02_descripcion_general.md](02_descripcion_general.md) y [08_arquitectura_propuesta.md](08_arquitectura_propuesta.md).
4. **Para implementar endpoints y casos de uso**: Guiarse por [06_funcionalidades.md](06_funcionalidades.md) y [07_flujos_principales.md](07_flujos_principales.md).
5. **Para empaquetar y desplegar en VPS**: Consultar [11_despliegue_y_vps.md](11_despliegue_y_vps.md).
