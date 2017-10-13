# -*- coding: utf-8 -*-
##############################################################################
#

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
    'name': 'Custom Financial Report for House Affairs Nigeria Limited',
    'summary': """Financial report customisation""",
    'version': '10.0.1.1',
    'description': """
        - Show balances after account reports
        - Show Gross Profit and Net Profit on P&L Report
        - Add excel export
    """,
    'author': 'Tahir Aduragba',
    'category': 'Accounts',
    'depends': ['base', 'account', 'report_xlsx'],
    'license': 'AGPL-3',
    'data': [
        'views/account_financial_report_data.xml',
        'views/report_financial.xml',
        'wizard/account_financial_report_wizard.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,

}

#TODO write format function
#TODO consider signs on reports
#TODO develop addon for House Affairs charts of account