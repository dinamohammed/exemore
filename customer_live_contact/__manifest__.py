# -*- coding: utf-8 -*-
{
    'name': "Customer Live Contact",

    'summary': """
    Multiple customizations regarding contacting customers using Whatsapp""",

    'description': """
        Contact customers via whatsapp, sms, email when exceeding followup days,
        Multiple changes on Contact's pricelist, Accounts depending upon type,
        Send Notification when product is available in stock.
    """,

    'author': "Egymentors",
    'website': "http://www.egymentors.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','contacts','product','sale_management'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/contact_method_data.xml',
        'views/views.xml',
        'views/res_config_settings_view.xml',
    ],
}
