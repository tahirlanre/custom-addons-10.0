# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models

from operator import itemgetter


import odoo.addons.decimal_precision as dp

class Partner(models.Model):
    _inherit = 'res.partner'
    
    @api.one
    @api.depends('debit', 'credit')
    def _get_balance(self):
        for partner in self:
            partner.balance = self.credit - self.debit
            
    @api.model
    def _balance_search(self, operator, operand):
        return self._asset_balance_search(operator, operand)
        
    @api.multi
    def _asset_balance_search(self, operator, operand):
        if operator not in ('<', '=', '>', '>=', '<='):
            return []
        if type(operand) not in (float, int):
            return []
        res = self._cr.execute('''
            SELECT partner.id
            FROM res_partner partner
            LEFT JOIN account_move_line aml ON aml.partner_id = partner.id
            RIGHT JOIN account_account acc ON aml.account_id = acc.id
            WHERE acc.internal_type in ('payable','receivable')
              AND NOT acc.deprecated
            GROUP BY partner.id
            HAVING COALESCE(SUM(aml.amount_residual), 0) ''' + operator + ''' %s''', (operand,))
        res = self._cr.fetchall()
        if not res:
            return [('id', '=', '0')]
        return [('id', 'in', map(itemgetter(0), res))]
            
    balance = fields.Float(
        compute='_get_balance',
        string='Balance', readonly=True,
        digits=dp.get_precision('Account'),
        search='_balance_search' )
        
