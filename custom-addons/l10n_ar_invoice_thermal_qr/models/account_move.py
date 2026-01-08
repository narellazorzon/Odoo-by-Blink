# -*- coding: utf-8 -*-
import json
import base64
import io
import qrcode
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Campo para almacenar la imagen QR
    afip_qr_code = fields.Binary(
        string='Código QR AFIP',
        compute='_compute_afip_qr_code',
        store=True,
        help='Código QR según especificación AFIP RG 4892'
    )

    @api.depends('afip_auth_code', 'afip_auth_mode', 'invoice_date', 'amount_total')
    def _compute_afip_qr_code(self):
        """
        Genera el código QR según especificación oficial de AFIP
        https://www.afip.gob.ar/fe/qr/documentos/QRespecificaciones.pdf
        """
        for rec in self:
            qr_code = False
            
            # Solo generar QR para facturas electrónicas con CAE/CAEA
            if rec.afip_auth_code and rec.afip_auth_mode in ['CAE', 'CAEA']:
                try:
                    # Preparar datos según especificación AFIP
                    qr_data = {
                        'ver': 1,
                        'fecha': rec.invoice_date.strftime('%Y-%m-%d') if rec.invoice_date else '',
                        'cuit': int(rec.company_id.vat or 0),
                        'ptoVta': rec.journal_id.l10n_ar_afip_pos_number or 0,
                        'tipoCmp': int(rec.l10n_latam_document_type_id.code or 0),
                        'nroCmp': int((rec.l10n_latam_document_number or '0').split('-')[-1]),
                        'importe': float(rec.amount_total),
                        'moneda': rec.currency_id.l10n_ar_afip_code or 'PES',
                        'ctz': float(getattr(rec, 'l10n_ar_currency_rate', 1.0)),
                        'tipoCodAut': 'E' if rec.afip_auth_mode == 'CAE' else 'A',
                        'codAut': int(rec.afip_auth_code),
                    }
                    
                    if rec.partner_id.l10n_latam_identification_type_id:
                        qr_data['tipoDocRec'] = int(rec.partner_id.l10n_latam_identification_type_id.l10n_ar_afip_code or 99)
                    if rec.partner_id.vat:
                        qr_data['nroDocRec'] = int(rec.partner_id.vat)
                    
                    json_str = json.dumps(qr_data, separators=(',', ':'))
                    json_bytes = json_str.encode('utf-8')
                    b64_data = base64.b64encode(json_bytes).decode('ascii')
                    qr_url = f"https://www.afip.gob.ar/fe/qr/?p={b64_data}"
                    
                    qr = qrcode.QRCode(
                        version=None,
                        error_correction=qrcode.constants.ERROR_CORRECT_M,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(qr_url)
                    qr.make(fit=True)
                    
                    img = qr.make_image(fill_color="black", back_color="white")
                    buffer = io.BytesIO()
                    img.save(buffer, format='PNG')
                    qr_code = base64.b64encode(buffer.getvalue())
                    
                    _logger.info(f"QR Code generado para factura {rec.name}")
                    
                except Exception as e:
                    _logger.error(f"Error generando QR Code: {str(e)}")
                    qr_code = False
            
            rec.afip_qr_code = qr_code


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    @api.model
    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        """
        Intercepta la generación de reportes para usar el térmico cuando viene del POS
        """
        # Obtener el reporte actual
        report_sudo = self._get_report(report_ref)
        
        # Si es el reporte de facturas estándar
        if report_sudo.report_name in ['account.report_invoice_with_payments', 'account.report_invoice']:
            # Verificar si alguna de las facturas viene del POS
            if res_ids:
                invoices = self.env['account.move'].browse(res_ids)
                if any(inv.pos_order_ids for inv in invoices):
                    # Cambiar al reporte térmico
                    thermal_report = self.env.ref(
                        'l10n_ar_invoice_thermal_qr.action_report_invoice_thermal_80mm',
                        raise_if_not_found=False
                    )
                    if thermal_report:
                        _logger.info(f"Cambiando a reporte térmico para facturas del POS: {invoices.mapped('name')}")
                        report_sudo = thermal_report
        
        # Llamar al método original con el reporte (posiblemente modificado)
        return super(IrActionsReport, report_sudo)._render_qweb_pdf_prepare_streams(report_ref, data, res_ids=res_ids)
