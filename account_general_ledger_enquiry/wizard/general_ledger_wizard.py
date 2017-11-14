from odoo import models, api, fields, _


class GeneralLedgerEnquiryWizard(models.TransientModel):
    
    _name = "general.ledger.enquiry.wizard"
    
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.user.company_id,
        string='Company'
    )
    
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries')],
                                   string='Target Moves',
                                   required=True,
                                   default='posted')
    account_id = fields.Many2one('account.account',
        string='Filter accounts', required=True
    )
    
    def _build_contexts(self, data):
        result = {}
        result['state'] = data['target_move'] or ''
        result['date_from'] = data['date_from'] or False
        result['date_to'] = data['date_to'] or False
        result['account_id'] = data['account_id'] or False
        #result['strict_range'] = True if result['date_from'] else False
        #result['show_parent_account'] = True
        return result
        
    @api.multi
    def open_general_ledger_enquiry(self):
        self.ensure_one()
        action = self.env.ref('account_general_ledger_enquiry.action_gl_move_line')
        data = self.read([])[0]
        used_context = self._build_contexts(data)
        self  = self.with_context(used_context)              
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'view_id': action.view_id.id,
            'target': action.target,
            'context': "{'default_account_id': " + str(self.account_id.id) + "}",
            'res_model': action.res_model,
            'domain': [('account_id', '=', self.account_id.id),('date', '>=', self.date_from),('date','<=',self.date_to),('move_id.state','=','posted')],
        }
        result_context = eval(result.get('context','{}')) or {}
        used_context.update(result_context)
        result['context'] = str(used_context)
        return result
        