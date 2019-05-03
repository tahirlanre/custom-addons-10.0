# -*- coding: utf-8 -*-
# © 2018 SITAYS (sitasyslimited@gmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields

class AssetReport(models.TransientModel):
    
    _name = 'report_asset_register_qweb'
    
    start_date = fields.Date("From purchase date")
    end_date = fields.Date("To purchase date")
    active = fields.Boolean("Active?")
    filter_asset_cat_ids = fields.Many2many(comodel_name='account.asset.category', string="Filter Categories")
    
    asset_cat_ids = fields.One2many(comodel_name='report_asset_register_cat', inverse_name='report_id')
    asset_cat_line_ids = fields.One2many(comodel_name='report_asset_register_line', inverse_name='report_id')
    
    @api.multi
    def print_report(self, xlsx_report):
        self.ensure_one()
        self.compute_data_for_report()
        if xlsx_report:
            report_name=''
        else:
            report_name='account_asset_report.report_asset_register_qweb'

        return self.env['report'].get_action(report_name=report_name,docids=self.ids)
    
    @api.multi
    def compute_data_for_report(self):
        self.ensure_one() 
        
        self.inject_asset_cat_values()
        
        self.inject_asset_cat_lines()
        
        self.refresh()
    
    def inject_asset_cat_values(self):
        query_inject_asset_cat_values = """
            WITH line AS(SELECT aa.id as id, aa.name as name, aa.value as value, sum(adl.amount) as total, aa.value - sum(adl.amount) as residual, aa.salvage_value as salvage,
            			    aa.state as state, aa.date as date, aa.category_id as categ_id, aa.active as active
            		        FROM account_asset_asset aa
                       		LEFT JOIN account_asset_depreciation_line adl on adl.asset_id = aa.id 
            		   		WHERE adl.depreciation_date <= %s or adl.asset_id is NULL
            		   		GROUP BY aa.id
            		)       
            INSERT INTO
                report_asset_register_cat
                (
                    report_id,
                    create_uid,
                    create_date,
                    asset_cat_id,
                    name,
                    total_purchase_price,
                    total_depr,
                    total_book_value,
                    total_salvage_value
                )
            SELECT 
                %s AS report_id,
                %s AS create_uid,
                NOW() as create_date,
                ac.id as asset_cat_id,
                ac.name as name,
                SUM(l.value),
                SUM(l.total),
                SUM(l.residual),
                sum(l.salvage)
            FROM account_asset_category ac
                left join line l on l.categ_id = ac.id
            WHERE l.state in ('close', 'open') AND l.date >= %s AND l.date <= %s AND l.active = %s"""
            
        if self.filter_asset_cat_ids:
            query_inject_asset_cat_values += """
                    AND ac.id in %s
                """
        query_inject_asset_cat_values += """
            GROUP BY ac.id
            ORDER BY name
        """
        
        query_inject_parameters = (
            self.end_date,
            self.id,
            self.env.uid,
            self.start_date,
            self.end_date,
            self.active,
            )
            
        if self.filter_asset_cat_ids:
            query_inject_parameters += (tuple(self.filter_asset_cat_ids.ids),)
        
        self.env.cr.execute(query_inject_asset_cat_values, query_inject_parameters)
        
    def inject_asset_cat_lines(self):
        query_inject_asset_cat_lines = """
            WITH line AS(SELECT aa.id as id, aa.name as name, aa.value as value, sum(adl.amount) as total, aa.value - sum(adl.amount) as residual, aa.salvage_value as salvage,
            			    aa.state as state, aa.date as date, aa.category_id as categ_id
            		        FROM account_asset_asset aa
                       		LEFT JOIN account_asset_depreciation_line adl on adl.asset_id = aa.id 
            		   		WHERE adl.depreciation_date <= %s or adl.asset_id is NULL
            		   		GROUP BY aa.id
            		)
            INSERT INTO
                report_asset_register_line(
                    report_id,
                    create_uid,
                    create_date,
                    asset_cat_report_id,
                    description,
                    purchase_date,
                    purchase_price,
                    book_value,
                    total_depr,
                    salvage_value,
                    asset_id
                )
            SELECT
                %s AS report_id,
                %s AS create_uid,
                NOW() AS create_date,
                rac.id,
                aa.name,
                aa.date,
                aa.value,
                l.residual,
                l.total,
                l.salvage,
                l.id
            FROM
                account_asset_asset aa
                left join line l on l.id = aa.id
                inner join report_asset_register_cat rac on rac.asset_cat_id = aa.category_id
                WHERE aa.state in ('close', 'open') AND aa.date >= %s AND aa.date <= %s AND aa.active = %s
                
        """
        query_inject_parameters = (
            self.end_date,
            self.id,
            self.env.uid,
            self.start_date,
            self.end_date,
            self.active,
        )
        
        
        print query_inject_asset_cat_lines
        
        self.env.cr.execute(query_inject_asset_cat_lines, query_inject_parameters)
        
class AssetReportCategory(models.TransientModel):
    _name = 'report_asset_register_cat'
    
    name = fields.Char()
    asset_cat_id = fields.Many2one('account.asset.category', index=True)
    total_purchase_price = fields.Float()
    total_depr = fields.Float()
    total_prior_years_depr = fields.Float()
    total_current_year_depr = fields.Float()
    total_current_month_depr = fields.Float()
    total_book_value = fields.Float()
    total_salvage_value = fields.Float()
    
    report_id = fields.Many2one('report_asset_register_qweb', ondelete='cascade', index=True)
    line_ids = fields.One2many(comodel_name='report_asset_register_line', inverse_name='asset_cat_report_id')
    
class AssetReportLines(models.TransientModel):
    _name = 'report_asset_register_line'
    
    code = fields.Char()
    description = fields.Char()
    purchase_date = fields.Date()
    depr_start_date = fields.Date()
    purchase_price = fields.Float()
    total_depr = fields.Float()
    prior_years_depr = fields.Float()
    current_year_depr = fields.Float()
    current_month_depr = fields.Float()
    book_value = fields.Float()
    salvage_value = fields.Float()
    asset_id = fields.Many2one('account.asset.asset', index=True)
    
    asset_cat_report_id = fields.Many2one(comodel_name='report_asset_register_cat', ondelete='cascade', index=True)
    report_id = fields.Many2one('report_asset_register_qweb', ondelete='cascade', index=True)
        