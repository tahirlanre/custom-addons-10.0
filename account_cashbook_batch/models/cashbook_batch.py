# -*- coding: utf-8 -*-
# © 2017 SITAYS (tahirlanre@hotmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class account_cashbook_batch(models.Model):
    _name = "account.cashbook.batch"
    _description = "Payments"
    _order = "payment_date desc, name desc"
    
    @api.model
    def _default_journal(self):
        journal_type = self.env.context.get('journal_type', False)
        company_id = self.env['res.company']._company_default_get('account.bank.statement').id
        if journal_type:
            journals = self.env['account.journal'].search([('type', '=', journal_type), ('company_id', '=', company_id)])
            if journals:
                return journals[0]
        return self.env['account.journal']
    
    @api.depends('batch_line_ids')
    @api.multi
    def _batch_line_no(self):
        for cashbook in self:
            line_no = 0
            for line in cashbook.batch_line_ids:
                line_no += 1
            cashbook.batch_line_no = line_no
                    
    name = fields.Char(readonly=True, copy=False, default="Draft") # The name is attributed upon post()
    payment_type = fields.Selection([('ar', 'Account Receivable'), ('ap', 'Account Payable'),('gl', 'General Ledger')], string='Payment Type')
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)
    batch_line_no = fields.Integer(compute='_batch_line_no', string='Lines Per Batch')
    batch_line_ids = fields.One2many('account.cashbook.batch.line','batch_id', string='Batch Lines', states={'confirm': [('readonly', True)]}, copy=True)
    #payment_method = fields.Selection([('inbound', 'Inbound'), ('outbound', 'Outbound')], required=True)
    state = fields.Selection([('open', 'New'), ('confirm', 'Posted')], string='Status', required=True, readonly=True, copy=False, default='open')
    move_line_ids = fields.One2many('account.move.line', 'batch_id', string='Entry lines', states={'confirm': [('readonly', True)]})
    user_id = fields.Many2one('res.users', string='Responsible', required=False, default=lambda self: self.env.user)
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, states={'confirm': [('readonly', True)]}, default=_default_journal)
    journal_type = fields.Selection(related='journal_id.type', help="Technical field used for usability purposes")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    
    @api.multi
    def unlink(self):
        for batch in self:
            if batch.state != 'open':
                raise UserError(_('You can not delete a cashbook batch that has been posted.'))
            # Explicitly unlink bank statement lines so it will check that the related journal entries have been deleted first
            batch.batch_line_ids.unlink()
        return super(account_cashbook_batch, self).unlink()
        
    @api.multi
    def button_journal_entries(self):
        return {
            'name': _('Journal Items'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('batch_id', 'in', self.ids)],
        }
    
    @api.multi
    def print_confirmation(self):
        self.ensure_one()
        return self.env['report'].get_action(self, 'account_cashbook_batch.cashbook_batch_report')
    
    @api.multi
    def post(self):
        batches = self.filtered(lambda r: r.state == 'open')
        amount = 0.0
        for batch in self:
            
            if batch.state != 'open':
                raise UserError(_("Only a draft batch can be posted. Trying to post a payment in state %s.") % batch.state)
            
            sequence_code = 'account.cashbook.batch'
            batch.name = self.env['ir.sequence'].next_by_code(sequence_code)
            
            moves = self.env['account.move']

            for batch_line in batch.batch_line_ids:
                batch_line._check_payment_deposit()
                
                if (batch_line.account_id or batch_line.partner_id) and not batch_line.journal_entry_ids.ids:
                    if batch_line.payment > 0.0:
                        amount = batch_line.payment * 1
                    elif batch_line.deposit > 0.0:
                        amount = batch_line.deposit * -1
                    
                    move = batch_line._create_entry(amount)
                moves += move
            #create the journal entry
            
            batch.write({'state':'confirm'})     

