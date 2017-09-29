# -*- coding: utf-8 -*-
{
    'name': 'House Affairs Custom Access Controls',
    'description': '',
    'author': 'Tahir Aduragba',
    'depends': ['base','sale','account'],
    'data': [
        'security/houseaffairs_security.xml',
        'security/ir.model.access.csv',
        'views/salesman_views.xml',
        'views/account_views.xml',
    ],
}
