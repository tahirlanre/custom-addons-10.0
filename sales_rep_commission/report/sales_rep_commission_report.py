# -*- coding: utf-8 -*-
# © 2017 SITAYS (tahirlanre@hotmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields

class sales_rep_commission_report(models.TransientModel):
    
    _name = 'report_sales_rep_commission_qweb'
    
    start_date = fields.Date("Start date")
    end_date = fields.Date("End date")
    sales_rep_code_from = fields.Many2one('sales.rep')
    sales_rep_code_to = fields.Many2one('sales.rep')
    
    sales_rep_report_ids = fields.One2many(comodel_name='report_sales_rep_commission_sr', inverse_name='report_id')
    
    @api.multi
    def print_report(self, xlsx_report):
        self.ensure_one()
        self.compute_data_for_report()
        if xlsx_report:
            report_name=''
        else:
            report_name='sales_rep_commission.report_sales_rep_commission_qweb'

        return self.env['report'].get_action(report_name=report_name,docids=self.ids)
    
    @api.multi
    def compute_data_for_report(self):
        self.ensure_one()
        
        self.inject_sales_rep_values()
        self.inject_line_values()
        
        self.refresh()
        
    def inject_line_values(self):
        query_inject_line="""
        
            INSERT INTO
                report_sales_rep_commission_line
                (
                    report_id,
                    create_uid,
                    create_date,
                    partner_code,
                    partner_name,
                    net_sales,
                    disc_granted,
                    disc_balance,
                    commission,
                    sales_rep_report_id,
                    date,
                    invoice_name,
                    invoice_id,
                    commission_categ 
                )
            SELECT
                    %s AS report_id,
                    %s AS create_uid,
                    NOW() AS create_date,
                    pr.ref,
                    pr.name,
                    a.price_subtotal + a.discount_net_amount,
                    a.discount,
                    (src.discount_allowed - a.discount) as disc_balance,
                    (a.price_subtotal + a.discount_net_amount) * (src.discount_allowed - a.discount)/100 as commission,
	                rs.id,
                    i.date_invoice,
                    i.number,
                    i.id,
	                spc.code
                    from account_invoice_line a
                    left join account_invoice i on (i.id = a.invoice_id)
                    left join res_partner pr on (i.partner_id = pr.id)
                    left join sales_rep sr on (pr.sales_rep_id = sr.id)
                    left join product_product pp on (pp.id = a.product_id)
                    left join product_template pt on (pt.id = pp.product_tmpl_id)
                    left join sales_rep_commission src on (src.sales_rep = sr.id and src.product_category = pt.commission_product_categ_code)
                    left join sales_rep_product_category spc on (spc.id = src.product_category)
                    left join report_sales_rep_commission_sr rs on (rs.sales_rep_id = sr.id)
                    where i.date_invoice >= %s and i.date_invoice <= %s and i.type in ('out_invoice') and i.state in ('paid', 'open')
        
            """
        if self.sales_rep_code_from:
            query_inject_line += """
                    and sr.code >= %s
            """
        if self.sales_rep_code_to:
            query_inject_line += """
                    and sr.code <= %s
            """
        
        query_inject_line += """
            UNION ALL
            SELECT	
                  %s AS report_id,
                  %s AS create_uid,
                  NOW() AS create_date,
                  pr.ref,
                  pr.name,
                  -1 * (a.price_subtotal + a.discount_net_amount),
                  -1 * a.discount,
                  -1 * (src.discount_allowed - a.discount) as disc_balance,
                  -1 * ((a.price_subtotal + a.discount_net_amount) * (src.discount_allowed - a.discount)/100) as commission,
                rs.id,
                  i.date_invoice,
                  i.number,
                  i.id,
                  spc.code
                  from account_invoice_line a
                  left join account_invoice i on (i.id = a.invoice_id)
                  left join res_partner pr on (i.partner_id = pr.id)
                  left join sales_rep sr on (pr.sales_rep_id = sr.id)
                  left join product_product pp on (pp.id = a.product_id)
                  left join product_template pt on (pt.id = pp.product_tmpl_id)
                  left join sales_rep_commission src on (src.sales_rep = sr.id and src.product_category = pt.commission_product_categ_code)
                  left join sales_rep_product_category spc on (spc.id = src.product_category)
                  left join report_sales_rep_commission_sr rs on (rs.sales_rep_id = sr.id)
                  where i.date_invoice >= %s and i.date_invoice <= %s and i.type in ('out_refund') and i.state in ('paid', 'open')
        """
        
        if self.sales_rep_code_from:
            query_inject_line += """
                    and sr.code >= %s
            """
        if self.sales_rep_code_to:
            query_inject_line += """
                    and sr.code <= %s
            """
            
        query_inject_parameters = (
            self.id,
            self.env.uid,
            self.start_date,
            self.end_date,
        )
        
        if self.sales_rep_code_from:
            query_inject_parameters += (self.sales_rep_code_from.code,)
            
        if self.sales_rep_code_to:
            query_inject_parameters += (self.sales_rep_code_to.code,)
        
        query_inject_parameters += (
            self.id,
            self.env.uid,
            self.start_date,
            self.end_date,
        )
        
        if self.sales_rep_code_from:
            query_inject_parameters += (self.sales_rep_code_from.code,)
            
        if self.sales_rep_code_to:
            query_inject_parameters += (self.sales_rep_code_to.code,)
            
        self.env.cr.execute(query_inject_line, query_inject_parameters)
    
    def inject_sales_rep_values(self):
        query_inject_sales_rep = """
        
            WITH 
                lines AS (
                    SELECT
                            %s AS report_id,
                            %s AS create_uid,
                            NOW() AS create_date,
                            a.product_id, a.name, a.quantity as qty, (a.price_subtotal + a.discount_net_amount) as amount,
        	                a.purchase_price * a.quantity as total_cost,
        	                a.margin as profit, 100 * a.margin/NULLIF((a.price_subtotal + a.discount_net_amount),0) as percent_profit,
        		            case when a.purchase_price = 0 then 0
        		                else 100 * a.margin/a.purchase_price end as markup,
                	        a.partner_id as partner_id,
                            pr.sales_rep_id,
                            i.date_invoice, i.number
                            from account_invoice_line a
                            left join account_invoice i on (i.id = a.invoice_id)
                            left join res_partner pr on (i.partner_id = pr.id)
                            left join sales_rep sr on (pr.sales_rep_id = sr.id )
                            where i.date_invoice >= %s and i.date_invoice <= %s and i.type in ('out_invoice') and i.state in ('paid', 'open')
            """
        if self.sales_rep_code_from:
            query_inject_sales_rep += """
                    and sr.code >= %s
            """
        if self.sales_rep_code_to:
            query_inject_sales_rep += """
                    and sr.code <= %s
            """
        query_inject_sales_rep += """
        
                    UNION ALL
                    SELECT	
                            %s AS report_id,
                            %s AS create_uid,
                            NOW() AS create_date,
                            a.product_id, a.name, a.quantity * -1 as qty, (a.price_subtotal + a.discount_net_amount) * -1 as amount,
                    	    a.purchase_price * a.quantity * -1 as total_cost,
                        	a.margin * -1 as profit, 100 * a.margin/NULLIF((a.price_subtotal + a.discount_net_amount),0) as percent_profit,
                            case when a.purchase_price = 0 then 0
                        		else 100 * a.margin/NULLIF(a.purchase_price,0) end as markup,
                        	a.partner_id as partner_id,
                        	pr.sales_rep_id,
                        	i.date_invoice, i.number
                        	from account_invoice_line a
                        	left join account_invoice i on (i.id = a.invoice_id)
                        	left join res_partner pr on (i.partner_id = pr.id)
                        	left join sales_rep sr on (pr.sales_rep_id = sr.id )
                        	where i.date_invoice >= %s and i.date_invoice <= %s and i.type in ('out_refund') and i.state in ('paid', 'open')
              """
        if self.sales_rep_code_from:
            query_inject_sales_rep += """
                    and sr.code >= %s
            """
        if self.sales_rep_code_to:
            query_inject_sales_rep += """
                    and sr.code <= %s
            """
            
        query_inject_sales_rep += """  
          )
            INSERT INTO
                report_sales_rep_commission_sr
                (
                    report_id,
                    create_uid,
                    create_date,
                    sales_rep_id,
                    name,
                    qty,
                    amount,
                    cost,
                    profit,
                    percent_profit,
                    percent_markup
                )
            SELECT
                %s AS report_id,
                %s AS create_uid,
                NOW() as create_date,
                rl.sales_rep_id, sr.name, 
                sum(rl.qty), sum(rl.amount), sum(rl.total_cost), 
                sum(rl.profit), 
                case when sum(rl.amount) = 0 then 0 
                    else 100 * sum(rl.profit)/NULLIF(sum(rl.amount),0) end, 
                case when sum(rl.total_cost) = 0 then 0 
                    else 100 * sum(rl.profit)/NULLIF(sum(rl.total_cost),0) end 
            FROM
                lines rl
                join sales_rep sr on rl.sales_rep_id = sr.id
                where rl.report_id = %s
                group by rl.sales_rep_id, sr.name
        """
        
        query_inject_parameters = (
            self.id,
            self.env.uid,
            self.start_date,
            self.end_date,
        )
        
        if self.sales_rep_code_from:
            query_inject_parameters += (self.sales_rep_code_from.code,)
            
        if self.sales_rep_code_to:
            query_inject_parameters += (self.sales_rep_code_to.code,)
        
        query_inject_parameters += (
            self.id,
            self.env.uid,
            self.start_date,
            self.end_date,
        )
        
        if self.sales_rep_code_from:
            query_inject_parameters += (self.sales_rep_code_from.code,)
            
        if self.sales_rep_code_to:
            query_inject_parameters += (self.sales_rep_code_to.code,)
            
        query_inject_parameters += (
            self.id,            
            self.env.uid,
            self.id,
        )
        self.env.cr.execute(query_inject_sales_rep, query_inject_parameters)

