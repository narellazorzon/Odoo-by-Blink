{
    'name': 'Blink AR Fixes',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Fixes for Argentina localization invoice reports',
    'depends': ['account', 'l10n_ar'],
    'data': [
        'views/report_invoice_inherit.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
