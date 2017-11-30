from odoo import fields, models, api, _

class product_template(models.Model):
    _inherit = 'product.template'
    
    commission_product_categ_code = fields.Many2one('sales_rep_product_category',string='Product Category Code', help='Specifier code to calucalate commission')