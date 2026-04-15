# -*- coding: utf-8 -*-
from odoo import models, api
import logging
import pytz

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

        # Fecha/hora de la orden en timezone del usuario
        invoice_datetime = False
        if order.date_order:
            try:
                user_tz = self.env.user.tz or 'UTC'
                tz = pytz.timezone(user_tz)
                local_dt = pytz.utc.localize(order.date_order).astimezone(tz)
                invoice_datetime = local_dt.strftime('%d/%m/%Y %H:%M')
            except Exception:
                invoice_datetime = order.date_order.strftime('%d/%m/%Y %H:%M')

        # Datos del cliente
        partner = move.partner_id
        partner_name = partner.name if partner else False
        partner_vat = partner.vat if partner else False
        partner_afip_responsibility = (
            partner.l10n_ar_afip_responsibility_type_id.name
            if partner and partner.l10n_ar_afip_responsibility_type_id
            else False
        )
        address_parts = [p for p in [
            partner.street if partner else None,
            partner.city if partner else None,
        ] if p]
        partner_address = ', '.join(address_parts) if address_parts else False

        result = {
            'afip_auth_code': move.afip_auth_code,
            'afip_auth_mode': move.afip_auth_mode,
            'afip_auth_code_due': move.afip_auth_code_due.strftime('%d/%m/%Y') if move.afip_auth_code_due else False,
            'afip_qr_code': move.afip_qr_code.decode('utf-8') if move.afip_qr_code and isinstance(move.afip_qr_code, bytes) else move.afip_qr_code or False,
            'document_number': move.name or False,
            'invoice_datetime': invoice_datetime,
            'partner_name': partner_name,
            'partner_vat': partner_vat,
            'partner_afip_responsibility': partner_afip_responsibility,
            'partner_address': partner_address,
        }

        _logger.info(
            'AFIP receipt data for POS order %s: CAE=%s, doc=%s',
            order.name, result['afip_auth_code'], result['document_number'],
        )

        return result
