from odoo import fields, api, models, _


class stock_picking(models.Model):
    _inherit = 'stock.picking'
    
    origin = fields.Char(
        'Source Document', index=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Reference of the document", required=True)