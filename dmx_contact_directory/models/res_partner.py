# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class dmx_contact_directory(models.Model):
#     _name = 'dmx_contact_directory.dmx_contact_directory'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

class res_partner(models.Model):
    _inherit = "res.partner"
    
    business_type = fields.Char(string='Business Type') #change to fields.Many2one
    phone2 = fields.Char(string='Phone 2')
    referral = fields.Char(string='Referral')
    instagram_account = fields.Text(string='Instagram')
    twitter_account = fields.Text(string='Twitter')
    facebook_account = fields.Text(string='Facebook')
    