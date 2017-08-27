# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Account(models.Model):
    _inherit = "account.journal"
    
    can_send = fields.Boolean(string="Can send in Internal Transfers", default=False)
    can_receieve = fields.Boolean(string="Can receieve in Internal Transfers", default=False)
    
class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    destination_journal_id = fields.Many2one('account.journal', string='Transfer To', domain=['&',('type', 'in', ('bank', 'cash')),('can_receieve','=','True')])
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True, domain=['&',('type', 'in', ('bank', 'cash')),('can_send','=','True')])