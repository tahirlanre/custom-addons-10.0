# -*- coding: utf-8 -*-
# © 2018 Tahir Aduragba (SITASYS)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _

class AgedPartnerBalanceReport(models.TransientModel):
    _inherit = 'report_aged_partner_balance_qweb'
    
    show_credit_balances_only = fields.Boolean()
    show_debit_balances_only = fields.Boolean()
    receiveable_accounts_only = fields.Boolean()
    payable_accounts_only = fields.Boolean()
    hide_account_balance_at_0 = fields.Boolean(default=True)
    
    def _prepare_report_open_items(self):
        self.ensure_one()
        return {
            'date_at': self.date_at,
            'only_posted_moves': self.only_posted_moves,
            'company_id': self.company_id.id,
            'filter_account_ids': [(6, 0, self.filter_account_ids.ids)],
            'filter_partner_ids': [(6, 0, self.filter_partner_ids.ids)],
            'hide_account_balance_at_0': self.hide_account_balance_at_0,
            'show_credit_balances_only': self.show_credit_balances_only,
            'show_debit_balances_only': self.show_debit_balances_only,
            'receiveable_accounts_only': self.receiveable_accounts_only,
            'payable_accounts_only': self.payable_accounts_only,
        }
    