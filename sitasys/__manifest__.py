# -*- coding: utf-8 -*-
{
    'name': 'SITASYS',
    'description': '',
    'author': 'Tahir Aduragba',
    'depends': ['base'],
    'data': [
        'views/res_users.xml',
        'views/res_company.xml',
        'security/res_groups.xml',
        'data/res_users.xml',
    ],
}

# TODO restrict no user_root from groups
# TODO check max no of users when reactivating users