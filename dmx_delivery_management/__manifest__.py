# -*- coding: utf-8 -*-
{
    'name': "DMX Logistics Delivery Management System",

    'summary': """
        custom app to manage deliveries for DMX Logisitics
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "SITASYS",
    'website': "",
    'application': True,

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Extra Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/delivery_management_menu.xml',
        'views/templates.xml',
        'data/data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}