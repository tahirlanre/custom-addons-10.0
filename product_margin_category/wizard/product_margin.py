# -*- coding: utf-8 -*-

from odoo import api, models, fields

class ProductMargin(models.TransientModel):
    _inherit = 'product.margin'
    
    category_to = fields.Many2one('product.category', string='From category', required=True)
    category_from = fields.Many2one('product.category', string='To category', required=True)
    
    #check if product was sold in the period
    def _sales_in_period(self,product):
        states = ()
        if self.invoice_state == 'paid':
            states = ('paid',)
        elif self.invoice_state == 'open_paid':
            states = ('open', 'paid')
        elif self.invoice_state == 'draft_open_paid':
            states = ('draft', 'open', 'paid')
        invoice_types = ('out_invoice', 'in_refund') 
        lines_in_period = self.env['account.invoice.line'].search([('product_id','=',product.id),('invoice_id.date_invoice','>=',self.from_date),('invoice_id.date_invoice','<=',self.to_date),('invoice_id.type','in',invoice_types),('invoice_id.state','=',states)])
        if len(lines_in_period) > 0:
            return True
        else:
            return False
    
    @api.multi
    def action_open_window(self):
        res = super(ProductMargin,self).action_open_window()
        data = []
        if self.category_to:
            category_to = int(self.category_to.id)
            
        if self.category_from:
            category_from = int(self.category_from.id)

        #FIXME TODO category range should be checked with code from product_usability and not id
        for product in self.env['product.product'].search([('categ_id.id','>=', category_to),('categ_id.id','<=', category_from)]):
            if self._sales_in_period(product):
                data.append(product.id)
            
        res['domain'] = [('id','in',data)]
        return res