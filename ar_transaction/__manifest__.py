# -*- coding: utf-8 -*-
# © 2018 SITAYS (sitasyslimited@gmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'AR Transaction summary',
    'version': '10.0.1.0.0',
    'category': 'Warehouse',
    'license': 'AGPL-3',
    'summary': '',
    'author': 'Tahir Aduragba',
    'depends': ['account'],
    'data': [
       'report.xml',
       'report/templates/ar_transaction.xml',
       'wizard/ar_transaction_wizard.xml',
    ],
    'installable': True,
}

