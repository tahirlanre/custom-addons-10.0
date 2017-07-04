# -*- coding: utf-8 -*-

import time
from odoo import api, models,fields

class account_financial_report(models.Model):
    _inherit = "account.financial.report"

class AccountingReport(models.TransientModel):
    _inherit = "accounting.report"
    
    @api.multi
    def check_report(self):
        if self.date_to and self.date_from:
            self.enable_filter = True
            self.label_filter = "Year to Date"
            self.filter_cmp = 'filter_date'
            self.date_from_cmp = time.strftime('%Y-01-01')
            self.date_to_cmp = self.date_to
        res = super(AccountingReport, self).check_report()
        
        return res
    
class ReportFinancial(models.AbstractModel):
    _inherit = 'report.account.report_financial'
        
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
                sub_lines = []
                for account_id, value in res[report.id]['account'].items():
                    #if there are accounts to display, we add them to the lines with a level equals to their level in
                    #the COA + 1 (to avoid having them with a too low level that would conflicts with the level of data
                    #financial reports for Assets, liabilities...)
                    flag = False
                    account = self.env['account.account'].browse(account_id)
                    sub_vals = {
                        'name': account.code + ' ' + account.name,
                        'balance': value['balance'] * report.sign or 0.0,
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