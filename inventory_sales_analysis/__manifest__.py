# -*- coding: utf-8 -*-
# © 2017 SITAYS (tahirlanre@hotmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Inventory Sales Analysis',
    'version': '10.0.1.0.0',
    'category': 'Warehouse',
    'license': 'AGPL-3',
    'summary': '',
    'author': 'Tahir Aduragba',
    'depends': ['account','stock_account','partner_sales_rep'],
    'data': [
        'report/templates/inventory_sales_analysis.xml',
        'wizard/inventory_sales_analysis_wizard.xml',
        'reports.xml',
    ],
    'installable': True,
}

