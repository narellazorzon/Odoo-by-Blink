# -*- coding: utf-8 -*-
{
    'name': 'Blink - POS Factura Electrónica Térmica',
    'version': '18.0.1.2.0',
    'category': 'Point of Sale',
    'summary': 'Toggle de factura electrónica AFIP en POS con impresión térmica 80mm',
    'description': """
        Agrega un toggle en la pantalla de pago del POS para controlar
        si se emite factura electrónica AFIP o se vende "en negro".

        - Toggle ON: Factura electrónica → AFIP (CAE) → Ticket térmico 80mm
        - Toggle OFF: Sin factura → Recibo POS estándar

        Usa el template térmico de l10n_ar_thermal_ticket para la impresión.
    """,
    'author': 'Somos Blink',
    'website': 'https://somosblink.com',
    'depends': [
        'point_of_sale',
        'l10n_ar_thermal_ticket',
        'l10n_ar_afipws_fe',
    ],
    'data': [
        'data/report_data.xml',
        'views/pos_config_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'blink_pos_thermal_invoice/static/src/js/pos_electronic_toggle.js',
            'blink_pos_thermal_invoice/static/src/xml/pos_electronic_toggle.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
