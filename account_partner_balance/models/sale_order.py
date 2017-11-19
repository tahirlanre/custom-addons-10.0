from odoo import models, fields, api, _
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    @api.onchange('partner_id')
    def _get_customer_balance(self):
        if self.partner_id:
            self.customer_balance = self.partner_id.balance
          
    customer_balance = fields.Float(string="Customer Balance",compute=_get_customer_balance, readonly=True)