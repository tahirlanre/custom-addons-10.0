# -*- coding: utf-8 -*-
# © 2017 SITAYS (tahirlanre@hotmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Prepayment',
    'version': '10.0.1.0.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Module for account prepayments',
    'author': 'Tahir Aduragba',
    'depends': ['account_accountant'],
    'data': [
        'security/account_prepayment_security.xml',
        'security/ir.model.access.csv',
        'views/account_prepayment.xml',
        'wizard/account_prepayment_wizard.xml',
    ],
    'installable': True,
}


#TODO create prepayment report