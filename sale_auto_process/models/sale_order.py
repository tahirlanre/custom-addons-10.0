from odoo import models, fields, api, _
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    @api.multi
    def process_order(self):
        for order in self:
            order.action_confirm()
            for picking in order.picking_ids:
                picking.validate_picking()
            invoice_ids = order.action_invoice_create()
            for invoice in self.env['account.invoice'].search([('id','in',invoice_ids)]):
                invoice.action_invoice_open()

    