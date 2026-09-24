# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies Pvt. Ltd.(<https://www.jupical.io>).
#    Author: Jupical Technologies Pvt. Ltd.(<https://www.jupical.io>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields
from odoo.exceptions import UserError


class TravelBillingRefundWizard(models.TransientModel):
    _name = 'travel.billing.refund.wizard'
    _description = 'Mark Billing Refunded'

    billing_id = fields.Many2one('travel.billing', ondelete='cascade')
    reason = fields.Text(string="Refund Reason")

    def action_apply(self):
        self.ensure_one()
        if not self.reason:
            raise UserError("Refund Reason is required.")
        self.billing_id.write({
            'state': 'refunded',
            'refund_reason': self.reason,
        })
        self._notify_accounts_team()

    def _notify_accounts_team(self):
        billing = self.billing_id
        accounts_teams = self.env['travel.team'].search([
            ('team_type_id.name', '=ilike', 'Accounts')
        ])
        users = accounts_teams.team_leader_id | accounts_teams.member_ids
        partners = users.mapped('partner_id')
        if not partners:
            return
        billing.with_context(
            mail_notify_author=True,
            mail_notify_author_mention=True,
        ).message_post(
            body=f"Bill {billing.name} has been marked as Refunded. Reason: {self.reason}",
            partner_ids=partners.ids,
        )