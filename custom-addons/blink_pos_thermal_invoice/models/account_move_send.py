# -*- coding: utf-8 -*-
from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class AccountMoveSend(models.AbstractModel):
    _inherit = 'account.move.send'

    @api.model
    def _get_default_pdf_report_id(self, move):
        """Override para usar el reporte térmico 80mm cuando la factura viene del POS."""
        # Si la factura viene de un POS con factura electrónica térmica habilitada
        if move.pos_order_ids:
            pos_order = move.pos_order_ids[0]
            if (pos_order.config_id.thermal_electronic_invoice
                    and pos_order.is_electronic_invoice):
                thermal_report = self.env.ref(
                    'l10n_ar_thermal_ticket.action_report_ticket_80mm',
                    raise_if_not_found=False,
                )
                if thermal_report:
                    _logger.info(
                        'BLINK_THERMAL: Factura %s del POS -> reporte térmico (id=%s)',
                        move.name, thermal_report.id,
                    )
                    return thermal_report

        result = super()._get_default_pdf_report_id(move)
        _logger.info(
            'BLINK_THERMAL: Factura %s (pos_orders=%s) -> reporte %s (id=%s)',
            move.name, bool(move.pos_order_ids), result.report_name, result.id,
        )
        return result
