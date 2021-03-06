{
    'name': 'Accounts user interface customisation for House Affairs Nigeria Limited',
    'summary': 'Custom user interface features.',
    'description': """
        -Hides fields that are not needed in journal entry lines
        -Automatically post journal entries""",
    'category': 'Account',
    'author': 'Tahir Aduragba',
    'depends': ['account'],
    'data': [
        'views/account_views.xml',
    ],
}

#TODO add confirmation wizard before automatically posting