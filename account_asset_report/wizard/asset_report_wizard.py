# -*- coding: utf-8 -*-
# © 2017 SITAYS (tahirlanre@hotmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields

class AssetRegisterWizard(models.TransientModel):
    _name = "asset.register.wizard"
    
    start_date = fields.Date("From purchase date", required="True")
    end_date = fields.Date("To purchase date", required="True")
    active = fields.Boolean("Active?", default="True")
    
    asset_cat_ids = fields.Many2many(comodel_name='account.asset.category', string="Filter Categories")
    
    @api.multi
    def button_export_pdf(self):
        self.ensure_one()
        return self._export()
        
    def _prepare_report_asset_register(self):
        return {
                    'start_date':self.start_date,
                    'end_date': self.end_date,
                    'filter_asset_cat_ids': [(6, 0, self.asset_cat_ids.ids)],
                    'active': self.active,
                }
    
    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        return self._export(xlsx_report=True)
        
    def _export(self, xlsx_report=False):
        model = self.env['report_asset_register_qweb']
        report = model.create(self._prepare_report_asset_register())
        return report.print_report(xlsx_report)