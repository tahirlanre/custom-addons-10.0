# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class account_move_line(models.Model):
    _inherit = "account.move.line"
    
    @api.multi   
    @api.depends('account_id.move_line_ids')
    def compute_values(self):
        context = dict(self._context or {})
        if context.get('date_from'):
            date_from = context['date_from']
        if context.get('date_to'):
            date_to = context['date_to']
        if context.get('account_id'):
            account_id = context['account_id']
            
        sqlstr = """
              select 
                s.id, s.account_id, s.date, s.debit, s.credit, 
                sum(s.balance) over (partition by s.account_id order by s.row) 
            	from (
                    select 
                        id, row_number() over(order by date, id asc) as row, date, name, 
                        account_id, debit, credit, (debit-credit) AS balance 
                        from account_move_line order by date, id asc) s
            """
        self.env.cr.execute(sqlstr)
        result = self.env.cr.fetchall()
        #import pdb; pdb.set_trace()
        for aml in self:
            for res in result:
                if aml.id == res[0]:
                    aml.cummul_balance = res[5]
        
    cummul_balance = fields.Float(compute="compute_values", digits=dp.get_precision('Account'), string='Running balance')
    partner_reference = fields.Char(string='Code', related = 'partner_id.ref')

class account_account(models.Model):
    _inherit = "account.account"
    
    move_line_ids = fields.One2many('account.move.line','account_id','Journal Entry Lines')
    