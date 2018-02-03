# -*- coding: utf-8 -*-
{
    'name': 'Custom OCA QWeb Financial Reports',
    'description': 'Custom OCA QWeb Financial Reports for House Affairs Nigeria Limited',
    'author': 'Tahir Aduragba',
    'summary': """
        - Show account balance in credit/debit side in OCA Trial Balance report
        - Hide Odoo reports menu that are provided by OCA QWeb Financial Reports module
        - Hide unnecessary columns on General Ledger
    """,
    'version': '10.0.1.0.0',
    'category': 'Accounting & Finance',
    'depends': ['base','account_financial_report_qweb'],
    'data': [
        'templates/trial_balance.xml',
        'templates/general_ledger.xml',
        'templates/layouts.xml',
    ],
}
