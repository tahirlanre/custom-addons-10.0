# -*- coding: utf-8 -*-

from odoo import models,api,fields,_
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang

        
        
class account_journal(models.Model):
    _inherit = "account.journal"
    
    @api.multi
    def create_cash_payment(self):
        ctx = self._context.copy()
        ctx.update({'journal_id': self.id, 'default_journal_id': self.id, 'default_journal_type': 'cash','default_statement_type': 'outbound'})
        return {
            'name': _('Create cash statement'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.bank.statement',
            'context': ctx,
        }
        
        
class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"
    
    def fast_counterpart_creation(self):
        if self.statement_id.statement_type == 'inbound':
            super(AccountBankStatementLine,self).fast_counterpart_creation()
        if self.statement_id.statement_type == 'outbound':
            for st_line in self:
                # Technical functionality to automatically reconcile by creating a new move line
                vals = {
                    'name': st_line.name,
                    'debit': st_line.amount > 0 and st_line.amount or 0.0,
                    'credit': st_line.amount < 0 and -st_line.amount or 0.0,
                    'account_id': st_line.account_id.id,
                }
                st_line.process_reconciliation(new_aml_dicts=[vals])
    
    account_id = fields.Many2one('account.account', required=True, string='Counterpart Account', domain=[('deprecated', '=', False)],
        help="This technical field can be used at the statement line creation/import time in order to avoid the reconciliation"
             " process on it later on. The statement line will simply create a counterpart on this account")    #set required=True
    name = fields.Char(string='Description', required=True) #default label changed from "Label" to "Description" and set to required=True
    ref = fields.Char(string='Journal')     #default label changed from "Reference" to "Journal"
             
class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"
            
    @api.multi
    def _balance_check(self):
        if self.statement_type == 'inbound':
            for stmt in self:
                if not stmt.currency_id.is_zero(stmt.difference):
                    if stmt.journal_type == 'cash':
                        if stmt.difference < 0.0:
                            account = stmt.journal_id.loss_account_id
                            name = _('Loss')
                        else:
                            # statement.difference > 0.0
                            account = stmt.journal_id.profit_account_id
                            name = _('Profit')
                        if not account:
                            raise UserError(_('There is no account defined on the journal %s for %s involved in a cash difference.') % (stmt.journal_id.name, name))

                        values = {
                            'statement_id': stmt.id,
                            'account_id': account.id,
                            'amount': stmt.difference,
                            'name': _("Cash difference observed during the counting (%s)") % name,
                        }
                        self.env['account.bank.statement.line'].create(values)
                    else:
                        balance_end_real = formatLang(self.env, stmt.balance_end_real, currency_obj=stmt.currency_id)
                        balance_end = formatLang(self.env, stmt.balance_end, currency_obj=stmt.currency_id)
                        raise UserError(_('The ending balance is incorrect !\nThe expected balance (%s) is different from the computed one. (%s)')
                            % (balance_end_real, balance_end))
        return True
            
    @api.multi
    def check_confirm_bank(self): 
        if self.statement_type == 'outbound':
            return self.button_confirm_bank()
        if self.statement_type == 'inbound':
            res = super(AccountBankStatement,self).check_confirm_bank()
            return res
    
    statement_type = fields.Selection([('inbound', 'In'), ('outbound', 'Out')], string='Statement Type', readonly=True, copy=False, default='inbound')
