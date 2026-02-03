# -*- coding: utf-8 -*-
from odoo import models, fields, _
import logging

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    is_electronic_invoice = fields.Boolean(
        string='Factura Electrónica',
        default=False,
        help='Indica si esta orden POS debe generar factura electrónica AFIP.'
    )

    def _prepare_invoice_vals(self):
        """Override para usar el diario AFIP cuando es factura electrónica."""
        vals = super()._prepare_invoice_vals()

        if self.is_electronic_invoice and self.config_id.afip_invoice_journal_id:
            vals['journal_id'] = self.config_id.afip_invoice_journal_id.id
            _logger.info(
                'POS Order %s: Usando diario AFIP %s para factura electrónica',
                self.name,
                self.config_id.afip_invoice_journal_id.name,
            )

        return vals
