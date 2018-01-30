# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright © 2017 Sitasys Limited.
#    Copyright (C) 2004-2015 OpenERP S.A. (<http://www.odoo.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "Custom Partner Account Code Generator",
    'version': '1.0',
    'summary': """
        Unique account code for Customers and Suppliers.""",

    'description': """
        This module generates unique account code for Customers and Suppliers According to customers/Suppliers name as Prefix.
        Included Sequence Code for Customer and Suppliers.
        
        Credits to Techspawn Solutions (custom_customer_vendor_id_generator)
    """,

    'author': "Tahir Aduragba",
    'website': "",
    'category': 'Others',
    'version': '1',
    'depends': ['base'],
    'data': [
        'data/res_partner_sequence.xml',
        'views/res_partner_view.xml',
        'views/res_company_view.xml',
    ],

}