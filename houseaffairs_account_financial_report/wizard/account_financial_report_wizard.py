# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time


class FinancialReportWizard(models.TransientModel):
    _inherit = "accounting.report"
    
    def _build_comparison_context(self, data):
        result = {}
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        if data['form']['filter_cmp'] == 'filter_date':
            result['date_from'] = data['form']['date_from_cmp']
            result['date_to'] = data['form']['date_to_cmp']
            result['strict_range'] = True
        return result
    
    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'debit_credit', 'account_report_id', 'enable_filter','filter_cmp','target_move'])[0]
        if data['form']['date_to'] and data['form']['date_from']:
            data['form']['enable_filter'] = True
            data['form']['label_filter'] = "Year to Date"
            data['form']['filter_cmp'] = 'filter_date'
            data['form']['date_from_cmp'] = time.strftime('%Y-01-01')
            data['form']['date_to_cmp'] = data['form']['date_to']
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'en_US'))
        comparison_context = self._build_comparison_context(data)
        data['form']['comparison_context'] = comparison_context
        report = self.env['report.account.report_financial']
        data['report_lines'] = report.get_account_lines(data.get('form'))
        #report_lines = report.get_account_lines(data.get('form'))
        
        return {'type': 'ir.actions.report.xml',
                'report_name': 'houseaffairs_account_financial_report.report_financial_report_xlsx',
                'datas': data,
                'name': 'Financial Report'
                }