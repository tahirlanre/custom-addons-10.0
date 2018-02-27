# -*- coding: utf-8 -*-
# © 2018 SITAYS (sitasysnigeria@gmail.com)from odoo import api, models, fields, _
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _

class res_partner(models.Model):
    _inherit = "res.partner"
    
    tin = fields.Char("Tax Identification No")