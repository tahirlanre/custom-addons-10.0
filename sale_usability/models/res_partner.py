# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo import exceptions

import odoo.addons.decimal_precision as dp

class Partner(models.Model):
    _inherit = 'res.partner'
    
    over_credit = fields.Boolean('Allow Over Credit?')