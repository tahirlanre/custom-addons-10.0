# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    is_refund = fields.Boolean(
        string="Is a refund?",
        compute="_compute_is_refund",
        inverse="_inverse_is_refund",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Indicate if this invoice is a refund.",
    )
    
    goods_return_note = fields.Char(string="Goods return note", readonly=True, states={"draft": [("readonly", False)]},)
    
    @api.multi
    @api.depends("type")
    def _compute_is_refund(self):
        """Know if this invoice is a refund or not."""
        for one in self:
            one.is_refund = one.type.endswith("_refund")

    @api.multi
    def _inverse_is_refund(self):
        for one in self:
            args = "refund", "invoice"
            if one.is_refund:
                args = reversed(args)
            one.type = one.type.replace(*args)
    
    def invoice_validate(self):
        super(AccountInvoice, self).invoice_validate()
        for invoice in self:
            if invoice.type in ('out_refund') and invoice.state == 'open':
                for line in invoice.invoice_line_ids:
                    line._generate_moves()
        return True

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"
    
    @api.multi
    def _get_move_values(self, qty, location_id, location_dest_id):
        self.ensure_one()
        return {
            'name': _('CUSTOMER RTN: ') + (self.product_id.name or ''),
            'product_id': self.product_id.id,
            'product_uom': self.uom_id.id,
            'product_uom_qty': qty,
            'date': self.invoice_id.date_invoice,
            'company_id': self.invoice_id.company_id.id,
            'state': 'confirmed',
            #'restrict_lot_id': self.prod_lot_id.id,
            'restrict_partner_id': self.invoice_id.partner_id.id,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
        }
        
    def _generate_moves(self):
        moves = self.env['stock.move']
        #Quant = self.env['stock.quant']
        location = self.env.ref('stock.stock_location_stock')
        source_location = self.env.ref('stock.stock_location_customers')
        for line in self:
            if line.quantity == 0:
                continue
            if line.quantity > 0:
                vals = self._get_move_values(abs(line.quantity),source_location.id,location.id)
            move = moves.create(vals)
            move.action_done()  #confirm move
        return moves
    