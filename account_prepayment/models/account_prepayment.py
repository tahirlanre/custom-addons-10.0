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
    account_prepayment_id = fields.Many2one('account.account', string='Prepayment Account', required = True, domain=[('deprecated', '=', False)], help="Account used to record the amount of the prepayment to be made")
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
    month_number = fields.Integer(string='Number of Months', default=12, required=True, readonly=True, states={'draft': [('readonly', False)]}, help="The number of months needed to post prepayment entries")
    value_residual = fields.Float(compute='_amount_residual', method=True, digits=0, string='Residual Value')
    month_residual = fields.Integer(compute='_month_residual', method=True, digits=0, string='Months Remaining')
    type = fields.Selection([('income', 'Prepaid Income'), ('expense', 'Prepaid Expense')], required=True, index=True, default='expense')
    date = fields.Date(string='Date', required=True, readonly=True, states={'draft': [('readonly', False)]}, default=fields.Date.context_today)
    value_monthly = fields.Float(string='Monthly amount', compute='_amount_monthly', digits=0, method=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True, states={'draft': [('readonly', False)]},
        default=lambda self: self.env.user.company_id.currency_id.id)
    initial_move_id = fields.Many2one('account.move', string='Intial Prepayment Entry')
    
    @api.multi
    @api.depends('prepayment_line_ids.move_id')
    def _entry_count(self):
        for prepayment in self:
            res = self.env['account.prepayment.line'].search_count([('prepayment_id', '=', prepayment.id), ('move_id', '!=', False)])
            prepayment.entry_count = res or 0
    
    @api.one
    @api.depends('value', 'prepayment_line_ids.move_check', 'prepayment_line_ids.amount')
    def _amount_residual(self):
        total_amount = 0.0
        for line in self.prepayment_line_ids:
            if line.move_check:
                total_amount += line.amount
        self.value_residual = self.value - total_amount
        
    def compute_prepayment_line_amount(self, sequence, month_number, residual_amount):
        amount = 0
        if sequence == month_number:
            amount = residual_amount
        else:
            amount = self.value_monthly
        return amount
          
    @api.multi
    def compute_prepayment_lines(self):
        self.ensure_one()
        posted_prepayment_line_ids = self.prepayment_line_ids.filtered(lambda x: x.move_check).sorted(key=lambda l: l.prepayment_date)
        unposted_prepayment_line_ids = self.prepayment_line_ids.filtered(lambda x: not x.move_check)
        
        commands = [(2, line_id.id, False) for line_id in unposted_prepayment_line_ids]
        
        if self.entry_count == 0:
            #amount_to_post = self.value_monthly
            residual_amount = self.value_residual
            prepayment_date = datetime.strptime(self.date[:7] + '-01', DF).date()
            
            day = prepayment_date.day
            month = prepayment_date.month
            year = prepayment_date.year
            total_days = (year % 4) and 365 or 366
            undone_month_number = self.month_number
            
            for x in range(len(posted_prepayment_line_ids), undone_month_number):
                sequence = x + 1
                amount = self.compute_prepayment_line_amount(sequence,undone_month_number,residual_amount)
                amount = self.currency_id.round(amount)
                if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                    continue
                residual_amount -= amount
                vals = {
                    'amount': amount,
                    'prepayment_id': self.id,
                    'sequence': sequence,
                    'name': (self.code or '') + '/' + str(sequence),
                    'remaining_value': residual_amount,
                    'prepayment_value': (self.value - residual_amount),
                    'prepayment_date': prepayment_date.strftime(DF),
                }
                commands.append((0, False, vals))
                
                prepayment_date = date(year, month, day) + relativedelta(months=+1)
                day = prepayment_date.day
                month = prepayment_date.month
                year = prepayment_date.year            
        self.write({'prepayment_line_ids': commands})
            
        return True
            
    @api.one
    @api.depends('month_number', 'entry_count')
    def _month_residual(self):
        self.month_residual = self.month_number - self.entry_count
        
    @api.multi
    def validate(self):
        self.write({'state':'open'})
        for prepayment in self:
            if self.state == 'open' and not self.initial_move_id:
                self.create_initial_move()
        
    @api.depends('value', 'month_number')
    def _amount_monthly(self):
        for prepayment in self:
            prepayment.value_monthly = prepayment.value / prepayment.month_number
    
    @api.multi
    def create_initial_move(self):
        created_moves = self.env['account.move']
        prec = self.env['decimal.precision'].precision_get('Account')
        for prepayment in self:
            start_date = prepayment.date or fields.Date.context_today(self)
            amount = prepayment.value
            prepayment_name = self.name
            if self.type == 'expense':
                move_line_1 = {
                    'name': prepayment_name,
                    'account_id': prepayment.account_prepayment_expense_id.id,
                    'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                    'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                    'journal_id': self.journal_id.id,
                }
                move_line_2 = {
                    'name': prepayment_name,
                    'account_id': prepayment.account_prepayment_id.id,
                    'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                    'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                    'journal_id': self.journal_id.id,
                }
                move_vals={
                    'ref': prepayment.code,
                    'date': start_date or False,
                    'journal_id': self.journal_id.id,
                    'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
                }
                move = self.env['account.move'].create(move_vals)
                move.post()
                prepayment.write({'initial_move_id':move.id})
                created_moves |= move
        return [x.id for x in created_moves]
                
    @api.model
    def create(self, vals):
        prepayment = super(AccountPrepayment,self).create(vals)
        prepayment.compute_prepayment_lines()
        return prepayment
        
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
    
    name = fields.Char(string='Depreciation Name', required=True, index=True)
    amount = fields.Float(string='Current Depreciation', digits=0, required=True)
    move_id = fields.Many2one('account.move', string='Prepayment Entry')
    move_check = fields.Boolean(compute='_get_move_check', string='Linked', track_visibility='always', store=True)
    move_posted_check = fields.Boolean(compute='_get_move_posted_check', string='Posted', track_visibility='always', store=True)
    prepayment_id = fields.Many2one('account.prepayment', string='Prepayment',required=True, ondelete='cascade')
    prepayment_value = fields.Float(string='Cumulative Prepayment Entry', required=True)
    prepayment_date = fields.Date('Prepayment Date', index=True)
    remaining_value = fields.Float(string='Next Period Prepayment', digits=0, required=True)
    sequence = fields.Integer(required=True)
    parent_state = fields.Selection(related='prepayment_id.state', string='State of Prepayment')
    
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
    def create_move(self):
        print 'Post entry for prepayment line'      
        
    @api.multi
    def unlink(self):
        for record in self:
            if record.move_check:
                msg = _("You cannot delete posted depreciation lines.")
                raise UserError(msg)
        return super(AccountPrepaymentLine, self).unlink()