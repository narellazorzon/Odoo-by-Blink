# -*- coding: utf-8 -*-
from odoo import models, api
import re
import logging

_logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_html(self, report_ref, res_ids=None, data=None):
        """
        Intercepta el HTML para asegurar UTF-8 correcto y corregir doble codificación
        """
        # Llamar al método padre
        if res_ids is None:
            result = super()._render_qweb_html(report_ref, data=data)
        else:
            result = super()._render_qweb_html(report_ref, res_ids, data=data)

        if result and len(result) > 0:
            html_content = result[0]
            was_bytes = isinstance(html_content, bytes)

            # Decodificar si es bytes
            if was_bytes:
                try:
                    html_content = html_content.decode('utf-8')
                except UnicodeDecodeError:
                    # Si falla, intentar con latin-1
                    try:
                        html_content = html_content.decode('latin-1')
                    except:
                        html_content = html_content.decode('utf-8', errors='ignore')

            # Log para debug - buscar palabra Condición
            if 'Condici' in html_content or 'IVA' in html_content:
                # Buscar el fragmento que contiene "Condición"
                import re
                matches = re.findall(r'.{0,30}Condici.{0,30}', html_content)
                if matches:
                    _logger.warning("=== ANTES DE CORRECCIONES ===")
                    for match in matches[:3]:  # Solo primeros 3 matches
                        _logger.warning(f"Texto encontrado: {repr(match)}")
                        _logger.warning(f"Bytes: {[hex(ord(c)) for c in match]}")

            # Corregir doble codificacion usando secuencias de escape
            corrections = {
                # Vocales con tilde minusculas
                '\xc3\xb3': chr(0xF3),  # o con tilde
                '\xc3\xa1': chr(0xE1),  # a con tilde
                '\xc3\xa9': chr(0xE9),  # e con tilde
                '\xc3\xad': chr(0xED),  # i con tilde
                '\xc3\xba': chr(0xFA),  # u con tilde
                '\xc3\xb1': chr(0xF1),  # n con tilde
                # Vocales con tilde mayusculas
                '\xc3\x93': chr(0xD3),  # O con tilde
                '\xc3\x81': chr(0xC1),  # A con tilde
                '\xc3\x89': chr(0xC9),  # E con tilde
                '\xc3\x8d': chr(0xCD),  # I con tilde
                '\xc3\x9a': chr(0xDA),  # U con tilde
                '\xc3\x91': chr(0xD1),  # N con tilde
                # Caracteres problematicos
                '\xc2': '',  # Eliminar este caracter
            }

            corrections_applied = 0
            for bad, good in corrections.items():
                count = html_content.count(bad)
                if count > 0:
                    _logger.warning(f"Reemplazando {repr(bad)} -> {repr(good)} ({count} veces)")
                    html_content = html_content.replace(bad, good)
                    corrections_applied += count

            _logger.warning(f"Total de correcciones aplicadas: {corrections_applied}")

            # NO convertir a entidades HTML, dejar caracteres UTF-8 nativos
            _logger.warning("Manteniendo caracteres UTF-8 nativos (sin entidades HTML)")

            # Log después de todas las correcciones
            if 'Condici' in html_content or 'IVA' in html_content:
                matches = re.findall(r'.{0,30}Condici.{0,30}', html_content)
                if matches:
                    _logger.warning("=== DESPUÉS DE CORRECCIONES ===")
                    for match in matches[:3]:
                        _logger.warning(f"Texto final: {repr(match)}")

            # Asegurar charset UTF-8 en el head
            if '<meta charset' not in html_content.lower():
                html_content = html_content.replace(
                    '<head>',
                    '<head>\n    <meta charset="UTF-8">\n    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">',
                    1
                )
            else:
                # Reemplazar cualquier charset existente por UTF-8
                html_content = re.sub(
                    r'<meta\s+charset=["\']?[^"\'>]+["\']?\s*/?>',
                    '<meta charset="UTF-8">',
                    html_content,
                    flags=re.IGNORECASE,
                    count=1
                )

            # Agregar encoding explícito en el tag html si no existe
            if '<html' in html_content and 'lang=' not in html_content[:500]:
                html_content = re.sub(
                    r'<html([^>]*)>',
                    r'<html\1 lang="es" xml:lang="es">',
                    html_content,
                    count=1,
                    flags=re.IGNORECASE
                )


            # Convertir caracteres con acento a entidades HTML NUMERICAS
            # wkhtmltopdf no respeta UTF-8 correctamente, pero sí las entidades numéricas
            import html
            # Convertir todos los caracteres > 127 a entidades numéricas
            html_content_entities = ''
            for char in html_content:
                if ord(char) > 127:
                    html_content_entities += f'&#{ord(char)};'
                else:
                    html_content_entities += char

            _logger.warning(f"Convertidos {sum(1 for c in html_content if ord(c) > 127)} caracteres especiales a entidades numéricas")
            html_content_utf8 = html_content_entities

            # Guardar HTML temporalmente para debug DESPUÉS de normalización
            try:
                import tempfile
                import os
                temp_dir = tempfile.gettempdir()
                temp_file = os.path.join(temp_dir, 'odoo_invoice_debug_utf8.html')
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(html_content_utf8 if isinstance(html_content_utf8, str) else html_content_utf8.decode('utf-8'))
                _logger.warning(f"HTML UTF-8 guardado en: {temp_file}")
            except Exception as e:
                _logger.warning(f"Error guardando HTML debug: {e}")

            # Convertir de vuelta a bytes si era bytes originalmente
            if was_bytes:
                # IMPORTANTE: Usar ASCII encoding para que las entidades numéricas
                # se mantengan como texto literal (ej: &#243; no se convierte a ó)
                html_content_utf8 = html_content_utf8.encode('ascii', errors='xmlcharrefreplace')
                _logger.warning("HTML convertido a bytes ASCII con entidades preservadas")
            else:
                _logger.warning("HTML mantenido como string con entidades numéricas")

            result = (html_content_utf8, result[1])

        return result

