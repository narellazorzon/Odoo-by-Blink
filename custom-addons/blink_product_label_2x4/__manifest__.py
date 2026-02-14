# -*- coding: utf-8 -*-
{
    'name': 'Product Label 2x4',
    'version': '18.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Etiquetas de producto 2x4 pulgadas para impresoras térmicas',
    'description': '''
        Agrega formato de etiqueta 2x4 pulgadas (51mm x 102mm) 
        para impresoras térmicas como Xprinter XP-470B.
        Similar al formato Dymo pero con tamaño mayor.
    ''',
    'author': 'Blink',
    'website': 'https://somosblink.com',
    'license': 'LGPL-3',
    'depends': ['product', 'stock'],
    'data': [
        'report/product_label_reports.xml',
        'report/product_label_templates.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'blink_product_label_2x4/static/src/scss/report_label_2x4.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
