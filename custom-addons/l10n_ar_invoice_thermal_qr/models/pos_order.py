# -*- coding: utf-8 -*-
from odoo import models
import logging

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def action_pos_order_invoice(self):
        """
        Override para que las facturas del POS usen el reporte térmico
        """
        # Llamar al método original para crear la factura
        result = super().action_pos_order_invoice()
        
        # Obtener las facturas creadas
        invoices = self.mapped('account_move')
        
        if invoices:
            _logger.info(f"Facturas creadas desde POS: {invoices.mapped('name')}")
            
            # Generar y retornar el reporte térmico
            thermal_report = self.env.ref(
                'l10n_ar_invoice_thermal_qr.action_report_invoice_thermal_80mm',
                raise_if_not_found=False
            )
            
            if thermal_report:
                _logger.info("Generando reporte térmico para facturas del POS")
                return thermal_report.report_action(invoices)
        
        return result
