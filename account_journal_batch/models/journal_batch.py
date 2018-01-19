# -*- coding: utf-8 -*-
# © 2017 SITASYS (Tahir <tahirlanre@hotmail.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import float_compare, float_is_zero

class account_journal_batch(models.Model):
    _name = 'account.journal.batch'
    
    @api.multi
    def _get_default_journal(self):
        misc_journal = self.env['account.journal'].search([('type','=','general')])[0]
        return misc_journal.id
        
    @api.depends('journal_batch_line_ids')
    @api.multi
    def _batch_line_count(self):
        for journal_batch in self:
            line_no = 0
            for line in journal_batch.journal_batch_line_ids:
                line_no += 1
            journal_batch.line_count = line_no
            
    name = fields.Char(string='Batch No',readonly=True, default='Draft')
    date = fields.Datetime(readonly=True,string='Last Processed Date')
    reference = fields.Char(string='Batch Reference', readonly=True)
    description = fields.Char(string='Batch Description')
    clear_batch = fields.Boolean(string='Clear batch after post?',default=False)
    repeat_batch = fields.Boolean(string='Repeat batch?')
    repeat_number = fields.Integer(string='Repeat Batch Count')
    repeat_count = fields.Integer(string='# Posted', default=0)
    transaction_code = fields.Char(string='Transaction Code')           #
    user_id = fields.Many2one('res.users', string='Responsible', required=False, default=lambda self: self.env.user)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, readonly=True, default=_get_default_journal)
    state = fields.Selection([('draft', 'Draft'), ('open', 'Running'), ('close', 'Close')], 'Status', required=True, copy=False, default='draft',
        help="When a prepayment is created, the status is 'Draft'.\n"
            "If the prepayment is confirmed, the status goes in 'Running' and the prepayment lines can be posted in the accounting.\n"
            "You can manually close a prepayment when the prepayment is over. If the last line of prepayment is posted, the prepayment automatically goes in that status.")
    journal_batch_line_ids = fields.One2many('account.journal.batch.line','journal_batch_id', string='Journal Batch Lines', copy=True)
    line_count = fields.Integer(compute='_batch_line_count', string='Lines Per Batch')
    move_ids = fields.Many2one('account.move', string='Journal Batch Entry')
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', store=True, readonly=True,
        default=lambda self: self.env.user.company_id)
    
    @api.onchange("repeat_number")
    def recompute_repeat_count(self):
        for batch in self:
            if not batch.journal_batch_line_ids and batch.repeat_count != 0:
                batch.write({'repeat_count':0})
        
    def clear_batch_lines(self):
        commands = [(2, line_id.id, False) for line_id in self.journal_batch_line_ids]
        self.write({'journal_batch_line_ids': commands})
        
    @api.model
    def create(self,vals):
        journal_batch = super(account_journal_batch,self).create(vals)
        journal_batch.assert_balanced()
        if journal_batch:
            sequence_code = 'account.journal.batch'
            journal_batch.name = self.env['ir.sequence'].next_by_code(sequence_code)

        return journal_batch
        
    @api.multi
    def write(self, vals):
        if 'journal_batch_line_ids' in vals:
            res = super(account_journal_batch, self).write(vals)
            self.assert_balanced()
        else:
            res = super(account_journal_batch, self).write(vals)
        return res
    
    @api.multi
    def post(self):
        for batch in self:
            if batch.repeat_batch:
                if batch.repeat_count > batch.repeat_number:
                    msg = _("You have exceded the number of times to post batch entries.")
                    raise UserError(msg)
                    
            if not self.journal_batch_line_ids:
                msg = _("You can not post a journal batch without lines.")
                raise UserError(msg)
                
            sequence_code = 'account.journal.batch.line'
            batch.reference = self.env['ir.sequence'].next_by_code(sequence_code)
            
            aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
            move = self.env['account.move'].create(self._get_move_vals())

            for line in self.journal_batch_line_ids:
                aml = aml_obj.create(line._get_move_line_vals(move.id))
            
            move.post()
            batch.repeat_count+=1
            batch.write({'date':time.strftime("%Y-%m-%d %H:%M:%S")})
            
            #clear batch lines if clear batch option selected or the last entry has been posted
            if batch.clear_batch or batch.repeat_number == batch.repeat_count:
                self.clear_batch_lines()
            
    def _get_move_vals(self, journal=None):
        """ Return dict to create the payment move
        """
        journal = journal or self.journal_id
        if not journal.sequence_id:
            raise UserError(_('Configuration Error !'), _('The journal %s does not have a sequence, please specify one.') % journal.name)
        if not journal.sequence_id.active:
            raise UserError(_('Configuration Error !'), _('The sequence of journal %s is deactivated.') % journal.name)
        name = journal.sequence_id.next_by_id()
        return {
            'name': name,
            'date': self.journal_batch_line_ids[0].date,
            'ref': self.reference or '',
            'company_id': self.company_id.id,
            'journal_id': journal.id,
            #'batch_line_id': self.id,
        }
        
    @api.multi
    def assert_balanced(self):
        if not self.ids:
            return True
        prec = self.env['decimal.precision'].precision_get('Account')

        self._cr.execute("""\
            SELECT      journal_batch_id
            FROM        account_journal_batch_line
            WHERE       journal_batch_id in %s
            GROUP BY    journal_batch_id
            HAVING      abs(sum(debit) - sum(credit)) > %s
            """, (tuple(self.ids), 10 ** (-max(5, prec))))
        if len(self._cr.fetchall()) != 0:
            raise UserError(_("Cannot create unbalanced journal batch entry."))
        return True
        
    @api.multi
    def unlink(self):
        for journal_batch in self:
            #if journal_batch.state in ['open', 'close']:
            #    raise UserError(_('You cannot delete a document is in %s state.') % (journal_batch.state,))
            if not journal_batch.journal_batch_line_ids and journal_batch.repeat_count == 0:
                raise UserError(_('You cannot delete a document that contains lines or has not finished running.'))
        return super(account_journal_batch, self).unlink()
    
    
