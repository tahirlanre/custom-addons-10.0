# -*- coding: utf-8 -*-
{
    'name': 'House Affairs Custom Access Controls',
    'description': 'Access controls and security features',
    'author': 'Tahir Aduragba',
    'depends': ['sale','account','account_cancel'],
    'data': [
        'security/houseaffairs_security.xml',
        'security/ir.model.access.csv',
        'views/salesman_views.xml',
        'views/account_invoice.xml',
        'views/account_move.xml',
    ],
}
