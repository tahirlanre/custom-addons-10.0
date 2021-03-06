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
            
        self.env.cr.execute("""
              select 
                s.id, s.account_id, s.date, s.debit, s.credit, 
                sum(s.balance) over (partition by s.account_id order by s.row) 
            	from (
                    select 
                        aml.id, row_number() over(order by aml.date, aml.id asc) as row, aml.date, aml.name, 
                        aml.account_id, aml.debit, aml.credit, (aml.debit-aml.credit) AS balance 
                        from account_move_line aml
                        join account_move am on am.id = aml.move_id
                        where am.state = 'posted' and am.date >= %s and am.date <= %s order by aml.date, aml.id asc) s
            """,(date_from, date_to))
            
        result = self.env.cr.fetchall()
        for aml in self:
            for res in result:
                if aml.id == res[0]:
                    aml.cummul_balance = res[5]
        
    cummul_balance = fields.Float(compute="compute_values", digits=dp.get_precision('Account'), string='Running balance')
    partner_reference = fields.Char(string='Code', related = 'partner_id.ref')

class account_account(models.Model):
    _inherit = "account.account"
    
    move_line_ids = fields.One2many('account.move.line','account_id','Journal Entry Lines')
    