# -*- coding: utf-8 -*-
{
    'name': "Product Barcode",

    'summary': """
        Product Barcode to be generated automatically""",

    'description': """
        Product Barcode to be generated automatically according to multiple critrea
        depending upon client's needs.
    """,

    'author': "Egymentors",
    'website': "http://www.egymentors.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','res_partner','purchase','sale_management'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'data/product_attributes.xml',
    ],
}
