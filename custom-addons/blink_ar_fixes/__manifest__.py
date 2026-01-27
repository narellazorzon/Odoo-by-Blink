{
    'name': 'Blink AR Fixes',
    'version': '18.0.1.1.0',
    'category': 'Accounting/Localizations',
    'summary': 'Fixes for Argentina localization invoice reports',
    'depends': ['account', 'l10n_ar', 'portal'],
    'data': [
        'views/report_invoice_inherit.xml',
        'views/portal_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
