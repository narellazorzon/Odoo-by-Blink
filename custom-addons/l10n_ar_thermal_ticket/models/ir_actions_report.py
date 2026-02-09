# -*- coding: utf-8 -*-
from odoo import models, api
import logging

_logger = logging.getLogger(__name__)
_logger.info('=== l10n_ar_thermal_ticket ir_actions_report.py CARGADO ===')


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    TICKET_REPORT_NAME = 'l10n_ar_thermal_ticket.report_ticket_80mm'

    # Altura base: header + doc + cliente + totales + CAE + QR + footer + separadores
    # Cada línea de producto: nombre + detalle + subtotal + margen
    TICKET_BASE_HEIGHT = 118
    TICKET_LINE_HEIGHT = 10

    @api.model
    def _build_wkhtmltopdf_args(
            self,
            paperformat_id,
            landscape,
            specific_paperformat_args=None,
            set_viewport_size=False):
        """Override para altura dinámica en ticket térmico."""

        command_args = super()._build_wkhtmltopdf_args(
            paperformat_id, landscape,
            specific_paperformat_args, set_viewport_size
        )

        _logger.info('=== THERMAL_TICKET DEBUG ===')
        _logger.info('specific_paperformat_args: %s', specific_paperformat_args)
        _logger.info('paperformat: %s (height=%s, width=%s)',
                     paperformat_id.name if paperformat_id else None,
                     paperformat_id.page_height if paperformat_id else None,
                     paperformat_id.page_width if paperformat_id else None)

        # Detectar si es nuestro paperformat por el nombre o dimensiones
        is_thermal = False
        if paperformat_id and paperformat_id.name == 'Ticket Térmico 80mm':
            is_thermal = True
        elif paperformat_id and paperformat_id.page_width == 80:
            is_thermal = True

        if is_thermal:
            _logger.info('THERMAL_TICKET: Detectado paperformat de ticket térmico')

            # Obtener altura desde specific_paperformat_args si existe
            custom_height = None
            if specific_paperformat_args:
                custom_height = specific_paperformat_args.get('thermal_ticket_height')

            if custom_height:
                _logger.info('THERMAL_TICKET: Usando altura personalizada: %smm', custom_height)
                # Reemplazar --page-height
                new_args = []
                skip_next = False
                for arg in command_args:
                    if skip_next:
                        skip_next = False
                        continue
                    if arg == '--page-height':
                        skip_next = True
                        continue
                    new_args.append(arg)
                new_args.extend(['--page-height', f'{custom_height}mm'])
                _logger.info('THERMAL_TICKET: Comando final: %s', ' '.join(new_args[-10:]))
                return new_args

        return command_args

    def _run_wkhtmltopdf(
            self,
            bodies,
            report_ref=False,
            header=None,
            footer=None,
            landscape=False,
            specific_paperformat_args=None,
            set_viewport_size=False):
        """Override para calcular e inyectar altura dinámica."""

        _logger.info('=== THERMAL_TICKET _run_wkhtmltopdf ===')
        _logger.info('report_ref: %s', report_ref)

        if report_ref:
            report_sudo = self._get_report(report_ref)
            _logger.info('report_name: %s', report_sudo.report_name)

            if report_sudo.report_name == self.TICKET_REPORT_NAME:
                _logger.info('THERMAL_TICKET: Es nuestro reporte!')

                # Calcular altura basada en el contenido HTML
                # Contar cuántos bodies hay (cada body es una factura)
                num_bodies = len(bodies) if bodies else 1

                # Estimar líneas desde el HTML (buscar divs de línea de producto)
                total_lines = 0
                for body in bodies:
                    # Contar ocurrencias de 'ticket-line' en el HTML
                    total_lines += body.count('ticket-line')

                if total_lines == 0:
                    total_lines = 5  # Default mínimo

                # Calcular altura
                height = self.TICKET_BASE_HEIGHT + (total_lines * self.TICKET_LINE_HEIGHT)
                _logger.info('THERMAL_TICKET: %d líneas detectadas -> altura %dmm', total_lines, height)

                # Inyectar en specific_paperformat_args
                if specific_paperformat_args is None:
                    specific_paperformat_args = {}
                else:
                    specific_paperformat_args = dict(specific_paperformat_args)
                specific_paperformat_args['thermal_ticket_height'] = height

        return super()._run_wkhtmltopdf(
            bodies,
            report_ref=report_ref,
            header=header,
            footer=footer,
            landscape=landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size
        )
