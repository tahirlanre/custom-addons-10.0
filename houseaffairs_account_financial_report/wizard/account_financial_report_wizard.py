# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TrialBalanceReportWizard(models.TransientModel):
    _inherit = "accounting.report"
    
    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'date_from_cmp', 'debit_credit', 'date_to_cmp', 'filter_cmp', 'account_report_id', 'enable_filter', 'label_filter', 'target_move'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'en_US'))
        return {'type': 'ir.actions.report.xml',
                'report_name': 'houseaffairs_financial_report.report_financial_report_xlsx',
                'datas': data,
                'name': 'Financial Report'
                }