# Mapa de Hosts y Entornos - Odoo by Blink

**Versión**: 1.0
**Última actualización**: 20 de Enero 2026
**Propósito**: Mapeo centralizado de hosts, entornos, ramas y configuraciones para arquitectura multi-cliente

---

## Tabla de Hosts y Entornos

| Host/Subdominio | Cliente | Entorno | Rama Deploy | Base de Datos | Archivo Config | Puerto | Notas |
|-----------------|---------|---------|-------------|---------------|----------------|--------|-------|
| **corteperfecto.somosblink.com** | Corte Perfecto | `production` | `main` | `corteperfecto-prod` | `corteperfecto.somosblink.com.conf` | 8076 | Cliente activo - Producción (por crear) |
| **corteperfecto-test.somosblink.com** | Corte Perfecto | `test` | `dev` | `corteperfecto-test` | `corteperfecto-test.somosblink.com.conf` | 8075 | Testing pre-prod - BD existente (ACTIVO) |
| **demo.somosblink.com** | Blink (interno) | `demo` | `demo` | `demo-showcase` | `demo.somosblink.com.conf` | 8077 | Demos para prospectos, datos de ejemplo |
| **blink.somosblink.com** | Blink (interno) | `internal` | `blink` | `blink-internal` | `blink.somosblink.com.conf` | 8078 | Uso interno de Blink, desarrollo avanzado |
| **localhost** | Desarrollo | `local` | `dev` | `odoo-dev` | `localhost.conf` | 8069 | Entorno de desarrollo local |

---

## Descripción de Entornos

