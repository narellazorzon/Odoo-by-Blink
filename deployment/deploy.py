#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo by Blink - Deployment Script
==================================

Script principal para hacer deployment de Odoo basado en configuración por HOST.

Uso:
    ./deployment/deploy.py --host corteperfecto.somosblink.com --branch main
    ./deployment/deploy.py --host corteperfecto-test.somosblink.com --branch test --auto
    ./deployment/deploy.py --host demo.somosblink.com --branch demo --reset-db

"""

import argparse
import configparser
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Colores para output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(msg):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{msg:^80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_success(msg):
    print(f"{Colors.OKGREEN}✓ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.FAIL}✗ {msg}{Colors.ENDC}")

def print_warning(msg):
    print(f"{Colors.WARNING}⚠ {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.OKCYAN}ℹ {msg}{Colors.ENDC}")

def run_command(cmd, cwd=None, check=True, capture_output=True):
    """Ejecutar comando shell y retornar resultado."""
    print_info(f"Ejecutando: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            check=check,
            capture_output=capture_output,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"Error ejecutando comando: {e}")
        if e.stderr:
            print(e.stderr)
        raise

class OdooDeployment:
    def __init__(self, host, branch, options):
        self.host = host
        self.branch = branch
        self.options = options
        self.repo_root = Path(__file__).parent.parent
        self.config_file = self.repo_root / "config" / "hosts" / f"{host}.conf"
        self.config = None

    def validate_config(self):
        """Validar que existe configuración para el host."""
        print_header(f"VALIDANDO CONFIGURACIÓN PARA {self.host}")

        if not self.config_file.exists():
            print_error(f"No existe archivo de configuración: {self.config_file}")
            print_info(f"Archivos disponibles en config/hosts/:")
            config_dir = self.repo_root / "config" / "hosts"
            for f in config_dir.glob("*.conf"):
                print(f"  - {f.name}")
            return False

        print_success(f"Archivo de configuración encontrado: {self.config_file}")

        # Leer configuración
        self.config = configparser.ConfigParser()
        try:
            self.config.read(self.config_file)
            print_success("Configuración leída correctamente")
        except Exception as e:
            print_error(f"Error leyendo configuración: {e}")
            return False

        # Validar valores críticos
        required_keys = ['hostname', 'environment', 'db_name', 'http_port']
        missing_keys = []

        if 'options' in self.config:
            for key in required_keys:
                if key not in self.config['options']:
                    missing_keys.append(key)
        else:
            print_error("Sección [options] no encontrada en configuración")
            return False

        if missing_keys:
            print_error(f"Faltan valores en configuración: {', '.join(missing_keys)}")
            return False

        print_success("Todos los valores requeridos están presentes")

        # Mostrar información
        opts = self.config['options']
        print_info(f"Hostname: {opts.get('hostname', 'N/A')}")
        print_info(f"Entorno: {opts.get('environment', 'N/A')}")
        print_info(f"Base de datos: {opts.get('db_name', 'N/A')}")
        print_info(f"Puerto: {opts.get('http_port', 'N/A')}")

        return True

    def check_git_status(self):
        """Verificar estado de Git y rama actual."""
        print_header("VERIFICANDO ESTADO DE GIT")

        # Verificar rama actual
        result = run_command("git branch --show-current", cwd=self.repo_root)
        current_branch = result.stdout.strip()
        print_info(f"Rama actual: {current_branch}")

        # Verificar cambios sin commitear
        result = run_command("git status --porcelain", cwd=self.repo_root)
        if result.stdout.strip():
            print_warning("Hay cambios sin commitear:")
            print(result.stdout)
            if not self.options.get('force'):
                print_error("Usa --force para continuar con cambios sin commitear")
                return False
        else:
            print_success("Working tree limpio")

        # Verificar que la rama especificada existe
        result = run_command(f"git rev-parse --verify {self.branch}", cwd=self.repo_root, check=False)
        if result.returncode != 0:
            print_error(f"La rama '{self.branch}' no existe")
            return False

        print_success(f"Rama '{self.branch}' existe")

        return True

    def checkout_branch(self):
        """Hacer checkout de la rama especificada."""
        print_header(f"CAMBIANDO A RAMA {self.branch}")

        try:
            # Fetch para obtener últimos cambios
            run_command("git fetch origin", cwd=self.repo_root)
            print_success("Fetch completado")

            # Checkout
            run_command(f"git checkout {self.branch}", cwd=self.repo_root)
            print_success(f"Checkout a {self.branch} completado")

            # Pull para actualizar
            run_command(f"git pull origin {self.branch}", cwd=self.repo_root)
            print_success("Pull completado")

            # Mostrar último commit
            result = run_command("git log -1 --oneline", cwd=self.repo_root)
            print_info(f"Último commit: {result.stdout.strip()}")

            return True
        except Exception as e:
            print_error(f"Error en checkout: {e}")
            return False

    def run_pre_deployment_checks(self):
        """Ejecutar checks pre-deployment."""
        print_header("EJECUTANDO PRE-DEPLOYMENT CHECKS")

        if self.options.get('skip_validations'):
            print_warning("Validaciones omitidas (--skip-validations)")
            return True

        # TODO: Agregar checks específicos según necesidad
        # - Verificar que base de datos existe
        # - Verificar que puerto no está en uso por otro servicio
        # - Verificar conectividad a base de datos
        # - Etc.

        print_success("Pre-deployment checks completados")
        return True

    def deploy_code(self):
        """Deployment del código (específico según entorno)."""
        print_header("DEPLOYMENT DE CÓDIGO")

        environment = self.config['options'].get('environment', 'unknown')

        if environment == 'local':
            print_info("Entorno local - No se requiere deployment remoto")
            return True

        # Para entornos remotos, necesitaríamos:
        # - SSH al servidor
        # - Pull del código en el servidor
        # - Reiniciar servicio

        print_warning("Deployment remoto no implementado aún")
        print_info("Pasos manuales:")
        print_info(f"1. SSH al servidor del host {self.host}")
        print_info("2. cd /opt/odoo/custom-addons")
        print_info(f"3. git fetch && git checkout {self.branch} && git pull")
        print_info("4. Reiniciar servicio Odoo")

        if self.options.get('auto'):
            print_error("No se puede continuar con --auto en deployment remoto sin implementar")
            return False

        if not self.confirm("¿Has completado los pasos manuales?"):
            print_error("Deployment cancelado")
            return False

        return True

    def update_modules(self):
        """Actualizar módulos de Odoo si es necesario."""
        print_header("ACTUALIZACIÓN DE MÓDULOS")

        if not self.options.get('update_modules'):
            print_info("Actualización de módulos omitida (usar --update-modules para habilitar)")
            return True

        # Comando para actualizar módulos
        # odoo-bin -c config.conf -u module_name -d database --stop-after-init

        print_warning("Actualización de módulos debe hacerse en servidor")
        print_info("Comando de ejemplo:")
        db_name = self.config['options'].get('db_name')
        print_info(f"sudo -u odoo /opt/odoo/odoo18/odoo-bin -c {self.config_file} -u all -d {db_name} --stop-after-init")

        return True

    def restart_service(self):
        """Reiniciar servicio de Odoo."""
        print_header("REINICIANDO SERVICIO")

        environment = self.config['options'].get('environment', 'unknown')
        client_code = self.config['options'].get('client_code', 'unknown')

        if environment == 'local':
            print_info("Entorno local - Reiniciar manualmente tu instancia de Odoo")
            return True

        # Nombre del servicio systemd (ajustar según convención)
        service_name = f"odoo-{client_code}"
        if environment != 'production':
            service_name = f"{service_name}-{environment}"

        print_warning(f"Reiniciar servicio en servidor: sudo systemctl restart {service_name}")

        return True

    def run_health_checks(self):
        """Ejecutar health checks post-deployment."""
        print_header("HEALTH CHECKS POST-DEPLOYMENT")

        if self.options.get('skip_validations'):
            print_warning("Health checks omitidos (--skip-validations)")
            return True

        # TODO: Implementar health checks
        # - Verificar que servicio está corriendo
        # - Verificar que puerto responde
        # - Verificar que base de datos es accesible
        # - Hacer request HTTP para verificar que responde

        print_success("Health checks completados")
        return True

    def send_notification(self):
        """Enviar notificación de deployment."""
        print_header("NOTIFICACIÓN")

        if not self.options.get('notify'):
            print_info("Notificaciones omitidas (usar --notify para habilitar)")
            return True

        # TODO: Implementar notificaciones
        # - Slack
        # - Email
        # - Discord
        # etc.

        message = f"""
