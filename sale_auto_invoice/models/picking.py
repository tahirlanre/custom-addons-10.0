# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    @api.multi
    def do_transfer(self):
        """
            On transfer create invoice
        """
        return_val = super(StockPicking, self).do_transfer()
        orders_to_invoice = []  
        for rec in self: 
            #FIXME check products invoicing policy
            if rec.sale_id and rec.picking_type_id.code == "outgoing":
                invoice_ids = rec.sale_id.action_invoice_create() 
                for invoice in self.env['account.invoice'].search([('id','in',invoice_ids)]):
                    invoice.action_invoice_open()
        
        return return_val
        