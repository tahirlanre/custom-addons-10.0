# -*- coding: utf-8 -*-
# © 2018 SITAYS (sitasyslimited@gmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields

class ar_transaction(models.TransientModel):
    
    _name = 'report_ar_transaction_qweb'
    
    start_date = fields.Date("Start date")
    end_date = fields.Date("End date")
    group_by_partner = fields.Boolean()
    summary = fields.Boolean()
    detailed = fields.Boolean()
    filter_partner_ids = fields.Many2many(comodel_name='res.partner')
    
    line_ids = fields.One2many(comodel_name='report_ar_transaction_qweb_line', inverse_name='report_id')
    partner_ids = fields.One2many(comodel_name='report_ar_transaction_qweb_partner', inverse_name='report_id')
    
    @api.multi
    def print_report(self, xlsx_report):
        self.ensure_one()
        self.compute_data_for_report()
        if xlsx_report:
            report_name=''
        else:
            report_name='ar_transaction.report_ar_transaction_qweb'

        return self.env['report'].get_action(report_name=report_name,docids=self.ids)
    
    @api.multi
    def compute_data_for_report(self):
        self.ensure_one()
        
        if self.group_by_partner:
            self.inject_partner_values()
        
        self.inject_line_values()
        
        self.refresh()
    
    def inject_line_values(self):
        query_inject_line_values="""
        
            INSERT INTO
                report_ar_transaction_qweb_line(
                    report_id,
                    create_uid,
                    create_date,
                    partner_report_id,
                    journal_id,
                    journal_name,
                    date,
                    reference,
                    description,
                    deposit,
                    payment,
                    partner_id
                )
            SELECT
                %s AS report_id,
                %s AS create_uid,
                NOW() AS create_date,
                pr.id,
                cbl.journal_id,
                aj.name,
                cb.payment_date,
                cbl.reference,
                cbl.description,
                cbl.deposit,
                cbl.payment,
                cbl.partner_id
                from account_cashbook_batch_line cbl 
                left join account_cashbook_batch cb on cb.id = cbl.batch_id
                left join account_journal aj on aj.id = cbl.journal_id
                left join report_ar_transaction_qweb_partner pr on pr.id = cbl.partner_id
                where cb.state = 'confirm' and cbl.payment_type = 'ar' and cb.payment_date >= %s and cb.payment_date <= %s
        """
        if self.filter_partner_ids:
            query_inject_line_values += """ and cbl.partner_id in %s"""
          
        query_inject_parameters = (
            self.id,
            self.env.uid,
            self.start_date,
            self.end_date,
        )
        
        if self.filter_partner_ids:
            query_inject_parameters += (tuple(self.filter_partner_ids.ids),)
        
        self.env.cr.execute(query_inject_line_values, query_inject_parameters)
        
    def inject_partner_values(self):
        query_inject_partner_values ="""
                WITH line AS (
                    SELECT
                        %s AS report_id,
                        %s AS create_uid,
                        cbl.partner_id as partner_id,
                        sum(cbl.deposit) as total_deposit,
                        sum(cbl.payment) as total_payment
                        from account_cashbook_batch_line cbl
                        left join account_cashbook_batch cb on cb.id = cbl.batch_id
                        where cbl.payment_type = 'ar' and cb.state = 'confirm' and cb.payment_date >= %s and cb.payment_date <= %s """
        
        if self.filter_partner_ids:
            query_inject_partner_values += """ and cbl.partner_id in %s """
        
        query_inject_partner_values += """
                    group by cbl.partner_id
                )
                INSERT INTO 
                    report_ar_transaction_qweb_partner
                    (
                        report_id,
                        create_uid,
                        create_date,
                        partner_id,
                        partner_name,
                        partner_code,
                        deposit,
                        payment
                    )
                SELECT
                    %s AS report_id,
                    %s AS create_uid,
                    NOW() as create_date,
                    l.partner_id as partner_id,
                    rp.name,
                    rp.ref,
                    l.total_deposit,
                    l.total_payment
                from line l
                    left join res_partner rp on rp.id = l.partner_id
                where report_id = %s
                ORDER BY partner_id
             """
            			
        query_inject_parameters = (
            self.id,
            self.env.uid,
            self.start_date,            
            self.end_date,
        )
        
        if self.filter_partner_ids:
            query_inject_parameters += (tuple(self.filter_partner_ids.ids),)
        
        query_inject_parameters += (
            self.id,
            self.env.uid,
            self.id
        )
        
        self.env.cr.execute(query_inject_partner_values, query_inject_parameters)
        
class ar_transaction_line(models.TransientModel):
    
    _name = 'report_ar_transaction_qweb_line'
    
    journal_id = fields.Many2one('account.journal', index = True)
    move_id = fields.Many2one('account.move', index = True)
    journal_name = fields.Char()
    partner_id = fields.Many2one('res.partner', index = True)
    deposit = fields.Float()
    payment = fields.Float()
    reference = fields.Char()
    description = fields.Char()
    date = fields.Date()
    
    report_id = fields.Many2one(comodel_name='report_ar_transaction_qweb', ondelete='cascade', index = True)
    partner_report_id = fields.Many2one(comodel_name='report_ar_transaction_qweb_partner', ondelete='cascade', index=True)
    
class ar_transaction_partner(models.TransientModel):
    
    _name = 'report_ar_transaction_qweb_partner'
    
    partner_id = fields.Many2one('res.partner', index = True)   
    partner_name = fields.Char()
    partner_code = fields.Char() 
    deposit = fields.Float()
    payment = fields.Float()
    
    report_id = fields.Many2one(comodel_name='report_ar_transaction_qweb', ondelete='cascade', index = True)
    line_ids = fields.One2many(comodel_name='report_ar_transaction_qweb_line', inverse_name='partner_report_id')