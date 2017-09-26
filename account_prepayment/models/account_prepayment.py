# -*- coding: utf-8 -*-
# © 2017 SITASYS (Tahir <tahirlanre@hotmail.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import float_compare, float_is_zero


class AccountPrepayment(models.Model):
    _name = "account.prepayment"
    _description = 'Prepaid Expense/Income'
    
    name = fields.Char(string='Details', required=True, index=True)
    active = fields.Boolean(default=True)
    account_prepayment_id = fields.Many2one('account.account', string='Prepayment Account', required = True, domain=[('internal_type','=','other'), ('deprecated', '=', False)], help="Account used to record the amount of the prepayment to be made")
    account_prepayment_expense_id = fields.Many2one('account.account', string='Prepayment: Expense Account', required = True, domain=[('internal_type','=','other'), ('deprecated', '=', False)], help="Account used in the prepayment entries, used to record the expense value")
    #account_prepayment_income_id = fields.Many2one('account.account', string='Prepayment: Income Account', required = True, domain=[('internal_type','=','other'), ('deprecated', '=', False)], help="Account used in prepayment entries, to record the income values")
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, readonly=True, states={'draft': [('readonly', False)]})
    code = fields.Char(string='Reference', size=32, readonly=True, states={'draft': [('readonly', False)]})
    value = fields.Float(string='Gross Value', required=True, readonly=True, digits=0, states={'draft': [('readonly', False)]})
    entry_count = fields.Integer(compute='_entry_count', string='# Posted')
    prepayment_line_ids = fields.One2many('account.prepayment.line', 'prepayment_id',string='Prepayment Lines', readonly=True, states={'draft': [('readonly', False)], 'open': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('open', 'Running'), ('close', 'Close')], 'Status', required=True, copy=False, default='draft',
        help="When a prepayment is created, the status is 'Draft'.\n"
            "If the prepayment is confirmed, the status goes in 'Running' and the prepayment lines can be posted in the accounting.\n"
            "You can manually close a prepayment when the prepayment is over. If the last line of prepayment is posted, the prepayment automatically goes in that status.")
    entry_number = fields.Integer(string='Number of Prepayment Entries', default=12, help="The number of prepayment entries needed to record")
    value_residual = fields.Float(compute='_amount_residual', method=True, digits=0, string='Residual Value')
    type = fields.Selection([('income', 'Prepaid Income'), ('expense', 'Prepaid Expense')], required=True, index=True, default='expense')
    date = fields.Date(string='Date', required=True, readonly=True, states={'draft': [('readonly', False)]}, default=fields.Date.context_today)
    value_monthly = fields.Float(string='Monthly amount', compute='_amount_monthly', digits=0, method=True)
    
    @api.multi
    @api.depends('prepayment_line_ids.move_id')
    def _entry_count(self):
        pass
    
    @api.one
    @api.depends('value', 'prepayment_line_ids.move_check', 'prepayment_line_ids.amount')
    def _amount_residual(self):
        total_amount = 0.0
        for line in self.prepayment_line_ids:
            if line.move_check:
                total_amount += line.amount
        self.value_residual = self.value - total_amount
    
    @api.multi
    def validate(self):
        self.write({'state':'open'})
        
    @api.depends('value', 'entry_number')
    def _amount_monthly(self):
        for prepayment in self:
            prepayment.value_monthly = prepayment.value / prepayment.entry_number
    
    @api.multi
    def unlink(self):
        for prepayment in self:
            if prepayment.state in ['open', 'close']:
                raise UserError(_('You cannot delete a document is in %s state.') % (prepayment.state,))
            for prepayment_line in prepayment.prepayment_line_ids:
                if prepayment_line.move_id:
                    raise UserError(_('You cannot delete a document that contains posted entries.'))
        return super(AccountPrepayment, self).unlink()
           
class AccountPrepaymentLine(models.Model):
    _name = "account.prepayment.line"
    
    amount = fields.Float(string='Current Depreciation', digits=0, required=True)
    move_id = fields.Many2one('account.move', string='Prepayment Entry')
    move_check = fields.Boolean(compute='_get_move_check', string='Linked', track_visibility='always', store=True)
    move_posted_check = fields.Boolean(compute='_get_move_posted_check', string='Posted', track_visibility='always', store=True)
    prepayment_id = fields.Many2one('account.prepayment', string='Prepayment',required=True, ondelete='cascade')
    
    @api.multi
    @api.depends('move_id')
    def _get_move_check(self):
        for line in self:
            line.move_check = bool(line.move_id)
            
    @api.multi
    @api.depends('move_id.state')
    def _get_move_posted_check(self):
        for line in self:
            line.move_posted_check = True if line.move_id and line.move_id.state == 'posted' else False
            
    @api.multi
    def unlink(self):
        for record in self:
            if record.move_check:
                msg = _("You cannot delete posted depreciation lines.")
                raise UserError(msg)
        return super(AccountPrepaymentLine, self).unlink()