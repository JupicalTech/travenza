# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies Pvt. Ltd.(<https://www.jupical.io>).
#    Author: Jupical Technologies Pvt. Ltd.(<https://www.jupical.io>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields

class ResCurrency(models.Model):
    _inherit = 'res.currency'

    def name_search(self, name='', domain=None, operator='ilike', limit=100):
        priority_codes = ['INR', 'USD', 'EUR']

        priority_recs = self.search([('name', 'in', priority_codes), ('active', '=', True)])
        priority_results = sorted(
            [(r.id, r.name) for r in priority_recs],
            key=lambda r: priority_codes.index(r[1]) if r[1] in priority_codes else len(priority_codes)
        )

        rest = super().name_search(name=name, domain=domain, operator=operator, limit=limit)
        priority_ids = {r[0] for r in priority_results}
        rest = [r for r in rest if r[0] not in priority_ids]

        return priority_results + rest