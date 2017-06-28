# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    def _update_product_cost_price(self):
        ProductProduct = self.env['product.product']
        PurchaseOrderLine = self.env['purchase.order.line']
        new_std_price = 0.0
        
        for order in self:
            for po_line in order.order_line:
                product = po_line.product_id
                if po_line.discount:
                    new_std_price = po_line.price_unit * (1 - po_line.discount/100)
                else:
                    new_std_price = po_line.price_unit
            
                if po_line.update_cost_price and product.standard_price != new_std_price:
                    product.write({'standard_price':new_std_price})
        return True
                    
    
class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    
    @api.depends('discount')
    def _compute_amount(self):
        prices = {}
        for line in self:
            if line.discount:
                prices[line.id] = line.price_unit
                line.price_unit *= (1 - line.discount / 100.0)
            super(PurchaseOrderLine, line)._compute_amount()
            if line.discount:
                line.price_unit = prices[line.id]
                
    @api.multi
    def _get_stock_move_price_unit(self):
        """Get correct price with discount replacing current price_unit
        value before calling super and restoring it later for assuring
        maximum inheritability.
        """
        self.ensure_one()
        line = self[0]
        order = line.order_id
        price_unit = line.price_unit
        if line.discount:
            price_unit *= (100 - line.discount) / 100
        if line.taxes_id:
            price_unit = line.taxes_id.with_context(round=False).compute_all(price_unit, currency=line.order_id.currency_id, quantity=1.0)['total_excluded']
        if line.product_uom.id != line.product_id.uom_id.id:
            price_unit *= line.product_uom.factor / line.product_id.uom_id.factor
        if order.currency_id != order.company_id.currency_id:
            price_unit = order.currency_id.compute(price_unit, order.company_id.currency_id, round=False)
        return price_unit
    
    discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'), default=0.0)
    update_cost_price = fields.Boolean(string="Update Cost Price?", default= True, help="Select to update cost price of product after transfer")
    
    _sql_constraints = [
        ('discount_limit', 'CHECK (discount <= 100.0)',
         'Discount must be lower than 100%.'),
    ]
    
    
class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def do_transfer(self):
        """
            On transfer update cost price
        """
        return_val = super(StockPicking, self).do_transfer()
        for rec in self: 
            if rec.purchase_id and rec.picking_type_id.code == "incoming":
                rec.purchase_id._update_product_cost_price()
        
        return return_val
        
        
    
    
        