class sales_rep_commission_sr(models.TransientModel):
    
    _name = 'report_sales_rep_commission_sr'
    
    name = fields.Char()
    qty = fields.Float()
    amount = fields.Float()
    cost = fields.Float()
    profit = fields.Float()
    percent_profit = fields.Float()
    percent_markup = fields.Float()
    sales_rep_id = fields.Many2one('sales.rep', index = True)
    

    report_id = fields.Many2one(comodel_name='report_sales_rep_commission_qweb', ondelete='cascade', index=True)
    line_ids = fields.One2many(comodel_name='report_sales_rep_commission_line', inverse_name='sales_rep_report_id')
    
class sales_rep_commission_line(models.TransientModel):
    
    _name = 'report_sales_rep_commission_line'
    
    date = fields.Date('Date')
    partner_code = fields.Char()
    partner_name = fields.Char()
    invoice_name = fields.Char()
    commission_categ = fields.Char()
    #gross_sales = fields.Float()
    #tax = fields.Float()
    net_sales = fields.Float()
    disc_granted = fields.Float()
    disc_balance = fields.Float()
    commission = fields.Float()
    invoice_id = fields.Many2one('account.invoice')
    report_id = fields.Many2one(comodel_name='report_sales_rep_commission_qweb', ondelete='cascade', index=True)
    sales_rep_report_id = fields.Many2one(comodel_name='report_sales_rep_commission_sr', ondelete='cascade', index=True)
    