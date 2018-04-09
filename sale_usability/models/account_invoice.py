# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    @api.onchange('partner_id')
    def _change_customer_details(self):
        if self.partner_id:
            self.customer_details = str(self.partner_id.name) + "\n" + str(self.partner_id.contact_address)
        return {}
    
    @api.depends('sale_id.customer_details')
    def _set_name_from_customer_details(self):
        for invoice in self:
            if invoice.customer_details:
                invoice.name_from_customer_details = invoice.customer_details.split('\n')[0]
        return {}
    
    sale_id = fields.Many2one('sale.order', string='Sale Order No', help="Reference of Sale Order that produced this invoice")
    customer_details = fields.Text(related='sale_id.customer_details', string='Customer Details')
    customer_code = fields.Char(related="partner_id.ref", string="Customer Code")
    name_from_customer_details = fields.Text(string="Customer Name", compute='_set_name_from_customer_details',store=True)
    
    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']
        account_move_line = self.env['account.move.line'].with_context(check_move_validity=False)
        
        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids:
                raise UserError(_('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            date_invoice = inv.date_invoice
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            iml += inv.tax_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)

            name = inv.name or '/'
            if inv.payment_term_id:
                totlines = inv.with_context(ctx).payment_term_id.with_context(currency_id=company_currency.id).compute(total, date_invoice)[0]
                res_amount_currency = total_currency
                ctx['date'] = date_invoice
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                })
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)
            
            #import pdb; pdb.set_trace()

            journal = inv.journal_id.with_context(ctx)
            line = inv.finalize_invoice_move_lines(line)

            date = inv.date or date_invoice
            move_vals = {
                'ref': inv.reference,
                #'line_ids': line,
                'journal_id': journal.id,
                'date': date,
                'narration': inv.comment,
            }
            ctx['company_id'] = inv.company_id.id
            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)
           
           # create account move line instead of using the write operation on to-many fields.
            for x, y, l in line:
                l['move_id'] = move.id
                account_move_line.create(l)
                
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
        return True
    
    
class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    #overide _onchange_product_id to use only product name without ref as invoice line description by default
    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine,self)._onchange_product_id()
        self.name = self.product_id.name             
        return res
    
    @api.one    
    @api.depends('discount')
    def _compute_price(self):
        super(AccountInvoiceLine,self)._compute_price()
        self.discount_net_amount = (self.price_unit * ((self.discount or 0.0) / 100.0)) * self.quantity
        
    
    discount_net_amount = fields.Float(string="Discount Amount", store=True, readonly=True, compute='_compute_price')