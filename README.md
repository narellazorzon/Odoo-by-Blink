# Odoo by Blink

**Plataforma multi-cliente basada en Odoo 18 con arquitectura de configuración por HOST**

---

## Descripción

Odoo by Blink es una solución empresarial multi-tenant que permite gestionar múltiples clientes desde un único codebase de Odoo 18, utilizando un sistema de configuración por hostname que facilita el deployment, mantenimiento y escalabilidad.

### Características Principales

- Un solo codebase para todos los clientes
- Configuración específica por host/entorno
- Deployment automatizado
- Módulos custom para localización Argentina
- Arquitectura escalable y mantenible
- Separación clara entre código y configuración

---

## Estructura del Proyecto

```
Odoo-by-Blink/
├── config/                      # Configuraciones por host
│   ├── base.conf                # Config base compartida
│   ├── templates/               # Templates para nuevos clientes
│   └── hosts/                   # Configs específicas por hostname
│
├── custom-addons/               # Módulos custom de Blink
│   ├── blink_invoice_layout/   # Diseño profesional de facturas AR
│   ├── blink_ar_fixes/         # Fixes para localización Argentina
│   └── ...
│
├── deployment/                  # Scripts de deployment
│   ├── deploy.py               # Script principal de deployment
│   └── ...
│
├── docs/                        # Documentación
│   ├── architecture.md         # Arquitectura del sistema
│   ├── host-environment-map.md # Mapa de hosts y entornos
│   └── clients/                # Documentación por cliente
│
├── scripts/                     # Scripts de utilidad
│   └── ...
│
├── odoo18/                      # Core de Odoo 18
│
├── .gitignore
└── README.md                    # Este archivo
```

---

## Quick Start

### Requisitos Previos

- Python 3.11+
- PostgreSQL 14+
- Git
- Sistema operativo: Ubuntu 20.04+ / macOS / Windows con WSL

### Instalación Local

1. **Clonar repositorio**:
   ```bash
   git clone https://github.com/narellazorzon/Odoo-by-Blink.git
   cd Odoo-by-Blink
   ```

2. **Instalar dependencias de Odoo**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install -y python3-pip python3-dev libxml2-dev libxslt1-dev \
       zlib1g-dev libsasl2-dev libldap2-dev build-essential libssl-dev libffi-dev \
       libmysqlclient-dev libjpeg-dev libpq-dev libjpeg8-dev liblcms2-dev \
       libblas-dev libatlas-base-dev npm

   # Instalar dependencias Python
   pip3 install -r odoo18/requirements.txt
   ```

3. **Configurar PostgreSQL**:
   ```bash
   sudo -u postgres createuser -s $USER
   createdb odoo-dev
   ```

4. **Configurar archivo de configuración local**:
   ```bash
   # El archivo localhost.conf ya está listo para usar
   # Ajustar rutas si es necesario
   vim config/hosts/localhost.conf
   ```

5. **Ejecutar Odoo**:
   ```bash
   python3 odoo18/odoo-bin -c config/hosts/localhost.conf --dev=all
   ```

6. **Acceder**:
   - Abrir navegador en: http://localhost:8069
   - Master password: `admin` (ver `config/hosts/localhost.conf`)
   - Crear base de datos desde la interfaz

---

## Gestión de Clientes

### Hosts y Entornos Actuales

| Host | Cliente | Entorno | Rama | Base de Datos |
|------|---------|---------|------|---------------|
| corteperfecto.somosblink.com | Corte Perfecto | Producción | main | corteperfecto-prod |
| corteperfecto-test.somosblink.com | Corte Perfecto | Test | test | corteperfecto-test |
| demo.somosblink.com | Blink | Demo | demo | demo-showcase |
| blink.somosblink.com | Blink | Internal | blink | blink-internal |
| localhost | Desarrollo | Local | dev | odoo-dev |

Ver documentación completa en [`docs/host-environment-map.md`](docs/host-environment-map.md)

### Agregar Nuevo Cliente

```bash
# 1. Copiar template de configuración
cp config/templates/production.template.conf config/hosts/nuevocliente.somosblink.com.conf

