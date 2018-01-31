# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF, float_compare
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
        
    @api.onchange('partner_id')
    def _change_customer_details(self):
        if self.partner_id:
            self.customer_details = str(self.partner_id.name) + "\n" + str(self.partner_id.contact_address)
        return {}
        
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder,self)._prepare_invoice()
        invoice_vals.update({'sale_id':self.id})
        invoice_vals.update({'date_invoice':self.date_order})
        return invoice_vals
    
    def check_product_qty_availability(self):
        for line in self.order_line:
            if line.product_id.type == 'product':
                precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
                product_qty = line.product_uom._compute_quantity(line.product_uom_qty, line.product_id.uom_id)
                if float_compare(line.product_id.qty_available, product_qty, precision_digits=precision) == -1:
                    is_available = line._check_routing()
                    if not is_available:
                        msg = 'You plan to sell %s %s of %s but you only have %s %s available!' % (line.product_uom_qty, line.product_uom.name, line.product_id.display_name, line.product_id.qty_available, line.product_id.uom_id.name)
                        raise UserError(_('Not enough inventory!\n' + msg))
        return {}
        

    def check_limit(self):
        current_user = self.env.user
        manager_group = 'sales_team.group_sale_manager'
        partner = self.partner_id
        moveline_obj = self.env['account.move.line']
        movelines = moveline_obj.search([('partner_id', '=', partner.id),('account_id.user_type_id.type', 'in',['receivable', 'payable'])])

        debit, credit = 0.0, 0.0
        today_dt = datetime.strftime(datetime.now().date(), DF)

        for line in movelines:
            #if line.date_maturity < today_dt:
            credit += line.debit
            debit += line.credit
        
        if (credit - debit + self.amount_total) > partner.credit_limit:
            if not partner.over_credit:
                msg = 'Can not confirm Sale Order, Total mature due Amount ' \
                      '%s as on %s !\nCheck Partner Accounts or Credit ' \
                      'Limits !' % (credit - debit, today_dt)
                raise UserError(_('Credit Over Limits !\n' + msg))
        else:
            return True

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:            
            order.check_limit()
            order.check_product_qty_availability()
        return res
    
    @api.depends('customer_details')
    @api.multi
    def _set_name_from_customer_details(self):
        for order in self:
            if self.customer_details:
                self.name_from_customer_details = self.customer_details.split('\n')[0]
        return {}
        
    customer_details = fields.Text(string='Customer Details')
    receipt_no = fields.Char(string='Receipt No', help="Receipt No from Dulux payment receipt")
    customer_code = fields.Char(related="partner_id.ref", string="Customer Code")
    name_from_customer_details = fields.Text(string="Customer Name", compute='_set_name_from_customer_details',store=True)
    
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    @api.multi
    @api.depends(
        'product_uom_qty',
        'product_id')
    def _get_product_available_qty(self):
        #self.ensure_one()
        for line in self:
            if line.order_id.state == 'draft':
                line.product_available_qty = line.product_id.with_context(
                    warehouse=line.order_id.warehouse_id.id
                ).qty_available
            
    product_available_qty = fields.Float(string='Available Qty',compute=_get_product_available_qty, readonly=True,store=True)
    #overide _onchange_product_id to use only product name without ref as invoice line description by default
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine,self).product_id_change()
        self.name = self.product_id.name             
        return res
    
    