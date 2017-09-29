# -*- coding: utf-8 -*-


from odoo import api, fields, models
import odoo.addons.decimal_precision as dp

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"
    
    margin = fields.Float(compute='_product_margin', digits=dp.get_precision('Product Price'), store=True)
    purchase_price = fields.Float(string='Cost', digits=dp.get_precision('Product Price'))
    
    def _compute_margin(self, invoice_id, product_id):
        frm_cur = self.env.user.company_id.currency_id
        to_cur = invoice_id.currency_id
        purchase_price = product_id.standard_price
        ctx = self.env.context.copy()
        ctx['date'] = invoice_id.date_invoice
        price = frm_cur.with_context(ctx).compute(purchase_price, to_cur, round=False)
        return price
    
    @api.model
    def _get_purchase_price(self, product, currency_id, date):
        frm_cur = self.env.user.company_id.currency_id
        to_cur = currency_id
        purchase_price = product.standard_price
        ctx = self.env.context.copy()
        ctx['date'] = date
        price = frm_cur.with_context(ctx).compute(purchase_price, to_cur, round=False)
        return {'purchase_price': price}
        
    @api.onchange('product_id')
    def product_id_change_margin(self):
        if not self.product_id:
            return
        self.purchase_price = self._compute_margin(self.invoice_id, self.product_id)
    
    @api.model
    def create(self, vals):
        # Calculation of the margin for programmatic creation of a SO line. It is therefore not
        # necessary to call product_id_change_margin manually
        if 'purchase_price' not in vals:
            invoice_id = self.env['account.invoice'].browse(vals['invoice_id'])
            product_id = self.env['product.product'].browse(vals['product_id'])
            #product_uom_id = self.env['product.uom'].browse(vals['product_uom'])

            vals['purchase_price'] = self._compute_margin(invoice_id, product_id)

        return super(AccountInvoiceLine, self).create(vals)
        
    @api.depends('product_id', 'purchase_price', 'quantity', 'price_unit')
    def _product_margin(self):
        for line in self:
            currency = line.invoice_id.currency_id
            line.margin = currency.round(line.price_subtotal - ((line.purchase_price or line.product_id.standard_price) * line.quantity))
    