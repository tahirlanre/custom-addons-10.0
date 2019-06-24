# -*- coding: utf-8 -*-

from odoo import models, fields, api

import odoo.addons.decimal_precision as dp


class delivery(models.Model):
    _name = 'delivery'
    _order = 'date'
    
    #TODO calculate date based on delivery type
    @api.depends('delivery_type_id')
    @api.multi
    def _calculate_actual_delivery_date(self):
        pass
    
    @api.depends('partner_id')
    def _get_partner_balance(self):
        if self.partner_id:
            self.partner_balance = self.partner_id.balance
    
    @api.onchange('partner_id')
    def _set_default_pickup_deatils(self):
        for delivery in self:
            street = ''
            street2 = ''
            city = ''
            if delivery.partner_id.street:
                street = delivery.partner_id.street
            if delivery.partner_id.street2:
                street2 = delivery.partner_id.street2
            if delivery.partner_id.city:
                city = delivery.partner_id.city
            delivery.pickup_location = street + street2 + city
            if delivery.partner_id.phone:
                delivery.pickup_number = delivery.partner_id.phone
                
            
    
    #TODO set required fields
    job_number = fields.Char('Tracking number', readonly=True, copy=False, default="Draft")
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    sequence = fields.Integer('Sequence') 
    date = fields.Date(required=True, default=lambda self: self._context.get('date', fields.Date.context_today(self)))
    invoice_ids = fields.Many2one('account.invoice', string='Delivery Invoice')
    booked_delivery_date = fields.Date(string='Booking Date',required=True, default=lambda self: self._context.get('date', fields.Date.context_today(self)))
    actual_delivery_date = fields.Date(string='Actual Delivery Date',required=True)
    delivery_line_ids = fields.One2many('delivery.line', 'delivery_id', string='Delivery lines')
    delivery_note = fields.Text(string='Delivery note')
    dropoff_rider = fields.Many2one('despatch.rider', string='Drop Off Rider')
    pickup_rider= fields.Many2one('despatch.rider', string='Pick up Rider')
    reference = fields.Char(string='Reference')
    status_id = fields.Many2one('delivery.status', string='Status', readonly=True, copy=False)
    pickup_location = fields.Char(string='Pickup Location')
    delivery_location = fields.Char(string='Delivery Location')
    pickup_number = fields.Char('Pick up Number')
    delivery_number = fields.Char('Delivery Number')
    item_description = fields.Char('Item Description')
    #delivery_type_id = fields.Many2one('delivery.type', string='Delivery Type')
    delivery_type = fields.Selection([('local','Local Delivery'),('state','Inter-state Delivery'),('international','International Delivery'),('special','Special Delivery')], default='local', required=True)
    payment_mode_id = fields.Many2one('delivery.payment.mode', string='Payment Mode')
    payment_status = fields.Selection([('not_paid','Not Paid'),('paid', 'Paid')], string='Payment Status', required=True, copy=False, default='not_paid')
    amount_to_collect = fields.Float('Amount to collect')
    third_party_company = fields.Char('Third-Party Company')
    third_party_info = fields.Char('Third-Party Tracking no')
    delivery_fee = fields.Float('Delivery Fee')
    state = fields.Selection([('open', 'New'), ('confirm', 'Confirmed')], string='Status', required=True, readonly=True, copy=False, default='open')
    status = fields.Selection([('ready_pick', 'Ready for Pickup'), ('pick', 'Picked up'),('out','Out for Delivery'),('deliver','Delivered'),('not_deliver','Not Delivered'),('cancel','Cancelled'),('pend','Pending'),('next','Next Day'),('return', 'Returned')], string='Status', required=True, readonly=True, copy=False, default='ready_pick')
    weight = fields.Float('Weight (KG)')
    duration = fields.Integer(readonly=True)
    user_id = fields.Many2one('res.users', string='Created by', track_visibility='onchange',
        readonly=True, default=lambda self: self.env.user)
    partner_balance = fields.Float(string="Customer Balance",compute=_get_partner_balance, readonly=True)
    #delivery_cost = fields.Float('Delivery Cost')
    
    def invoice(self):
        pass
        
    def button_invoice(self):
        pass
    
    @api.multi
    def confirm_delivery(self):
        for delivery in self:
            if delivery.state != 'open':
                raise UserError(_("Only a draft delivery can be confirmed. Trying to confirm a delivery in state %s.") % delivery.state)
            
            sequence_code = 'delivery.sequence'
            delivery.job_number = self.env['ir.sequence'].next_by_code(sequence_code)
            
            delivery.write({'state':'confirm'})

class delivery_line(models.Model):
    _name = 'delivery.line'
    
    delivery_id = fields.Many2one('delivery', string='Delivery')
    name = fields.Text(string='Description', required=True)
    product_id = fields.Many2one('product.product', string='Product',
        ondelete='restrict', index=True)
    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Product Price'))
    price_subtotal = fields.Float(string='Amount',
        store=True, readonly=True)
    price_subtotal_signed = fields.Float(string='Amount Signed',
        store=True, readonly=True, compute='_compute_price',
        help="Total amount in the currency of the company, negative for credit notes.")
    quantity = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'),
        required=True, default=1)
    discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'),
        default=0.0)
    partner_id = fields.Many2one('res.partner', string='Partner',
        related='delivery_id.partner_id', store=True, readonly=True, related_sudo=False)
    
class delivery_location(models.Model):
    _name = 'delivery.location'
    #string fields
    name = fields.Char('Name')
    desc = fields.Text('Description') 
    location_on_map = fields.Char('Google Map Location')
    
    # Numeric fields: 
    sequence = fields.Integer('Sequence')
    
class delivery_type(models.Model):
    _name = 'delivery.type'
    
    #string fields
    name = fields.Char('Name')
    desc = fields.Text('Description') 
    
    # Numeric fields: 
    sequence = fields.Integer('Sequence')
    
class delivery_payment_mode(models.Model):
    _name = 'delivery.payment.mode'
    
    #string fields
    name = fields.Char('Name')
    desc = fields.Text('Description') 
    
    # Numeric fields: 
    sequence = fields.Integer('Sequence')
    
class delivery_status(models.Model):
    _name = 'delivery.status'
    _order = 'sequence asc'
    
    #string fields
    name = fields.Char('Name')
    desc = fields.Text('Description') 
    
    # Numeric fields: 
    sequence = fields.Integer('Sequence') 
    perc_complete = fields.Float('% Complete', (3, 2)) 
    
    
class despatch_rider(models.Model):
    _name = 'despatch.rider'
    
    name = fields.Char('Name')
    phone = fields.Char('Phone #')
    
    
    
    
    
    
    
    