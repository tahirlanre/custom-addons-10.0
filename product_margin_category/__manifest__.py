# -*- coding: utf-8 -*-
##############################################################################
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
    'name': 'Margins by Product Category',
    'summary': """Margins by product with category filter""",
    'version': '10.0.1.0',
    'description': """
        -   Display margins of products based on selected category range
        -   Display margins of products only sold within period selected
    """,
    'author': 'Tahir Aduragba',
    'company': 'SITASYS Limited',
    'website': '',
    'category': 'Sales',
    'depends': ['account','product_margin','sale_margin'],
    'license': 'AGPL-3',
    'data': [
        'views/product_product.xml',
        'wizard/product_margin.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,

}



