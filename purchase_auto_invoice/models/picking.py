# -*- coding: utf-8 -*-
# © 2017 SITASYS LTD ()
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models

class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def do_transfer(self):
        """
            On transfer create invoice
        """
        return_val = super(StockPicking, self).do_transfer()
        #for picking in self:
        #    vals={'purchase_id': self.purchase_id}
        orders_to_invoice = []
        invoice = self.env['account.invoice']
        for rec in self: 
            if rec.purchase_id and rec.picking_type_id.code == "incoming":
                rec.purchase_id.action_invoice_create()
        
        return return_val