# -*- coding: utf-8 -*-
# © 2017 SITASYS (Tahir <tahirlanre@hotmail.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, models, fields, _

class AccountJournalBatchWizard(models.TransientModel):
    _name = 'account.journal.batch.wizard'