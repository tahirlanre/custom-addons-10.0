# -*- coding: utf-8 -*-
# © 2017 SITAYS (sitasyslimited@gmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Financial Report Xlsx',
    'version': '10.0.1.0.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'description': """This module adds Xls export to account financial reports""",
    'author': 'Tahir Aduragba',
    'depends': ['account','report_xlsx'],
    'data': [
        'wizard/account_financial_report_wizard.xml',
        'reports.xml',
    ],
    'installable': True,
}

