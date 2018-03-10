# -*- coding: utf-8 -*-
# © 2018 SITAYS (sitasyslimited@gmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields

class ar_transaction_wizard(models.TransientModel):
    _name = "ar.transaction.wizard"
    
    start_date = fields.Date("Start date", required="True")
    end_date = fields.Date("End date", required="True")
    group_by = fields.Selection([('customer','Customer')], string='Group by', required=True, default='customer')
    #sales_rep_ids = fields.Many2many(comodel_name='sales.rep', string="Filter Sales Representatives")
    #product_ids = fields.Many2many(comodel_name='product.product', string="Filter Products")
    partner_ids = fields.Many2many(comodel_name='res.partner', string="Filter Customers")
    options = fields.Selection([('summary','Summary'),('detail','Detail')], string='Report Option', required=True, default='summary')

    
    @api.multi
    def button_export_pdf(self):
        self.ensure_one()
        return self._export()
        
    def _prepare_report_transaction(self):
        return {
                    'start_date':self.start_date,
                    'end_date': self.end_date,
                    'group_by_partner': self.group_by == 'customer',
                    'filter_partner_ids': [(6, 0, self.partner_ids.ids)],
                    'detailed': self.options == 'detail',
                    'summary': self.options == 'summary',
                }
    
    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        return self._export(xlsx_report=True)
        
    def _export(self, xlsx_report=False):
        model = self.env['report_ar_transaction_qweb']
        report = model.create(self._prepare_report_transaction())
        return report.print_report(xlsx_report)
