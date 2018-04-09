from timer import timing

from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @timing
    @api.multi
    def process_order(self):
        return super(SaleOrder,self).process_order()