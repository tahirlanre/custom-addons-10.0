# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<http://www.cybrosys.com>).
#    Author: Niyas Raphy,Fasluca(<http://www.cybrosys.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Account Bank Statement Usability',
    'summary': """Custom account bank statment features for House Affairs Nigeria Limited""",
    'version': '10.0.1.0',
    'description': """
        - Create payments (outward) in account bank statments and cash transactions
        - Auto validate statement/transaction after saving
        - Custom user interface
    """,
    'author': 'Tahir Aduragba',
    'category': 'Accounting',
    'depends': ['base', 'account'],
    'license': 'AGPL-3',
    'data': [
        'views/account_journal_dashboard_view.xml',
        'views/account_bank_statement_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,

}


#TODO add confirmation wizard before auto validating
