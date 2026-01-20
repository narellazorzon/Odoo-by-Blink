# Configuración de Corte Perfecto

## Información General
- **Cliente**: Corte Perfecto
- **Dominio**: corteperfecto.somosblink.com
- **Versión Odoo**: 18
- **Servidor**: EC2 Ubuntu 24.04.3 LTS
- **IP Pública**: 98.95.14.205
- **IP Privada**: 172.31.65.122

## Acceso SSH
```bash
ssh -i "odoo-ec2-key.pem" ubuntu@98.95.14.205
```

## Configuración de Red
- **Puerto Interno (Odoo)**: 8075
- **Puerto Externo (HTTPS)**: 443
- **Puerto HTTP**: 80 (redirige a HTTPS)
- **Interface Odoo**: 127.0.0.1 (solo localhost)
- **Proxy Mode**: Activado (Nginx como reverse proxy)

## Certificado SSL
- **Proveedor**: Let's Encrypt
- **Certificado**: /etc/letsencrypt/live/corteperfecto.somosblink.com/fullchain.pem
- **Clave Privada**: /etc/letsencrypt/live/corteperfecto.somosblink.com/privkey.pem

## Base de Datos PostgreSQL
- **Nombre de BD**: corteperfecto-test
- **Host**: localhost (conexión via socket Unix)
- **Puerto**: 5432
- **Usuario**: odoo
- **Contraseña**: Odoo2025Testing!
- **Filtro de BD**: ^corteperfecto-.*$
- **Max Connections**: 64

## Configuración Odoo

### Seguridad
- **Admin Password**: 8qg-9USIxNbsOwfkNL1GdGwOfnp7eevg9KVTcmtaNhM

### Performance
- **Workers**: 0 (modo single process)
- **CPU Time Limit**: 600s
- **Real Time Limit**: 1200s
- **Memory Soft Limit**: 2GB
- **Memory Hard Limit**: 2.5GB
- **Request Limit**: 8192
- **Max Cron Threads**: 1

### Rutas de Addons
```
/opt/odoo/custom-addons
/opt/odoo/odoo18/addons
/opt/odoo/custom-addons/odoo-argentina
/opt/odoo/custom-addons/odoo-argentina-ce
/opt/odoo/custom-addons/account-financial-tools
```

### Directorios
- **Odoo Binary**: /opt/odoo/odoo18/odoo-bin
- **Data Directory**: /opt/odoo/.local/share/Odoo-corteperfecto
- **Configuración**: /etc/odoo/odoo-corteperfecto.conf
- **Logs**: /var/log/odoo/odoo-corteperfecto.log
- **Log Level**: info

## Servicios Systemd

### Servicio Principal
- **Nombre**: odoo-corteperfecto.service
- **Usuario**: odoo
- **Comando**: /usr/bin/python3 /opt/odoo/odoo18/odoo-bin -c /etc/odoo/odoo-corteperfecto.conf
- **Restart Policy**: on-failure

### Comandos Útiles
```bash
# Ver estado del servicio
sudo systemctl status odoo-corteperfecto

# Reiniciar servicio
sudo systemctl restart odoo-corteperfecto

# Ver logs en tiempo real
sudo tail -f /var/log/odoo/odoo-corteperfecto.log

# Ver logs de Nginx
sudo tail -f /var/log/nginx/corteperfecto_access.log
sudo tail -f /var/log/nginx/corteperfecto_error.log
```

## Configuración Nginx

### Archivo de Configuración
- **Disponible**: /etc/nginx/sites-available/corteperfecto.somosblink.com
- **Habilitado**: /etc/nginx/sites-enabled/corteperfecto.somosblink.com

### Características
- Redirección HTTP → HTTPS automática
- Cache para assets estáticos (90 días)
- Max body size: 100MB
- Timeouts: 300s
- Compresión habilitada

## Notas de Despliegue

### Actualizar Código
```bash
# Conectar al servidor
ssh -i "odoo-ec2-key.pem" ubuntu@98.95.14.205

# Ir al directorio de custom addons
cd /opt/odoo/custom-addons

# Actualizar código (git pull, copiar archivos, etc.)

# Reiniciar servicio
sudo systemctl restart odoo-corteperfecto
```

### Actualizar Módulos
```bash
# Desde la interfaz web de Odoo
# Apps → Buscar módulo → Actualizar

# O desde línea de comandos
sudo -u odoo /opt/odoo/odoo18/odoo-bin -c /etc/odoo/odoo-corteperfecto.conf -u nombre_modulo -d corteperfecto-test --stop-after-init
```

## Información del Sistema
- **Sistema Operativo**: Ubuntu 24.04.3 LTS
- **Kernel**: 6.14.0-1016-aws
- **Uso de Disco**: ~34% de 28GB
- **Uso de Memoria**: ~69%
- **Actualizaciones Pendientes**: 46 (al 20/01/2026)

## Respaldo y Seguridad
- **Fail2ban**: Configurado (/etc/fail2ban/filter.d/odoo.conf)
- **Logrotate**: Configurado (/etc/logrotate.d/odoo)
- **Firewall**: Configuración a verificar

---
*Última actualización: 20 de Enero 2026*
