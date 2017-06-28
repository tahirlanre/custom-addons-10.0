# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    @api.onchange('partner_id')
    def _change_customer_details(self):
        if self.partner_id:
            self.customer_details = str(self.partner_id.name) + "\n" + str(self.partner_id.contact_address)
        return {}
    
    @api.depends('sale_id.customer_details')
    def _set_name_from_customer_details(self):
        for invoice in self:
            if invoice.customer_details:
                invoice.name_from_customer_details = invoice.customer_details.split('\n')[0]
        return {}
    
    sale_id = fields.Many2one('sale.order', string='Sale Order No', help="Reference of Sale Order that produced this invoice")
    customer_details = fields.Text(related='sale_id.customer_details', string='Customer Details')
    customer_code = fields.Char(related="partner_id.ref", string="Customer Code")
    name_from_customer_details = fields.Text(string="Customer Name", compute='_set_name_from_customer_details',store=True)
    
    
class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    #overide _onchange_product_id to use only product name without ref as invoice line description by default
    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine,self)._onchange_product_id()
        self.name = self.product_id.name             
        return res
    
    @api.one    
    @api.depends('discount')
    def _compute_price(self):
        super(AccountInvoiceLine,self)._compute_price()
        self.discount_net_amount = (self.price_unit * ((self.discount or 0.0) / 100.0)) * self.quantity
        
    
    discount_net_amount = fields.Float(string="Discount Amount", store=True, readonly=True, compute='_compute_price')