# 2. Editar y completar valores
vim config/hosts/nuevocliente.somosblink.com.conf
# Buscar y reemplazar todos los <COMPLETAR>

# 3. Crear documentación del cliente
cp docs/clients/template.md docs/clients/nuevocliente.md
vim docs/clients/nuevocliente.md

# 4. Actualizar mapa de hosts
vim docs/host-environment-map.md

# 5. Hacer deployment
./deployment/deploy.py --host nuevocliente.somosblink.com --branch main --update-modules
```

Ver guía completa en [`docs/deployment-guide.md`](docs/deployment-guide.md)

---

## Ramas y Flujo de Trabajo

### Ramas Principales

- **`main`** - Código de producción estable, protegida
- **`test`** - Código en testing pre-producción
- **`blink`** - Desarrollo interno de Blink
- **`demo`** - Código para demos comerciales
- **`dev`** - Desarrollo activo

### Flujo de Desarrollo

```mermaid
graph LR
    A[feature/*] -->|PR| B[dev]
    B -->|PR + Tests| C[test]
    C -->|UAT OK| D[main]
    D -->|Deploy| E[Production]
```

**Proceso**:
1. Crear feature branch desde `dev`
2. Desarrollar y hacer commits
3. Pull Request a `dev` (requiere 1 revisor)
4. Merge a `test` para UAT
5. Merge a `main` cuando esté aprobado (requiere 2 revisores + cliente)
6. Deployment automático a producción

---

## Deployment

### Deployment Manual

```bash
# Producción
./deployment/deploy.py --host corteperfecto.somosblink.com --branch main --notify

# Test
./deployment/deploy.py --host corteperfecto-test.somosblink.com --branch test --auto

# Demo con reset de BD
./deployment/deploy.py --host demo.somosblink.com --branch demo --reset-db
```

### Opciones del Script de Deployment

```bash
./deployment/deploy.py --help

Opciones:
  --host HOSTNAME          Hostname del entorno (requerido)
  --branch BRANCH          Rama de Git para deployment (requerido)
  --auto                   Modo automático sin confirmaciones
  --force                  Forzar aunque haya cambios sin commitear
  --skip-validations       Omitir validaciones y health checks
  --update-modules         Actualizar módulos de Odoo
  --reset-db               Reset base de datos (CUIDADO!)
  --notify                 Enviar notificaciones de deployment
```

---

## Módulos Custom

### Módulos Disponibles

#### blink_invoice_layout
Diseño profesional de facturas para localización Argentina.

**Características**:
- Layout moderno y profesional
- Soporte para QR de AFIP
- Customizable por cliente
- Compatible con facturas A, B, C

**Instalación**:
- Incluido en `addons_path` por defecto
- Instalar desde Apps en Odoo

#### blink_ar_fixes
Correcciones y mejoras para la localización Argentina.

**Características**:
- Fixes de bugs conocidos en l10n_ar
- Mejoras de performance
- Validaciones adicionales

#### l10n_ar_invoice_thermal_qr
QR codes para impresoras térmicas con facturas electrónicas.

**Características**:
- Generación de QR AFIP
- Compatible con impresoras térmicas
- Integración con punto de venta

### Desarrollo de Nuevos Módulos

```bash
# Crear estructura de módulo
cd custom-addons
mkdir mi_nuevo_modulo
cd mi_nuevo_modulo

# Crear archivos base
touch __init__.py __manifest__.py
mkdir models views

# Seguir estructura estándar de Odoo
# Ver: https://www.odoo.com/documentation/18.0/developer/howtos.html
```

---

## Configuración

### Sistema de Configuración

Todas las instancias heredan de `config/base.conf` y sobrescriben valores específicos:

```ini
# config/hosts/ejemplo.somosblink.com.conf
[options]
extends = ../base.conf

hostname = ejemplo.somosblink.com
environment = production
db_name = ejemplo-prod
http_port = 8075
admin_passwd = <password-fuerte>
```

### Valores Importantes

| Configuración | Producción | Test | Local |
|---------------|------------|------|-------|
| `workers` | (CPUs * 2) + 1 | 0 | 0 |
| `list_db` | False | True | True |
| `log_level` | info | info/debug | debug |
| `proxy_mode` | True | True | False |

Ver documentación completa en [`config/README.md`](config/README.md)

---

## Documentación

### Documentos Principales

- **[Arquitectura](docs/architecture.md)** - Visión general de la arquitectura del sistema
- **[Mapa de Hosts](docs/host-environment-map.md)** - Mapeo de hosts, entornos y configuraciones
- **[Guía de Deployment](docs/deployment-guide.md)** - Proceso completo de deployment
- **[Configuraciones](config/README.md)** - Sistema de configuración por host

### Documentación por Cliente

- [Corte Perfecto](docs/clients/corteperfecto.md)

---

## Seguridad

### Buenas Prácticas Implementadas

- Secrets no están en Git (usar variables de entorno)
- SSH con autenticación por keys
- Firewall configurado (UFW)
- Fail2ban activo
- SSL/TLS obligatorio en producción
- Odoo en modo proxy (solo localhost)
- Contraseñas de admin fuertes y únicas

### Reportar Vulnerabilidades

Si encuentras una vulnerabilidad de seguridad, por favor NO la reportes públicamente. Contacta directamente al equipo de desarrollo.

---

## Troubleshooting

### Problemas Comunes

**Odoo no inicia**:
```bash
# Verificar logs
tail -f /var/log/odoo/odoo-[cliente].log

# Verificar servicio
sudo systemctl status odoo-[cliente]

# Reiniciar servicio
sudo systemctl restart odoo-[cliente]
```

**Puerto en uso**:
```bash
# Ver qué proceso usa el puerto
lsof -i :8075

# Cambiar puerto en config
vim config/hosts/[hostname].conf
# Modificar: http_port = 8076
```

**Base de datos no conecta**:
```bash
# Verificar que PostgreSQL está corriendo
sudo systemctl status postgresql

# Verificar que base de datos existe
psql -U odoo -l

# Verificar credenciales en config
vim config/hosts/[hostname].conf
```

**Módulo no se actualiza**:
```bash
# Actualizar módulo específico
sudo -u odoo /opt/odoo/odoo18/odoo-bin \
    -c /etc/odoo/odoo-[cliente].conf \
    -u nombre_modulo \
    -d nombre_bd \
    --stop-after-init

# Reiniciar servicio
sudo systemctl restart odoo-[cliente]
```

---

## Contribuir

### Proceso de Contribución

1. Fork el repositorio
2. Crear feature branch (`git checkout -b feature/mi-feature`)
3. Hacer commits con mensajes descriptivos
4. Push al branch (`git push origin feature/mi-feature`)
5. Crear Pull Request

### Estándares de Código

- Seguir [PEP 8](https://pep8.org/) para Python
- Usar nombres descriptivos para variables y funciones
- Documentar funciones complejas
- Escribir commits siguiendo [Conventional Commits](https://www.conventionalcommits.org/)

### Code Review

Todos los PRs requieren:
- Al menos 1 revisor para merge a `dev`
- Al menos 1 revisor senior para merge a `test`
- Al menos 2 revisores + aprobación de cliente para merge a `main`

---

## Soporte

### Canales de Soporte

- **Documentación**: Revisar carpeta `docs/`
- **Issues**: GitHub Issues para reportar bugs o solicitar features
- **Email**: [contacto de soporte]
- **Slack/Discord**: [canal de la comunidad]

### Recursos Externos

- [Documentación Oficial de Odoo 18](https://www.odoo.com/documentation/18.0/)
- [Odoo Community Forums](https://www.odoo.com/forum)
- [Odoo GitHub](https://github.com/odoo/odoo)

---

## Licencia

Este proyecto utiliza Odoo Community Edition (LGPL v3).

Módulos custom desarrollados por Blink: [Especificar licencia]

---

## Equipo

**Mantenido por**: Equipo de Desarrollo Blink

**Contributors**:
- [Listar contributors principales]

---

## Changelog

Ver [CHANGELOG.md](CHANGELOG.md) para historial de cambios.

---

**Última actualización**: 2026-01-20
**Versión**: 1.0
