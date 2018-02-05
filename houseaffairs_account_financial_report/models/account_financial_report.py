# -*- coding: utf-8 -*-

import time
from odoo import api, models,fields
    
class ReportFinancial(models.AbstractModel):
    _inherit = 'report.account.report_financial'
    
    @api.depends('company_id')
    def _compute_unaffected_earnings_account(self):
        account_type = self.env.ref('account.data_unaffected_earnings')
        self.unaffected_earnings_account = self.env['account.account'].search(
            [
                ('user_type_id', '=', account_type.id),
                ('company_id', '=', self.company_id.id)
            ])

    unaffected_earnings_account = fields.Many2one(
        comodel_name='account.account',
        compute='_compute_unaffected_earnings_account',
        store=True
    )
    
    company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.user.company_id)
    
    def _complete_unaffected_earnings_account_values(self):
        context = dict(self._context or {})
        
        company = self.env.user.company_id
        unaffected_earnings_account = self.env['account.account'].search([('company_id', '=', company.id), ('user_type_id', '=', self.env.ref('account.data_unaffected_earnings').id)], limit=1)
        
        res = {}
        
        if context.get('date_from'):
            date_from = context['date_from']
            state = context
            init_balance_history = True
        else:
            return
        
        query = """
        
        SELECT
            %s as id, COALESCE(SUM(credit), 0) as credit, 
            COALESCE(SUM(debit),0) - COALESCE(SUM(credit), 0) as balance, 
            COALESCE(SUM(debit), 0) as debit
        FROM
            account_move_line aml
            LEFT JOIN account_account acc ON (aml.account_id = acc.id)
            LEFT JOIN account_account_type acc_type ON (acc.user_type_id = acc_type.id)
            LEFT JOIN account_move m ON (aml.move_id = m.id)
        WHERE
            m.state IN %s
            AND aml.company_id = %s
            AND aml.date < %s
            AND acc_type.include_initial_balance = FALSE
        """

        params = [
            # SELECT
            unaffected_earnings_account.id,
            # WHERE
            ('posted',), #TODO
            company.id,
            date_from,
        ]

        self.env.cr.execute(query, tuple(params))
        for row in self.env.cr.dictfetchall():
            res[row['id']] = row
        return res
    
    def _compute_account_balance(self, accounts):
        company = self.env.user.company_id
        unaffected_earnings_account = self.env['account.account'].search([('company_id', '=', company.id), ('user_type_id', '=', self.env.ref('account.data_unaffected_earnings').id)], limit=1)
        unaffected_earnings_account_id = unaffected_earnings_account.id
        
        res = super(ReportFinancial,self)._compute_account_balance(accounts)
        
        if unaffected_earnings_account_id in accounts.ids:
            unaffected_earnings_account_values = self._complete_unaffected_earnings_account_values()
            res[unaffected_earnings_account_id]['credit'] = res[unaffected_earnings_account_id]['credit'] + unaffected_earnings_account_values[unaffected_earnings_account_id]['credit']
            res[unaffected_earnings_account_id]['debit'] = res[unaffected_earnings_account_id]['debit'] + unaffected_earnings_account_values[unaffected_earnings_account_id]['debit']
            res[unaffected_earnings_account_id]['balance'] = res[unaffected_earnings_account_id]['balance'] + unaffected_earnings_account_values[unaffected_earnings_account_id]['balance']
        return res
        
    def get_account_lines(self,data):
        lines = []
        account_report = self.env['account.financial.report'].search([('id', '=', data['account_report_id'][0])])
        child_reports = account_report._get_children_by_order()
        res = self.with_context(data.get('used_context'))._compute_report_balance(child_reports)
        if data['enable_filter']:
            comparison_res = self.with_context(data.get('comparison_context'))._compute_report_balance(child_reports)
            for report_id, value in comparison_res.items():
                res[report_id]['comp_bal'] = value['balance']
                report_acc = res[report_id].get('account')
                if report_acc:
                    for account_id, val in comparison_res[report_id].get('account').items():
                        report_acc[account_id]['comp_bal'] = val['balance']
                        
        for report in child_reports:
            vals = {
                'name': report.name,
                'balance': res[report.id]['balance'] * report.sign,
                'type': 'report',
                'level': bool(report.style_overwrite) and report.style_overwrite or report.level,
                'account_type': report.type or False, #used to underline the financial report balances
            }
            if data['debit_credit']:
                vals['debit'] = res[report.id]['debit']
                vals['credit'] = res[report.id]['credit']

            if data['enable_filter']:
                vals['balance_cmp'] = res[report.id]['comp_bal'] * report.sign

            if report.display_detail == 'no_detail':
                lines.append(vals)
                #the rest of the loop is used to display the details of the financial report, so it's not needed here.
                continue

            if res[report.id].get('account'):
            #if res[report.id].get('account_type'):
                sub_lines = []
                for account_id, value in res[report.id]['account'].items():
                #for account_type_id, value in res[report.id]['account_type'].items():
                    #if there are accounts to display, we add them to the lines with a level equals to their level in
                    #the COA + 1 (to avoid having them with a too low level that would conflicts with the level of data
                    #financial reports for Assets, liabilities...)
                    #account_type_balance = 0.0
                    flag = False
                    account = self.env['account.account'].browse(account_id)
                    #account_type = self.env['account.account.type'].browse(account_type_id)
                    #for account_id, value1 in value['account'].items():
                        #account_type_balance += value1['balance']
                        #account = self.env['account.account'].browse(account_id) #FIXME bad programming.....
                    
                    sub_vals = {
                        'name': account.code + ' ' + account.name,
                        #'name': account_type.name,
                        'balance': value['balance'] * report.sign or 0.0,
                        #'balance': value['balance'] * report.sign or 0.0,
                        'type': 'account',
                        'level': report.display_detail == 'detail_with_hierarchy' and 4,
                        'account_type': account.internal_type,
                    }
                    if data['debit_credit']:
                        sub_vals['debit'] = value['debit']
                        sub_vals['credit'] = value['credit']
                        if not account.company_id.currency_id.is_zero(vals['debit']) or not account.company_id.currency_id.is_zero(sub_vals['credit']):
                            flag = True
                    if not account.company_id.currency_id.is_zero(sub_vals['balance']):
                        flag = True
                    if data['enable_filter']:
                        sub_vals['balance_cmp'] = value['comp_bal'] * report.sign
                        if not account.company_id.currency_id.is_zero(sub_vals['balance_cmp']):
                            flag = True
                    if flag:
                        sub_lines.append(sub_vals)
                        vals.update({'sub_lines': sub_lines})
                #lines += sorted(sub_lines, key=lambda sub_line: sub_line['name'])
            lines.append(vals)
        return lines