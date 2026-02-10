# -*- coding: utf-8 -*-
{
    "name": "Product Label Jewelry",
    "version": "18.0.1.0.0",
    "category": "Inventory",
    "summary": "Etiquetas de joyeria tipo banderita para impresoras termicas",
    "description": """
        Agrega formato de etiqueta para joyeria (65mm x 10mm) 
        tipo banderita para anillos.
        Imprime codigo y precio duplicado en dos bloques.
    """,
    "author": "Blink",
    "website": "https://somosblink.com",
    "license": "LGPL-3",
    "depends": ["product", "stock"],
    "data": [
        "report/product_label_reports.xml",
        "report/product_label_templates.xml",
    ],
    "assets": {
        "web.report_assets_common": [
            "blink_product_label_jewelry/static/src/scss/report_label_jewelry.scss",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
