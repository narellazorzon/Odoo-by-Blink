# Configuraciones de Odoo by Blink

Este directorio contiene todas las configuraciones de Odoo organizadas por host y entorno.

## Estructura

```
config/
├── base.conf                    # Configuración base compartida
├── templates/                   # Templates para nuevos clientes
│   ├── production.template.conf
│   └── test.template.conf
├── hosts/                       # Configuraciones por host (específicas)
│   ├── corteperfecto-test.somosblink.com.conf
│   ├── corteperfecto.somosblink.com.conf
│   ├── demo.somosblink.com.conf
│   ├── blink.somosblink.com.conf
│   └── localhost.conf
└── README.md                    # Este archivo
```

## Cómo funciona

### Herencia de Configuración

Todas las configuraciones específicas heredan de `base.conf`:

```ini
[options]
extends = ../base.conf
# ... configuración específica sobrescribe valores de base
```

Esto permite:
- Mantener configuración común en un solo lugar
- Sobrescribir solo lo necesario por cliente
- Facilitar actualizaciones globales

### Archivos por Host

Cada archivo en `hosts/` corresponde a un hostname/entorno específico:

| Archivo | Host | Entorno | Cliente |
|---------|------|---------|---------|
| `corteperfecto.somosblink.com.conf` | corteperfecto.somosblink.com | Producción | Corte Perfecto |
| `corteperfecto-test.somosblink.com.conf` | corteperfecto-test.somosblink.com | Test | Corte Perfecto |
| `localhost.conf` | localhost | Desarrollo | N/A |

## Agregar Nuevo Cliente

### Opción 1: Usar Template (Recomendado)

1. **Copiar template correspondiente:**
   ```bash
   # Para producción
   cp config/templates/production.template.conf config/hosts/nuevocliente.somosblink.com.conf

   # Para test
   cp config/templates/test.template.conf config/hosts/nuevocliente-test.somosblink.com.conf
   ```

2. **Editar archivo y completar valores:**
   - Buscar todos los `<COMPLETAR>` en el archivo
   - Reemplazar con valores reales del cliente
   - Generar contraseña de admin: `openssl rand -base64 32`

3. **Validar configuración:**
   ```bash
   # Verificar sintaxis
   python3 odoo18/odoo-bin -c config/hosts/nuevocliente.somosblink.com.conf --test-enable --stop-after-init
   ```

4. **Actualizar documentación:**
   - Agregar entrada en `docs/host-environment-map.md`
   - Crear `docs/clients/nuevocliente.md`

### Opción 2: Script Automatizado

```bash
./scripts/setup_new_client.sh nuevocliente production
```

Este script:
- Crea archivo de configuración desde template
- Solicita valores necesarios interactivamente
- Genera contraseñas seguras automáticamente
- Actualiza documentación
- Crea estructura de directorios necesaria

## Valores Importantes por Entorno

### Producción
- `workers`: Configurar según CPUs disponibles `(num_cpus * 2) + 1`
- `admin_passwd`: Contraseña fuerte única (32+ caracteres)
- `list_db`: `False` (ocultar lista de bases de datos)
- `log_level`: `info` (o `warn` para menos verbosidad)
- `db_filter`: Restrictivo `^cliente-prod$`

### Test/Staging
- `workers`: `0` (single process para debugging) o similar a prod para testing realista
- `admin_passwd`: Puede ser compartida en equipo (pero robusta)
- `list_db`: `True` (permitir ver bases de datos)
- `log_level`: `info` o `debug` según necesidad
- `db_filter`: Menos restrictivo `^cliente-.*$`

### Desarrollo Local
- `workers`: `0` (siempre single process)
- `admin_passwd`: Simple como `admin`
- `list_db`: `True`
- `log_level`: `debug`
- `http_interface`: `0.0.0.0` (accesible desde red local)
- Sin `db_filter` (permitir múltiples bases)

## Seguridad

### Archivos que DEBEN estar en Git
- ✅ `base.conf` (sin secretos)
- ✅ `templates/*.conf` (sin secretos)
- ✅ `README.md`

### Archivos que NO DEBEN estar en Git (si contienen secretos)
- ❌ Archivos con contraseñas reales en texto plano
- ❌ Archivos con tokens o API keys
- ❌ Archivos con datos sensibles de clientes

### Mejores Prácticas
1. **Usar variables de entorno para secretos:**
   ```ini
   [options]
   db_password = ${DB_PASSWORD}
   admin_passwd = ${ADMIN_PASSWORD}
   ```

2. **Usar herramientas de gestión de secretos:**
   - AWS Secrets Manager
   - HashiCorp Vault
   - Ansible Vault
   - dotenv files (fuera de Git)

3. **Para este proyecto:**
   - Archivos de configuración están en Git porque son entornos de test
   - Para producción real, considerar externalizar credenciales
   - Agregar `.gitignore` entry: `config/hosts/*.production.conf`

## Validación de Configuración

### Verificar Sintaxis
```bash
python3 odoo18/odoo-bin -c config/hosts/[archivo].conf --test-enable --stop-after-init
```

### Verificar Herencia
```bash
# Ver configuración final con valores heredados
python3 -c "
import configparser
cfg = configparser.ConfigParser()
cfg.read('config/hosts/corteperfecto-test.somosblink.com.conf')
for section in cfg.sections():
    print(f'[{section}]')
    for key, val in cfg.items(section):
        print(f'{key} = {val}')
"
```

### Script de Auditoría
```bash
# Verificar que todos los archivos de config tienen los valores requeridos
./scripts/audit_configs.py
```

## Troubleshooting

### Odoo no inicia con la configuración

1. **Verificar sintaxis del archivo:**
   ```bash
   python3 odoo18/odoo-bin -c config/hosts/[archivo].conf --test-enable --stop-after-init
   ```

2. **Verificar que base.conf existe:**
   ```bash
   ls -la config/base.conf
   ```

3. **Verificar ruta del extends:**
   - Debe ser relativa al archivo que hereda
   - Formato: `extends = ../base.conf`

4. **Verificar permisos:**
   ```bash
   ls -la config/hosts/[archivo].conf
   # Debe ser legible por usuario que ejecuta Odoo
   ```

### Puerto en uso

```bash
# Ver qué proceso usa el puerto
lsof -i :8075
# o en Windows
netstat -ano | findstr :8075

# Cambiar puerto en config
# http_port = 8076
```

### Base de datos no se conecta

1. Verificar que PostgreSQL está corriendo
2. Verificar credenciales en config
3. Verificar que base de datos existe:
   ```bash
   psql -U odoo -l
   ```

## Referencias

- **Mapa de hosts**: `docs/host-environment-map.md`
- **Documentación de clientes**: `docs/clients/`
- **Scripts de deployment**: `deployment/`
- **Documentación oficial de Odoo**: https://www.odoo.com/documentation/18.0/administration/install.html

---

**Última actualización**: 2026-01-20
