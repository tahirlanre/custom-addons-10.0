# -*- coding: utf-8 -*-
# © 2017 SITAYS (tahirlanre@hotmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Journal Batches',
    'version': '10.0.1.0.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Journal batches for House Affairs Nigeria Limited',
    'author': 'Tahir Aduragba',
    'depends': ['account'],
    'data': [
        'views/journal_batch_view.xml',
        'wizard/journal_batch_wizard.xml',
        'security/ir.model.access.csv',
        'data/journal_batch_data.xml',
    ],
    'installable': True,
}

