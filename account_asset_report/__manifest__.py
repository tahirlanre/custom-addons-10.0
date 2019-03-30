# -*- coding: utf-8 -*-
{
    'name': "Asset Register Report",

    'summary': """
        A report to show details of assets on the asset register
        """,

    'description': """
    """,

    'author': "SITASYS",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','report_xlsx', 'account_asset'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        'reports.xml',
        'wizard/asset_report_wizard.xml',
        'report/templates/asset_register.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}