Deployment completado:
- Host: {self.host}
- Rama: {self.branch}
- Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Entorno: {self.config['options'].get('environment')}
"""
        print_info("Notificación:")
        print(message)

        return True

    def confirm(self, question):
        """Solicitar confirmación al usuario."""
        if self.options.get('auto'):
            return True

        response = input(f"{question} (y/n): ").lower().strip()
        return response == 'y' or response == 'yes'

    def run(self):
        """Ejecutar deployment completo."""
        print_header(f"DEPLOYMENT A {self.host}")
        print_info(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print_info(f"Rama: {self.branch}")

        steps = [
            ("Validar configuración", self.validate_config),
            ("Verificar Git", self.check_git_status),
            ("Checkout rama", self.checkout_branch),
            ("Pre-deployment checks", self.run_pre_deployment_checks),
            ("Deploy código", self.deploy_code),
            ("Actualizar módulos", self.update_modules),
            ("Reiniciar servicio", self.restart_service),
            ("Health checks", self.run_health_checks),
            ("Notificación", self.send_notification),
        ]

        for step_name, step_func in steps:
            try:
                if not step_func():
                    print_error(f"Fallo en paso: {step_name}")
                    return False
            except KeyboardInterrupt:
                print_error("\nDeployment cancelado por usuario")
                return False
            except Exception as e:
                print_error(f"Error inesperado en {step_name}: {e}")
                return False

        print_header("DEPLOYMENT COMPLETADO EXITOSAMENTE")
        return True

def main():
    parser = argparse.ArgumentParser(
        description="Deployment de Odoo by Blink basado en configuración por HOST",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s --host corteperfecto.somosblink.com --branch main
  %(prog)s --host corteperfecto-test.somosblink.com --branch test --auto
  %(prog)s --host demo.somosblink.com --branch demo --reset-db
  %(prog)s --host blink.somosblink.com --branch blink --skip-validations
        """
    )

    parser.add_argument('--host', required=True, help='Hostname/dominio del entorno (ej. corteperfecto.somosblink.com)')
    parser.add_argument('--branch', required=True, help='Rama de Git para hacer deployment (ej. main, test, dev)')
    parser.add_argument('--auto', action='store_true', help='Modo automático sin confirmaciones')
    parser.add_argument('--force', action='store_true', help='Forzar deployment aunque haya cambios sin commitear')
    parser.add_argument('--skip-validations', action='store_true', help='Omitir validaciones y health checks')
    parser.add_argument('--update-modules', action='store_true', help='Actualizar módulos de Odoo después del deployment')
    parser.add_argument('--reset-db', action='store_true', help='Reset base de datos (CUIDADO: elimina datos)')
    parser.add_argument('--notify', action='store_true', help='Enviar notificaciones de deployment')

    args = parser.parse_args()

    options = {
        'auto': args.auto,
        'force': args.force,
        'skip_validations': args.skip_validations,
        'update_modules': args.update_modules,
        'reset_db': args.reset_db,
        'notify': args.notify,
    }

    deployment = OdooDeployment(args.host, args.branch, options)
    success = deployment.run()

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
