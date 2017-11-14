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
    'name': 'Sales Usability',
    'summary': """User friendly features""",
    'version': '10.0.1.0',
    'description': """
        - Custom UI improvements
        - Editable name field in Sales Order form
        - Set credit limit for each customer
    """,
    'author': 'Tahir Aduragba',
    'category': 'Sales',
    'depends': ['base', 'sale','report_extended'],
    'license': 'AGPL-3',
    'data': [ 'views/templates.xml',
    'views/sale_order_line_view.xml',
    'views/sale_order_report.xml',
    #'views/reports.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,

}

# TODO show wizard to accept or decline confirmation when customer over credit limit