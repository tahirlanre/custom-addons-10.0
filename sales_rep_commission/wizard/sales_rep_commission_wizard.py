# -*- coding: utf-8 -*-
# © 2017 SITAYS (tahirlanre@hotmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields

class sales_rep_commission_wizard(models.TransientModel):
    _name = "sales.rep.commission.wizard"
    
    start_date = fields.Date("Start date", required="True")
    end_date = fields.Date("End date", required="True")
    sales_rep_from = fields.Many2one('sales.rep')
    sales_rep_to = fields.Many2one('sales.rep')
    
    @api.multi
    def button_export_pdf(self):
        self.ensure_one()
        return self._export()
        
    def _prepare_report_sales_rep_commission(self):
        return {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'sales_rep_id_from': self.sales_rep_from.id,
            'sales_rep_id_to': self.sales_rep_to.id,
        }
    
    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        return self._export(xlsx_report=True)
        
    def _export(self, xlsx_report=False):
        model = self.env['report_sales_rep_commission_qweb']
        report = model.create(self._prepare_report_sales_rep_commission())
        return report.print_report(xlsx_report)

