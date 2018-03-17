# -*- coding: utf-8 -*-
# © 2017 SITAYS (tahirlanre@hotmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Inventory Transaction',
    'version': '10.0.1.0.0',
    'category': 'Warehouse',
    'license': 'AGPL-3',
    'summary': '',
    'author': 'Tahir Aduragba',
    'depends': ['stock_account','partner_sales_rep','account_invoice_margin'],
    'data': [
       'report.xml',
       'report/templates/inventory_transaction.xml',
       'wizard/inventory_transaction_wizard.xml',
       'data/inventory.transaction.type.csv',
       'security/ir.model.access.csv'
    ],
    'installable': True,
}

