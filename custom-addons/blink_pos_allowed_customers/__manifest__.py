{
    'name': 'Blink POS Allowed Customers',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Filter which customers are available in POS',
    'author': 'Blink',
    'depends': ['point_of_sale'],
    'data': [
        'views/res_partner_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'blink_pos_allowed_customers/static/src/**/*',
        ],
    },
    'post_init_hook': '_post_init_hook',
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
