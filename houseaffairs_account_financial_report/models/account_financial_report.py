# -*- coding: utf-8 -*-

import time
from odoo import api, models,fields


class account_financial_report(models.AbstractModel):
    _inherit = 'account.financial.report'
    
    def test(self):
        pass
        
    type = fields.Selection([
        ('sum', 'View'),
        ('pre_sum', 'Pre-View'),
        ('accounts', 'Accounts'),
        ('account_type', 'Account Type'),
        ('account_report', 'Report Value'),
        ], 'Type', default='sum')
        
    