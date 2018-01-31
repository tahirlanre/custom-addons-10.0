# -*- coding: utf-8 -*-
# © 2017 SITAYS (tahirlanre@hotmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Inventory Valuation',
    'version': '10.0.1.0.0',
    'category': 'Warehouse',
    'license': 'AGPL-3',
    'summary': 'Stock inventory valuation in PDF and Excel',
    'author': 'Tahir Aduragba',
    'depends': ['stock_account','report_xlsx'],
    'data': [
        'views/inventory_valuation.xml',
        'wizard/inventory_valuation_wizard.xml',
    ],
    'installable': True,
}

# TODO create options on wizard not to show zero balances