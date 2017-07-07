# -*- coding: utf-8 -*-

from odoo import models,api,fields


class AccountJournal(models.Model):
    _inherit = "account.journal"
       
    default_debit_account_code = fields.Char(string="Journal Account Code", domain="['|',('journal_type','=','bank'),('journal_type','=','cash')]",related="default_credit_account_id.code")