# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models

from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError

class purchase_order_line(models.Model):
    _inherit = "purchase.order.line"
    
    @api.multi
    def _prepare_invoice_line(self, invoice):
        """
        Prepare the dict of values to create the new invoice line for a purchase order line.
        
        :param invoice: account.invoice 
        """
        self.ensure_one()
        res = {}
        if self.product_id.purchase_method == 'purchase':
            qty = self.product_qty - self.qty_invoiced
        else:
            qty = self.qty_received - self.qty_invoiced
        if float_compare(qty, 0.0, precision_rounding=self.product_uom.rounding) <= 0:
            qty = 0.0
        invoice_line = self.env['account.invoice.line']
        taxes = self.taxes_id
        invoice_line_tax_ids = self.order_id.fiscal_position_id.map_tax(taxes)
        res = {
            'name': self.order_id.name+': '+self.name,
            #'sequence': self.sequence,
            'origin': self.order_id.name,
            'account_id': invoice_line.with_context({'journal_id': invoice.journal_id.id, 'type': 'in_invoice'})._default_account(),
            'price_unit': self.price_unit,
            'quantity': qty,
            'discount': self.discount,
            'uom_id': self.product_uom.id,
            'product_id': self.product_id.id or False,
            #'layout_category_id': self.layout_category_id and self.layout_category_id.id or False,
            'account_analytic_id': self.account_analytic_id.id,
            'analytic_tag_ids': self.analytic_tag_ids.ids,
            'invoice_line_tax_ids': [(6,0,invoice_line_tax_ids.ids)],
        }
        account = invoice_line.get_invoice_line_account('in_invoice', self.product_id, self.order_id.fiscal_position_id, self.env.user.company_id)
        if account:
            res['account_id'] = account.id
        return res
        
    @api.multi
    def invoice_line_create(self, invoice, qty):
        """
        Create an invoice line. The quantity to invoice can be positive (invoice) or negative
        (refund).

        :param invoice: account.invoice
        :param qty: float quantity to invoice
        """
        inv_obj = self.env['account.invoice']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            if not float_is_zero(qty, precision_digits=precision):
                vals = line._prepare_invoice_line(invoice)
                vals.update({'invoice_id': invoice.id, 'purchase_line_id': line.id})
                self.env['account.invoice.line'].create(vals)
    
    

class purchase_order(models.Model):
    _inherit = "purchase.order"
    
    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a purchase order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        
        journal_domain = [
            ('type', '=', 'purchase'),
            ('company_id', '=', self.company_id.id),
        ]
        journal_id = self.env['account.journal'].search(journal_domain, limit=1)
      
        if not journal_id:
            raise UserError(_('Please define an accounting purchase journal for this company.'))
        invoice_vals = {
            'name': '',
            'origin': self.name,
            'type': 'in_invoice',
            'account_id': self.partner_id.property_account_payable_id.id,
            'partner_id': self.partner_id.id,
            #'partner_shipping_id': self.partner_shipping_id.id,
            'journal_id': journal_id.id,
            'currency_id': self.currency_id.id,
            'date_invoice':self.date_order,
            #'comment': self.note,
            #'payment_term_id': self.payment_term_id.id,
            #'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            #'user_id': self.user_id and self.user_id.id,
            #'team_id': self.team_id.id
        }
        return invoice_vals
    
    @api.multi
    def action_invoice_create(self, grouped=False):
        """
        Create the invoice associated to the PO.
        :param grouped: if True, invoices are grouped by PO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :returns: list of created invoices
        """
        inv_obj = self.env['account.invoice']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoices = {}
        references = {}
        for order in self:
            group_key = order.id if grouped else (order.partner_id.id, order.currency_id.id)
            for line in order.order_line:
                if float_is_zero(line.product_qty - line.qty_invoiced, precision_digits=precision):
                    continue
                if group_key not in invoices:
                    inv_data = order._prepare_invoice()
                    invoice = inv_obj.create(inv_data)
                    references[invoice] = order
                    invoices[group_key] = invoice
                elif group_key in invoices:
                    vals = {}
                    if order.name not in invoices[group_key].origin.split(', '):
                        vals['origin'] = invoices[group_key].origin + ', ' + order.name
                    #if order.partner_id and order.partner_id not in invoices[group_key].name.split(', ') and order.partner_id != invoices[group_key].name:
                    #    vals['name'] = invoices[group_key].name + ', ' + order.partner_id.ref or 
                    invoices[group_key].write(vals)
                line.invoice_line_create(invoices[group_key],line.product_qty - line.qty_invoiced)
            if references.get(invoices.get(group_key)):
                if order not in references[invoices[group_key]]:
                    references[invoice] = references[invoice] | order

        if not invoices:
            raise UserError(_('There is no invoicable line.'))

        for invoice in invoices.values():
            if not invoice.invoice_line_ids:
                raise UserError(_('There is no invoicable line.'))
            # If invoice is negative, do a refund invoice instead
            if invoice.amount_untaxed < 0:
                invoice.type = 'out_refund'
                for line in invoice.invoice_line_ids:
                    line.quantity = -line.quantity
            # Use additional field helper function (for account extensions)
            for line in invoice.invoice_line_ids:
                line._set_additional_fields(invoice)
            # Necessary to force computation of taxes. In account_invoice, they are triggered
            # by onchanges, which are not triggered when doing a create.
            invoice.compute_taxes()
            invoice.message_post_with_view('mail.message_origin_link',
                values={'self': invoice, 'origin': references[invoice]},
                subtype_id=self.env.ref('mail.mt_note').id)
        return [inv.id for inv in invoices.values()]