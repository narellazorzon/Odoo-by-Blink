# -*- coding: utf-8 -*-
{
    'name': 'Blink - POS Recibo AFIP (CAE/QR)',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Muestra CAE y QR de AFIP en el recibo en pantalla del POS',
    'author': 'Somos Blink',
    'depends': [
        'point_of_sale',
        'blink_pos_thermal_invoice',
        'l10n_ar_invoice_thermal_qr',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'blink_pos_receipt_afip/static/src/js/pos_order_afip.js',
            'blink_pos_receipt_afip/static/src/js/payment_screen_afip.js',
            'blink_pos_receipt_afip/static/src/xml/order_receipt_afip.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
