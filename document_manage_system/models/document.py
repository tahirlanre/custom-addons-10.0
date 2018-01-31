from odoo import api, models, fields, _

class document(models.Model):
    _inherit = 'todo.task'
    
    document = fields.Binary('Document')
    document_filename = fields.Char('File name')