### 🟢 Production (`production`)
- **Propósito**: Entorno de producción para clientes activos
- **Estabilidad**: Máxima - código probado y validado
- **Rama fuente**: `main` (protegida)
- **Deployment**: Manual con aprobación, vía CI/CD pipeline
- **Backups**: Automáticos cada 6 horas + diarios
- **Monitoreo**: 24/7 con alertas
- **SSL**: Obligatorio (Let's Encrypt)
- **Acceso**: Solo administradores y cliente final

### 🟡 Test (`test`)
- **Propósito**: Validación pre-producción, UAT (User Acceptance Testing)
- **Estabilidad**: Alta - código candidato a producción
- **Rama fuente**: `test`
- **Deployment**: Automático al hacer merge a `test`
- **Backups**: Diarios, retención 7 días
- **Monitoreo**: Business hours
- **SSL**: Obligatorio
- **Acceso**: Equipo interno + cliente para validación
- **Base de datos**: Copia sanitizada de producción (datos reales anonimizados)

### 🔵 Demo (`demo`)
- **Propósito**: Demostraciones comerciales para prospectos
- **Estabilidad**: Media-Alta - features estables y atractivas
- **Rama fuente**: `demo`
- **Deployment**: Semi-automático, por solicitud de equipo comercial
- **Backups**: Semanales, retención 30 días
- **Monitoreo**: Business hours
- **SSL**: Obligatorio
- **Acceso**: Equipo comercial + prospectos (acceso temporal)
- **Base de datos**: Datos ficticios de ejemplo, reset mensual
- **Características**: Datos de muestra bien diseñados, casos de uso variados

### 🟣 Internal (`internal`)
- **Propósito**: Desarrollo interno de Blink, testing de features nuevas
- **Estabilidad**: Media - código en desarrollo activo
- **Rama fuente**: `blink`
- **Deployment**: Automático al hacer push a `blink`
- **Backups**: Opcionales, no críticos
- **Monitoreo**: Básico
- **SSL**: Recomendado
- **Acceso**: Solo equipo de desarrollo de Blink
- **Base de datos**: Datos de prueba internos

### ⚪ Local (`local`)
- **Propósito**: Desarrollo individual en máquina local
- **Estabilidad**: Variable - código en desarrollo
- **Rama fuente**: `dev` o feature branches
- **Deployment**: Manual, desarrollo local
- **Backups**: Responsabilidad del desarrollador
- **Monitoreo**: N/A
- **SSL**: Opcional (HTTP suficiente)
- **Acceso**: Solo desarrollador local
- **Base de datos**: SQLite o PostgreSQL local con datos mínimos

---

## Flujo de Deployment por Host

### 1. Deployment a Production (Cliente Real)

```mermaid
dev → test → main → corteperfecto.somosblink.com (production)
```

**Proceso**:
1. Desarrollador trabaja en rama `dev` o feature branch
2. Merge a `test` para validación en `corteperfecto-test.somosblink.com`
3. Cliente valida en entorno de test (UAT)
4. Aprobación formal del cliente (ticket/email)
5. Merge de `test` → `main` (requiere pull request + code review)
6. CI/CD pipeline ejecuta deployment automático a producción
7. Script de deployment:
   - Detecta hostname (`corteperfecto.somosblink.com`)
   - Carga configuración correspondiente (`config/hosts/corteperfecto.somosblink.com.conf`)
   - Actualiza código en servidor
   - Actualiza módulos de Odoo si es necesario
   - Reinicia servicio systemd (`odoo-corteperfecto`)
   - Ejecuta health checks
   - Notifica a equipo y cliente

**Comando**:
```bash
./deployment/deploy.py --host corteperfecto.somosblink.com --branch main --notify
```

---

### 2. Deployment a Test (Pre-Producción)

```mermaid
dev → test → corteperfecto-test.somosblink.com
```

**Proceso**:
1. Desarrollador hace merge de feature branch a `test`
2. Deployment automático via webhook/CI
3. Script de deployment carga `corteperfecto-test.somosblink.com.conf`
4. Notificación a cliente para validación
5. Si hay issues, se corrige en `test` directamente (hotfix) o se revierte

**Comando**:
```bash
./deployment/deploy.py --host corteperfecto-test.somosblink.com --branch test --auto
```

---

### 3. Deployment a Demo (Comercial)

```mermaid
blink → demo → demo.somosblink.com
```

**Proceso**:
1. Equipo selecciona features estables de rama `blink`
2. Merge selectivo a rama `demo`
3. Deployment manual o por solicitud
4. Reset de base de datos a estado limpio con datos de ejemplo
5. Validación de demos por equipo comercial

**Comando**:
```bash
./deployment/deploy.py --host demo.somosblink.com --branch demo --reset-db
```

---

### 4. Deployment a Internal (Blink)

```mermaid
dev → blink → blink.somosblink.com
```

**Proceso**:
1. Merge de features a rama `blink` (desarrollo activo)
2. Deployment automático (webhook)
3. Sin validaciones estrictas, para experimentación rápida
4. Usado para testing interno antes de promover a `test`

**Comando**:
```bash
./deployment/deploy.py --host blink.somosblink.com --branch blink --skip-validations
```

---

### 5. Deployment Local (Desarrollo)

```mermaid
feature-branch → local (dev machine)
```

**Proceso**:
1. Desarrollador clona repo
2. Crea/edita `config/hosts/localhost.conf` con su configuración local
3. Ejecuta Odoo localmente: `./odoo-bin -c config/hosts/localhost.conf`
4. Desarrollo y testing local
5. Commit y push cuando esté listo

**Comando**:
```bash
python3 odoo18/odoo-bin -c config/hosts/localhost.conf --dev=all
```

---

## Estrategia de Ramas y Promoción de Código

### Jerarquía de Ramas

```
main (producción)
  ↑
test (pre-producción)
  ↑
dev (desarrollo)
  ↑
feature/* (features individuales)

[Paralelas]
blink → demo (interno)
```

### Reglas de Merge

| Desde | Hacia | Requiere | Aprobación |
|-------|-------|----------|------------|
| `feature/*` | `dev` | Pull Request | 1 revisor |
| `dev` | `test` | Pull Request + Tests passing | 1 revisor senior |
| `test` | `main` | Pull Request + UAT approval | 2 revisores + cliente |
| `dev` | `blink` | Push directo | N/A (interno) |
| `blink` | `demo` | Pull Request | 1 revisor |
| `main` | `hotfix/*` | Emergency only | CTO approval |

---

## Convenciones de Nomenclatura

### Hosts
```
[cliente].[entorno].somosblink.com
```

**Excepciones**:
- Producción: `[cliente].somosblink.com` (sin entorno en el nombre)
- Test: `[cliente]-test.somosblink.com`
- Staging: `[cliente]-staging.somosblink.com` (si se usa)

**Ejemplos**:
- ✅ `corteperfecto.somosblink.com` (prod)
- ✅ `corteperfecto-test.somosblink.com` (test)
- ✅ `nuevocliente.somosblink.com` (prod)
- ✅ `nuevocliente-test.somosblink.com` (test)
- ❌ `corteperfecto-prod.somosblink.com` (redundante)

### Bases de Datos
```
[cliente]-[entorno]
```

**Ejemplos**:
- `corteperfecto-prod`
- `corteperfecto-test`
- `nuevocliente-prod`
- `demo-showcase`
- `blink-internal`

### Archivos de Configuración
```
[hostname-completo].conf
```

**Ejemplos**:
- `corteperfecto.somosblink.com.conf`
- `corteperfecto-test.somosblink.com.conf`
- `localhost.conf`

### Servicios Systemd
```
odoo-[cliente]-[entorno]
```

**Ejemplos**:
- `odoo-corteperfecto-prod`
- `odoo-corteperfecto-test`
- `odoo-demo`

### Puertos
```
Base: 8069 (Odoo default)
Clients: 8070-8999
```

**Asignación**:
- 8069: Reservado (Odoo default)
- 8070-8099: Clientes producción
- 8100-8199: Clientes test
- 8200-8299: Entornos internos
- 8300+: Desarrollo local

**Registro de Puertos** (actualizar al agregar cliente):
| Puerto | Host | Cliente | Entorno |
|--------|------|---------|---------|
| 8075 | corteperfecto.somosblink.com | Corte Perfecto | Production |
| 8076 | corteperfecto-test.somosblink.com | Corte Perfecto | Test |
| 8077 | demo.somosblink.com | Blink | Demo |
| 8078 | blink.somosblink.com | Blink | Internal |
| 8069 | localhost | Dev | Local |

---

## Buenas Prácticas para Mantener este Mapa Actualizado

### 1. Actualización Obligatoria
- **ANTES** de hacer deployment de nuevo cliente → Actualizar este documento
- **ANTES** de crear nuevo entorno → Registrar en la tabla
- **DESPUÉS** de cambio de configuración → Documentar cambios

### 2. Proceso de Alta de Nuevo Cliente

**Checklist**:
```
[ ] Definir hostname(s) siguiendo convenciones
[ ] Asignar puertos disponibles
[ ] Crear entrada en tabla de hosts
[ ] Crear archivo config/hosts/[hostname].conf
[ ] Crear documentación docs/clients/[cliente].md
[ ] Actualizar registro de puertos
[ ] Crear base de datos
[ ] Configurar servicio systemd
[ ] Configurar SSL/certificado
[ ] Hacer deployment inicial
[ ] Validar con cliente
[ ] Commit de documentación actualizada
```

### 3. Control de Versiones
- Este documento debe estar en Git (rama `main`)
- Cada cambio debe ser un commit separado con mensaje descriptivo:
  ```
  docs: Agregar host nuevocliente.somosblink.com a mapa de entornos
  docs: Actualizar puerto para corteperfecto-test a 8076
  docs: Modificar rama de deployment de demo a 'demo'
  ```

### 4. Revisión Periódica
- **Mensual**: Revisar que hosts activos coincidan con tabla
- **Trimestral**: Auditar puertos asignados vs en uso
- **Semestral**: Validar que archivos de configuración existen y están vigentes
- **Anual**: Revisión completa de arquitectura y optimizaciones

### 5. Automatización
- Script `scripts/audit_hosts.py` para validar:
  - Hosts en tabla vs archivos de config existentes
  - Puertos asignados vs puertos en uso
  - Bases de datos registradas vs bases de datos existentes
  - Servicios systemd configurados

**Ejecutar**:
```bash
python scripts/audit_hosts.py --report --fix-docs
```

### 6. Documentación de Cambios
Cuando cambies algo en la arquitectura, actualizar:
- [ ] Este documento (`docs/host-environment-map.md`)
- [ ] Documentación del cliente (`docs/clients/[cliente].md`)
- [ ] Archivo de configuración (`config/hosts/[host].conf`)
- [ ] README principal si afecta uso general
- [ ] Changelog (`CHANGELOG.md`) si es cambio significativo

### 7. Comunicación
- **Slack/Discord**: Notificar cambios de infraestructura al equipo
- **Clientes**: Informar cambios que los afecten (cambio de URL, mantenimiento)
- **Documentación**: Mantener enlaces actualizados en wikis/notion/confluence

### 8. Backup de Configuraciones
- Antes de modificar archivo de configuración de producción → Backup
- Guardar copias de configuraciones antiguas en `config/archive/`
- Nombrar backups con fecha: `corteperfecto.somosblink.com.conf.2026-01-20.bak`

### 9. Validación Pre-Deployment
Script pre-deployment debe validar:
- Host existe en este mapa
- Archivo de configuración existe
- Base de datos existe
- Puerto no está en conflicto
- Rama es la correcta para el entorno

### 10. Ownership y Responsables
- **Owner de este documento**: Tech Lead / DevOps Lead
- **Revisores**: Todo el equipo de desarrollo
- **Aprobadores de cambios**: CTO + Tech Lead (para cambios en producción)

---

## Troubleshooting

### ¿Qué hacer si...?

**Un host no funciona después de deployment:**
1. Verificar que el host está registrado en esta tabla
2. Verificar que existe `config/hosts/[hostname].conf`
3. Verificar que el puerto no está en uso: `lsof -i :[puerto]`
4. Verificar que el servicio systemd está activo: `systemctl status odoo-[cliente]`
5. Revisar logs: `/var/log/odoo/[cliente].log`

**Un puerto está en conflicto:**
1. Consultar tabla de registro de puertos
2. Cambiar puerto en archivo de configuración
3. Actualizar este documento
4. Reiniciar servicio

**No sé desde qué rama hacer deployment:**
1. Consultar columna "Rama Deploy" en tabla de hosts
2. Si el entorno es producción → siempre `main`
3. Si es test → `test`
4. Si es demo → `demo`
5. Si es interno → `blink`

**Necesito agregar un nuevo entorno para cliente existente (ej. staging):**
1. Duplicar configuración de test
2. Modificar hostname: `[cliente]-staging.somosblink.com`
3. Asignar nuevo puerto
4. Crear nueva base de datos: `[cliente]-staging`
5. Actualizar tabla en este documento
6. Seguir proceso de alta

---

## Referencias y Enlaces

- **Documentación de Arquitectura**: [`docs/architecture.md`](./architecture.md)
- **Guía de Deployment**: [`docs/deployment-guide.md`](./deployment-guide.md)
- **Configuraciones Base**: [`config/README.md`](../config/README.md)
- **Scripts de Deployment**: [`deployment/`](../deployment/)

---

## Historial de Cambios

| Fecha | Cambio | Autor | Ticket |
|-------|--------|-------|--------|
| 2026-01-20 | Creación inicial del documento | Sistema | - |
| 2026-01-20 | Agregado host corteperfecto.somosblink.com (prod) | - | - |
| 2026-01-20 | Agregado host corteperfecto-test.somosblink.com (test) | - | - |

---

**Nota**: Este documento es la fuente de verdad para la arquitectura multi-cliente. Mantenlo actualizado religiosamente.
