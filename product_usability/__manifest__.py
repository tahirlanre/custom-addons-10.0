# -*- coding: utf-8 -*-
##############################################################################
#
#    SITASYS Ltd.
#    Copyright (C) 2017-TODAY SITASYS.
#    Author: Tahir Aduragba
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
    'name': 'Product Usability',
    'summary': """Add code to Product Category""",
    'version': '10.0.1.0',
    'description': """
        - 
    """,
    'author': 'Tahir Aduragba',
    'category': 'Product',
    'depends': ['product'],
    'license': 'AGPL-3',
    'data': [ 'views/product_category.xml',
    'product_category_data.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,

}

# TODO overide name_search & name_get functions for product.category
# TODO Show product price history in product form view