# -*- coding: utf-8 -*-
# © 2017 SITAYS (tahirlanre@hotmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Cashbook Batch',
    'version': '10.0.1.0.0',
    'description': '',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Account cashbook batches for House Affairs Nigeria Limited',
    'author': 'Tahir Aduragba',
    'depends': ['account'],
    'data': [
        'views/cashbook_batch_view.xml',
        'data/cashbook_batch_data.xml',
        'views/report_cashbook_batch_line.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}

