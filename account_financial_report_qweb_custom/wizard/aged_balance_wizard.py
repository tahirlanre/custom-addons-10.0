# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
# Author: Damien Crier, Andrea Stirpe, Kevin Graveman, Dennis Sluijk
# Author: Julien Coux
# Copyright 2016 Camptocamp SA, Onestein B.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from odoo import api, fields, models

class AgedReceivableBalance(models.TransientModel):
    """Aged partner balance report wizard."""
    
    _name = 'aged.receivable.balance.wizard'
    _description = 'Aged Receivable Balance Wizard'

    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.user.company_id,
        string='Company'
    )
    date_at = fields.Date(required=True,
                          default=fields.Date.to_string(datetime.today()))
    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries')],
                                   string='Target Moves',
                                   required=True,
                                   default='all')
    account_ids = fields.Many2many(
        comodel_name='account.account',
        string='Filter accounts',
    )
    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Filter partners',
    )
    show_move_line_details = fields.Boolean()
    show_credit_balances_only = fields.Boolean(string='Show credit balances only')
    show_debit_balances_only = fields.Boolean(string='Show debit balances only')
    hide_account_balance_at_0 = fields.Boolean(string='Hide zero balances',default=True)


    @api.multi
    def button_export_pdf(self):
        self.ensure_one()
        return self._export()

    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        return self._export(xlsx_report=True)

    def _prepare_report_aged_partner_balance(self):
        self.ensure_one()
        self.account_ids = self.env['account.account'].search([('internal_type', '=', 'receivable')])
        return {
            'date_at': self.date_at,
            'only_posted_moves': self.target_move == 'posted',
            'company_id': self.company_id.id,
            'filter_account_ids': [(6, 0, self.account_ids.ids)],
            'filter_partner_ids': [(6, 0, self.partner_ids.ids)],
            'show_move_line_details': self.show_move_line_details,
            'hide_account_balance_at_0': self.hide_account_balance_at_0,
            'show_credit_balances_only': self.show_credit_balances_only,
            'show_debit_balances_only': self.show_debit_balances_only,
            'receiveable_accounts_only': True,
            'payable_accounts_only': False,
        }

    def _export(self, xlsx_report=False):
        """Default export is PDF."""
        model = self.env['report_aged_partner_balance_qweb']
        report = model.create(self._prepare_report_aged_partner_balance())
        return report.print_report(xlsx_report)
        

class AgedPayableBalance(models.TransientModel):
    """Aged partner balance report wizard."""

    _name = 'aged.payable.balance.wizard'
    _description = 'Aged Receivable Balance Wizard'

    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.user.company_id,
        string='Company'
    )
    date_at = fields.Date(required=True,
                          default=fields.Date.to_string(datetime.today()))
    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries')],
                                   string='Target Moves',
                                   required=True,
                                   default='all')
    account_ids = fields.Many2many(
        comodel_name='account.account',
        string='Filter accounts',
    )
    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Filter partners',
    )
    show_move_line_details = fields.Boolean()
    show_credit_balances_only = fields.Boolean(string='Show credit balances only')
    show_debit_balances_only = fields.Boolean(string='Show debit balances only')
    hide_account_balance_at_0 = fields.Boolean(string='Hide zero balances',default=True)


    @api.multi
    def button_export_pdf(self):
        self.ensure_one()
        return self._export()

    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        return self._export(xlsx_report=True)

    def _prepare_report_aged_partner_balance(self):
        self.ensure_one()
        self.account_ids = self.env['account.account'].search([('internal_type', '=', 'payable')])
        return {
            'date_at': self.date_at,
            'only_posted_moves': self.target_move == 'posted',
            'company_id': self.company_id.id,
            'filter_account_ids': [(6, 0, self.account_ids.ids)],
            'filter_partner_ids': [(6, 0, self.partner_ids.ids)],
            'show_move_line_details': self.show_move_line_details,
            'hide_account_balance_at_0': self.hide_account_balance_at_0,
            'show_credit_balances_only': self.show_credit_balances_only,
            'show_debit_balances_only': self.show_debit_balances_only,
            'payable_accounts_only': True,
            'receiveable_accounts_only': False,
        }

    def _export(self, xlsx_report=False):
        """Default export is PDF."""
        model = self.env['report_aged_partner_balance_qweb']
        report = model.create(self._prepare_report_aged_partner_balance())
        return report.print_report(xlsx_report)

    
    
