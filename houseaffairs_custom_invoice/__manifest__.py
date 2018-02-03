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
    'name': 'Invoice Report',
    'summary': """Custom Invoice Report for House Affairs Nigeria Limited""",
    'version': '10.0.1.0',
    'description': """""",
    'author': 'Tahir Aduragba',
    'category': 'Accounting',
    'depends': ['sale_usability'],
    'license': 'AGPL-3',
    'data': [
        'views/report_invoice.xml',
        'views/account_invoice.xml',
        'views/res_company_view.xml',
        'data/data.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,

}

#TODO Proforma invoice