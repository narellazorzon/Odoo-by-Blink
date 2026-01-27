# -*- coding: utf-8 -*-
{
    'name': 'Argentina - Ticket Térmico 80mm',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Localizations/Reporting',
    'summary': 'Reporte adicional de factura en formato ticket 80mm para impresoras térmicas',
    'description': """
        Módulo de localización Argentina - Ticket Térmico
        ==================================================
        
        Este módulo agrega un reporte ADICIONAL para imprimir facturas
        en formato ticket de 80mm para impresoras térmicas.
        
        Características:
        * No modifica reportes existentes
        * No requiere Point of Sale
        * Usa el QR de AFIP existente (l10n_ar_afipws_fe)
        * Fácil de desinstalar sin efectos secundarios
        
        Para usar: Abrir factura → Imprimir → "Ticket 80mm"
    """,
    'author': 'Somos Blink',
    'website': 'https://somosblink.com',
    'depends': [
        'account',
        'l10n_ar',
    ],
    'data': [
        'data/paperformat.xml',
        'report/report_action.xml',
        'report/ticket_template.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'l10n_ar_thermal_ticket/static/src/css/ticket.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
