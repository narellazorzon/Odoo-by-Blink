# -*- coding: utf-8 -*-
from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def get_afip_receipt_data(self, order_ids):
        """Retorna los datos AFIP (CAE, QR) de la factura vinculada a la orden POS.

        Solo devuelve datos si la factura existe y fue autorizada electrónicamente
        (tiene afip_auth_code).

        Args:
            order_ids: lista con un único ID de pos.order

        Returns:
            dict con datos AFIP o None si no aplica
        """
        if not order_ids:
            return None

        order = self.browse(order_ids[0])
        if not order.exists():
            return None

        move = order.account_move
        if not move or not move.afip_auth_code:
            return None

        result = {
            'afip_auth_code': move.afip_auth_code,
            'afip_auth_mode': move.afip_auth_mode,
            'afip_auth_code_due': move.afip_auth_code_due.strftime('%d/%m/%Y') if move.afip_auth_code_due else False,
            'afip_qr_code': move.afip_qr_code.decode('utf-8') if move.afip_qr_code and isinstance(move.afip_qr_code, bytes) else move.afip_qr_code or False,
            'document_number': move.name or False,
        }

        _logger.info(
            'AFIP receipt data for POS order %s: CAE=%s, doc=%s',
            order.name, result['afip_auth_code'], result['document_number'],
        )

        return result
