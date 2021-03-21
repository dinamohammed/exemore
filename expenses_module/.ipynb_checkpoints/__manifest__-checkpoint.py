# -*- coding: utf-8 -*-
{
    'name': "Expenses Module",

    'summary': """
        Expenses Module ; to create expenses In a seperate Module""",

    'description': """
    """,

    'author': "Egymentors",
    'website': "http://www.egymentors.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting-Expenses',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_accountant'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/expenses_security.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
