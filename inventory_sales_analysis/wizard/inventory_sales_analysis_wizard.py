# -*- coding: utf-8 -*-
# © 2017 SITAYS (tahirlanre@hotmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields

class inventory_sales_analysis_wizard(models.TransientModel):
    _name = "inventory.sales.analysis.wizard"
    
    start_date = fields.Date("Start date", required="True")
    end_date = fields.Date("End date", required="True")
    group_by = fields.Selection([('product','Product'), ('customer','Customer'),('sales_rep','Sales Representative')], string='Group by', required=True, default='product')
    sales_rep_ids = fields.Many2many(comodel_name='sales.rep', string="Filter Sales Representatives")
    product_ids = fields.Many2many(comodel_name='product.product', string="Filter Products")
    partner_ids = fields.Many2many(comodel_name='res.partner', string="Filter Customers")
    options = fields.Selection([('summary','Summary'),('detail','Detail')], string='Report Option', required=True, default='summary')

    
    @api.multi
    def button_export_pdf(self):
        self.ensure_one()
        return self._export()
        
    def _prepare_report_sales_analysis(self):
        
        return {
                    'start_date':self.start_date,
                    'end_date': self.end_date,
                    'group_by_product': self.group_by == 'product',
                    'group_by_sales_rep': self.group_by == 'sales_rep',
                    'group_by_partner': self.group_by == 'customer',
                    'filter_product_ids': [(6, 0, self.product_ids.ids)],
                    'filter_partner_ids': [(6, 0, self.partner_ids.ids)],
                    'filter_sales_rep_ids': [(6, 0, self.sales_rep_ids.ids)],
                }
    
    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        return self._export(xlsx_report=True)
        
    def _export(self, xlsx_report=False):
        model = self.env['report_inventory_sales_analysis_qweb']
        report = model.create(self._prepare_report_sales_analysis())
        return report.print_report(xlsx_report)