class account_cashbook_batch_line(models.Model):
    _name = "account.cashbook.batch.line"
    _description = "Cashbook Batch Line"
    _order = "batch_id desc, sequence, id desc"
        
    payment_type = fields.Selection([('ar', 'Account Receivable'), ('ap', 'Account Payable'),('gl', 'General Ledger')], string='Payment Type', required=True, default='ar')
    batch_id = fields.Many2one('account.cashbook.batch', string="Batch id")
    partner_id = fields.Many2one('res.partner', string='Partner')
    account_id = fields.Many2one('account.account', string='Account', domain=[('deprecated', '=', False)])
    description = fields.Char(string='Description',required=True)
    payment_type = fields.Selection([('ar', 'Account Receivable'), ('ap', 'Account Payable'),('gl', 'General Ledger')], string='Payment Type', default='gl')
    reference = fields.Char(string='Reference')
    date = fields.Date(required=True, default=lambda self: self._context.get('date', fields.Date.context_today(self)))
    payment = fields.Float(string='Payment', required=True)
    deposit = fields.Float(string='Deposit', required=True)
    journal_id = fields.Many2one('account.journal', related='batch_id.journal_id', string='Journal', store=True, readonly=True)
    sequence = fields.Integer(index=True, help="Gives the sequence order when displaying a list of bank statement lines.", default=1)
    state = fields.Selection(related='batch_id.state' , string='Status', readonly=True)
    journal_entry_ids = fields.One2many('account.move', 'batch_line_id', 'Journal Entries', copy=False, readonly=True)
    
    @api.one
    @api.constrains('payment')
    def _check_amount(self):
        if not self.payment > 0.0 and not self.deposit > 0.0:
            raise ValidationError(_('The deposit amount must be strictly positive.'))
    
    @api.one
    @api.constrains('deposit')
    def _check_amount(self):
        if not self.deposit > 0.0 and not self.payment > 0.0:
            raise ValidationError(_('The payment amount must be strictly positive.'))
    
    def _check_payment_deposit(self):
        if self.deposit > 0 and self.payment > 0:
            raise UserError(_("You can not pay and deposit on the same batch line") )   
    
    def _create_entry(self,amount):
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        invoice_currency = False
        
        if not self.payment > 0.0 and not self.deposit > 0.0:
            raise ValidationError(_('The deposit/payment amount must be strictly positive.'))
        
        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.date).compute_amount_fields(amount, self.batch_id.currency_id, self.batch_id.company_id.currency_id, invoice_currency)
               
        move = self.env['account.move'].create(self._get_move_vals())
        
        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        counterpart_aml_dict.update(self._get_counterpart_move_line_vals())
        #counterpart_aml_dict.update({'currency_id': self.batch_id.currency_id})
        counterpart_aml = aml_obj.create(counterpart_aml_dict)
        
        #Write counterpart lines
        if not self.batch_id.currency_id != self.batch_id.company_id.currency_id:
            amount_currency = 0
        liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
        aml_obj.create(liquidity_aml_dict)
        
        move.post()
        return move
        
    def _get_move_vals(self, journal=None):
        """ Return dict to create the payment move
        """
        journal = journal or self.journal_id
        if not journal.sequence_id:
            raise UserError(_('Configuration Error !'), _('The journal %s does not have a sequence, please specify one.') % journal.name)
        if not journal.sequence_id.active:
            raise UserError(_('Configuration Error !'), _('The sequence of journal %s is deactivated.') % journal.name)
        name = journal.with_context(ir_sequence_date=self.date).sequence_id.next_by_id()
        return {
            'name': name,
            'date': self.date,
            'ref': (self.reference or '') + ' - ' + (self.batch_id.name or ''),
            'company_id': self.batch_id.company_id.id,
            'journal_id': journal.id,
            'batch_line_id': self.id,
        }
        
    def _get_shared_move_line_vals(self, debit, credit, amount_currency, move_id, invoice_id=False):
        """ Returns values common to both move lines (except for debit, credit and amount_currency which are reversed)
        """
        return {
            'partner_id': self.payment_type in ('ar', 'ap') and self.env['res.partner']._find_accounting_partner(self.partner_id).id or False,
            #'invoice_id': invoice_id and invoice_id.id or False,
            'move_id': move_id,
            'debit': debit,
            'credit': credit,
            'amount_currency': amount_currency or False,
        }   
        
    def _get_counterpart_move_line_vals(self, invoice=False):
        if self.payment_type == 'transfer':
            name = self.name
        else:
            name = ''
            if self.payment_type == 'ar':
                if self.payment > 0.0:
                    name += _("Customer Payment")
                elif self.deposit > 0.0:
                    name += _("Customer Refund")
            elif self.payment_type == 'ap':
                if self.payment > 0.0:
                    name += _("Vendor Payment")
                elif self.deposit > 0.0:
                    name += _("Vendor Refund")
            if invoice:
                name += ': '
                for inv in invoice:
                    if inv.move_id:
                        name += inv.number + ', '
                name = name[:len(name)-2] 
        return {
            'name': self.description,
            'account_id': self._get_destination_account_id(),
            'journal_id': self.journal_id.id,
            'currency_id': self.batch_id.currency_id != self.batch_id.company_id.currency_id and self.batch_id.currency_id.id or False,
            'batch_id': self.batch_id.id,
        }
         
    def _get_liquidity_move_line_vals(self, amount):
        name = self.description
        if self.payment_type == 'transfer':
            name = _('Transfer to %s') % self.destination_journal_id.name
        vals = {
            'name': name,
            'account_id': self.payment_type in ('ap','gl') and self.journal_id.default_debit_account_id.id or self.journal_id.default_credit_account_id.id,
            'batch_id': self.batch_id.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.batch_id.currency_id != self.batch_id.company_id.currency_id and self.currency_id.id or False,
        }

        # If the journal has a currency specified, the journal item need to be expressed in this currency
        if self.journal_id.currency_id and self.batch_id.currency_id != self.journal_id.currency_id:
            amount = self.batch_id.currency_id.with_context(date=self.date).compute(amount, self.journal_id.currency_id)
            debit, credit, amount_currency, dummy = self.env['account.move.line'].with_context(date=self.date).compute_amount_fields(amount, self.journal_id.currency_id, self.batch_id.company_id.currency_id)
            vals.update({
                'amount_currency': amount_currency,
                'currency_id': self.journal_id.currency_id.id,
            })

        return vals
    
    def _get_destination_account_id(self):        
        if self.payment_type == 'ar':
            return self.partner_id.property_account_receivable_id.id
        elif self.payment_type == 'ap':
            return self.partner_id.property_account_payable_id.id
        elif self.payment_type == 'gl':
            return self.account_id.id
    
    @api.multi
    def unlink(self):
        for line in self:
            if line.journal_entry_ids.ids:
                raise UserError(_('You cannot delete a cashbook batch line that has been posted.'))
        return super(account_cashbook_batch_line, self).unlink()
    
