# -*- coding: utf-8 -*-

{
    'name': 'Account Invoice Margin',
    'description': """
    This module adds the 'Margin' on Account Invoice.
    =============================================

    This gives the profitability by calculating the difference between the Unit
    Price and Cost Price.
    """,
    'author': 'Tahir Aduragba',
    'depends': ['account'],
    'data': [
        'views/invoice_margin_view.xml',
    ],

}