class account_journal_batch_line(models.Model):
    _name = 'account.journal.batch.line'
    
    journal_batch_id = fields.Many2one('account.journal.batch', string='Journal Batch')
    move_line_id = fields.Many2one('account.move', string='Journal Batch Line Entry')
    date = fields.Date(required=True, default=lambda self: self._context.get('date', fields.Date.context_today(self)))
    account_id = fields.Many2one('account.account',required=True,string='Account', domain=[('deprecated', '=', False)])
    reference = fields.Char('Reference')
    description = fields.Char('Description')
    debit = fields.Float('Debit')
    credit = fields.Float('Credit')
    journal_id = fields.Many2one('account.journal', related='journal_batch_id.journal_id', string='Journal',
        index=True, store=True, copy=False)  # related is required
    
    _sql_constraints = [
        ('credit_debit1', 'CHECK (credit*debit=0)', 'Wrong credit or debit value in accounting entry !'),
        ('credit_debit2', 'CHECK (credit+debit>=0)', 'Wrong credit or debit value in accounting entry !'),
    ]
        
    def _get_move_line_vals(self, move_id):
        return {
            'move_id': move_id,
            'debit': self.debit,
            'credit': self.credit,
            'name': self.journal_batch_id.description + " / " + (self.description or ''),
            'account_id': self.account_id.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.journal_batch_id.currency_id != self.journal_batch_id.company_id.currency_id and self.journal_batch_id.currency_id.id or False,
        }
        
    @api.multi
    def unlink(self):
        for record in self:
            if record.move_line_id:
                msg = _("You cannot delete posted journal batch entries.")
                raise UserError(msg)
        return super(account_journal_batch_line, self).unlink()
    
    