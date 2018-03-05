# -*- coding: utf-8 -*-
# © 2018 SITAYS (sitasysnigeria@gmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Document Management System KW-AG',
    'version': '10.0.1.0.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Document mangement system for Kwara State Accountant General Office',
    'description':"""
        - Manage payment voucher upload
        - Manage release letter upload
    
        Credits to https://renjie.me
    """
    ,
    'author': 'Tahir Aduragba',
    'depends': ['document','swr_datepicker','mail'],
    'data': [
        'views/document_views.xml',
        'views/document_menu.xml',
        'views/res_partner_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

