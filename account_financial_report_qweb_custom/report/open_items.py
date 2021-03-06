# -*- coding: utf-8 -*-
# © 2018 Tahir Aduragba (SITASYS)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _

class OpenItemsReport(models.TransientModel):
    _inherit = 'report_open_items_qweb'
    
    show_credit_balances_only = fields.Boolean()
    show_debit_balances_only = fields.Boolean()
    receiveable_accounts_only = fields.Boolean()
    payable_accounts_only = fields.Boolean()
    
    @api.multi
    def compute_data_for_report(self):
        self.ensure_one()
        # Compute report data
        self._inject_account_values()
        self._inject_partner_values()
        self._inject_line_values()
        self._inject_line_values(only_empty_partner_line=True)
        self._clean_partners_and_accounts()
        self._compute_partners_and_accounts_cumul()
        if self.show_credit_balances_only:
            self._clean_partners_and_accounts(
                only_delete_account_balance_gt_0=True
            )
        if self.show_debit_balances_only:
            self._clean_partners_and_accounts(
                only_delete_account_balance_lt_0=True
            )
        if self.hide_account_balance_at_0:
            self._clean_partners_and_accounts(
                only_delete_account_balance_at_0=True
            )
        # Compute display flag
        self._compute_has_second_currency()
        # Refresh cache because all data are computed with SQL requests
        self.refresh()
    
    def _clean_partners_and_accounts(self,
                                     only_delete_account_balance_at_0=False,
                                     only_delete_account_balance_gt_0=False,
                                     only_delete_account_balance_lt_0=False):
        """ Delete empty data for
        report_open_items_qweb_partner and report_open_items_qweb_account.

        The "only_delete_account_balance_at_0" value is used
        to delete also the data with cumulative amounts at 0.
        """
        query_clean_partners = """
DELETE FROM
    report_open_items_qweb_partner
WHERE
    id IN
        (
            SELECT
                DISTINCT rp.id
            FROM
                report_open_items_qweb_account ra
            INNER JOIN
                report_open_items_qweb_partner rp
                    ON ra.id = rp.report_account_id
            LEFT JOIN
                report_open_items_qweb_move_line rml
                    ON rp.id = rml.report_partner_id
            WHERE
                ra.report_id = %s
        """
        if only_delete_account_balance_gt_0:
            query_clean_partners += """
            AND (
                rp.final_amount_residual IS NULL
                OR round(rp.final_amount_residual,2) >= 0
                )
            """
        elif only_delete_account_balance_lt_0:
            query_clean_partners += """
            AND (
                rp.final_amount_residual IS NULL
                or round(rp.final_amount_residual,2) <= 0
                )
            """
        elif only_delete_account_balance_at_0:
            query_clean_partners += """
            AND (
                rp.final_amount_residual IS NULL
                OR round(rp.final_amount_residual,2) = 0
                )
            """
        elif not only_delete_account_balance_at_0:
            query_clean_partners += """
            AND rml.id IS NULL
            """
        
        query_clean_partners += """
        )
        """
        params_clean_partners = (self.id,)
        self.env.cr.execute(query_clean_partners, params_clean_partners)
        query_clean_accounts = """
        DELETE FROM
            report_open_items_qweb_account
        WHERE
            id IN
                (
                    SELECT
                        DISTINCT ra.id
                    FROM
                        report_open_items_qweb_account ra
                    LEFT JOIN
                        report_open_items_qweb_partner rp
                            ON ra.id = rp.report_account_id
                    WHERE
                        ra.report_id = %s
                """
        if not only_delete_account_balance_at_0:
            query_clean_accounts += """
            AND rp.id IS NULL
            """
        elif only_delete_account_balance_at_0:
            query_clean_accounts += """
            AND (
                ra.final_amount_residual IS NULL
                OR round(ra.final_amount_residual,2) = 0
                )
            """
        query_clean_accounts += """
        )
        """
        params_clean_accounts = (self.id,)
        self.env.cr.execute(query_clean_accounts, params_clean_accounts)