class account_journal(models.Model):
    _inherit = "account.journal"
    
    @api.multi
    def open_action(self):
        """return action based on type for related journals"""
        action_name = self._context.get('action_name', False)
        if not action_name:
            if self.type == 'bank' or self.type == 'cash':
                action_name = 'action_cashbook_batch'
            else:
                action = super(account_journal,self).open_action()
                return action
                
        _journal_type_map = {
            ('bank', None): 'bank',
            ('cash', None): 'cash',
        }
        journal_type = _journal_type_map[(self.type, self._context.get('invoice_type'))]

        ctx = self._context.copy()
        ctx.pop('group_by', None)
        ctx.update({
            'journal_type': self.type,
            'default_journal_id': self.id,
            'search_default_journal_id': self.id,
            'default_type': journal_type,
            'type': journal_type
        })

        [action] = self.env.ref('account_cashbook_batch.%s' % action_name).read()
        action['context'] = ctx
        action['domain'] = self._context.get('use_domain', [])
        if action_name in ['action_cashbook_batch']:
            action['views'] = False
            action['view_id'] = False
        return action
        
class account_move(models.Model):
    _inherit = 'account.move'
    
    batch_line_id = fields.Many2one('account.cashbook.batch.line', index=True, string='Cashbook batch line', copy=False, readonly=True)
    
class account_move_line(models.Model):
    _inherit = 'account.move.line'
    
    batch_id = fields.Many2one('account.cashbook.batch', index=True, string='Cashbook Batch', copy=False)
    