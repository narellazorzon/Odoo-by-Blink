# -*- coding: utf-8 -*-
from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    thermal_electronic_invoice = fields.Boolean(
        string='Factura Electrónica Térmica',
        default=False,
        help='Habilita el toggle de factura electrónica en el POS. '
             'Cuando está activo, el cajero puede elegir si emitir '
             'factura electrónica AFIP (con ticket térmico) o vender sin factura.'
    )
    afip_invoice_journal_id = fields.Many2one(
        'account.journal',
        string='Diario Factura AFIP',
        domain=[('type', '=', 'sale')],
        help='Diario de venta con punto de venta AFIP configurado. '
             'Se usa cuando el cajero activa la factura electrónica.'
    )
