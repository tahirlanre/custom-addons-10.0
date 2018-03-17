# -*- coding: utf-8 -*-
# © 2017 SITAYS (tahirlanre@hotmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields

class inventory_transaction_wizard(models.TransientModel):
    _name = "inventory.transaction.wizard"
    
    start_date = fields.Date("Start date", required="True")
    end_date = fields.Date("End date", required="True")
    group_by = fields.Selection([('product','Product'), ('customer','Customer'),('sales_rep','Sales Representative'),('date','Date')], string='Group by', required=True, default='product')
    sales_rep_ids = fields.Many2many(comodel_name='sales.rep', string="Filter Sales Representatives")
    product_ids = fields.Many2many(comodel_name='product.product', string="Filter Products")
    partner_ids = fields.Many2many(comodel_name='res.partner', string="Filter Customers")
    product_category_ids = fields.Many2many(comodel_name='product.category', string="Product Categories")
    options = fields.Selection([('summary','Summary'),('detail','Detail')], string='Report Option', required=True, default='summary')
    transaction_type_ids = fields.Many2many(comodel_name='inventory.transaction.type', string="Transaction types")
    #in_invoice = fields.Boolean('Vendor Bill', default=True)
    #in_refund = fields.Boolean('Vendor Refund', default=True)
    #out_invoice = fields.Boolean('Customer Invoice',default=True)
    #out_refund = fields.Boolean('Customer Refund',default=True)

    @api.multi
    def button_export_pdf(self):
        self.ensure_one()
        return self._export()
        
    def _prepare_report_transaction(self):
        return {
                    'start_date':self.start_date,
                    'end_date': self.end_date,
                    'group_by_product': self.group_by == 'product',
                    'group_by_sales_rep': self.group_by == 'sales_rep',
                    'group_by_partner': self.group_by == 'customer',
                    'group_by_date': self.group_by == 'date',
                    'filter_product_ids': [(6, 0, self.product_ids.ids)],
                    'filter_partner_ids': [(6, 0, self.partner_ids.ids)],
                    'filter_sales_rep_ids': [(6, 0, self.sales_rep_ids.ids)],
                    'filter_transaction_types': [(6, 0, self.transaction_type_ids.ids)],
                    'filter_product_categories': [(6, 0, self.product_category_ids.ids)],
                    #'filter_in_invoice': self.in_invoice,
                    #'filter_out_invoice': self.in_refund,
                    #'filter_in_refund': self.out_invoice,
                    #'filter_out_refund': self.out_refund,
                    'detailed': self.options == 'detail',
                    'summary': self.options == 'summary',
                }
    
    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        return self._export(xlsx_report=True)
        
    def _export(self, xlsx_report=False):
        model = self.env['report_inventory_transaction_qweb']
        report = model.create(self._prepare_report_transaction())
        return report.print_report(xlsx_report)

