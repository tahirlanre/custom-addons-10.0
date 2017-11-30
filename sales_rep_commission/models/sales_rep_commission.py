from odoo import fields, models, api, _

class product_category(models.Model):
    _name = 'sales_rep_product_category'
    
    _sql_constraints = [
            ('sales_rep_product_category_code_uniq', 
             'UNIQUE (code)', 
             'Product category code must be unique!')]

    
    name = fields.Char('Product Category', required=True, index=True)
    code = fields.Char('Code',required=True)
    
class sales_representative(models.Model):
    _name = 'sales_rep_commission'
    
    sales_rep = fields.Many2one('sales.rep',required=True, string='Sales Representative', index=True)
    discount_allowed = fields.Float('Discount Allowed')
    product_category = fields.Many2one('sales_rep_product_category',string='Product Category')