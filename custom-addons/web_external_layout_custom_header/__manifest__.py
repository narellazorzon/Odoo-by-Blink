{
    'name': 'External Layout Custom Header Support',
    'version': '18.0.1.0.0',
    'category': 'Web',
    'summary': 'Adds support for custom_header and custom_footer in external_layout_standard',
    'description': """
        Extends external_layout_standard to check for custom_header and custom_footer variables.
        If these variables are set (e.g., by localization modules like l10n_ar), they will be 
        rendered instead of the standard header/footer. This maintains backward compatibility
        while allowing localizations to meet legal requirements.
    """,
    'depends': ['web'],
    'data': [
        'views/report_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,  # Auto-install when web is installed
    'license': 'LGPL-3',
}
