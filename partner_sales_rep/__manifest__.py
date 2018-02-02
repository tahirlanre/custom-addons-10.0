# -*- coding: utf-8 -*-
{
    'name': 'Partner Sales Representative',
    'description': 'Assign sales rep to partners',
    'author': 'Tahir Aduragba',
    'category': 'Sales',
    'depends': ['sale'],
    'data': [
        'views/res_partner.xml',
        'views/sales_rep.xml',
        'security/sales_rep_security.xml',
        'security/ir.model.access.csv',
        'data/sales_rep_data.xml',
    ],
}

# TODO  Report to show sales rep sales analysis