# -*- coding: utf-8 -*-
# © 2018 SITAYS (sitasyslimited@gmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields

class AssetReport(models.TransientModel):
    
    _name = 'report_asset_register_qweb'
    
    start_date = fields.Date("From purchase date")
    end_date = fields.Date("To purchase date")
    
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
        
        self.refresh()
    
    def inject_asset_cat_values(self):
        query_inject_asset_cat_values = """
            WITH line AS (SELECT
                    %s AS report_id,
                    aa.id AS asset_id,
                    aa.name AS name,
                    aa.category_id AS asset_cat_id,
                    aa.value AS purchase_price,
                    (aa.value -  SUM(adl.amount)) AS book_value,
                    SUM(adl.amount) AS total_depr, 
                    aa.salvage_value as salvage_value,
                    aa.state AS state,
                    aa.date AS date
                    from account_asset_asset aa
                    left join account_asset_depreciation_line adl on adl.asset_id = aa.id
                    where adl.move_check = 'true' or aa.salvage_value > 0
                    GROUP BY aa.id, aa.name
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
            SELECT DISTINCT
                %s AS report_id,
                %s AS create_uid,
                NOW() as create_date,
                ac.id as asset_cat_id,
                ac.name as name,
                sum(l.purchase_price) as total_purchase_price,
                sum(l.total_depr) as total_depr,
                sum(l.book_value) as total_book_value,
                sum(l.salvage_value) as total_salvage_value
            FROM line l
                left join account_asset_category ac on ac.id = l.asset_cat_id
            WHERE l.report_id = %s and l.state = 'open' and l.date >= %s and l.date <= %s
            GROUP BY ac.id
            ORDER BY name
        """
        
        query_inject_parameters = (
            self.id,
            self.id,
            self.env.uid,
            self.id,
            self.start_date,
            self.end_date
        )
        
        self.env.cr.execute(query_inject_asset_cat_values, query_inject_parameters)
        
    def inject_asset_cat_lines(self):
        query_inject_asset_cat_lines = """
            INSERT INTO
                report_asset_register_line(
                    report_id,
                    create_uid,
                    create_date,
                    asset_cat_report_id,
                    description,
                    purchase_date,
                    depr_start_date,
                    purchase_price,
                    book_value
                )
        """
        
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
    asset_id = fields.Many2one('account.asset.asset', index=True)
    
    asset_cat_report_id = fields.Many2one(comodel_name='report_asset_register_cat', ondelete='cascade', index=True)
    report_id = fields.Many2one('report_asset_register_qweb', ondelete='cascade', index=True)
        