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

class CrmLeadExternalLink(models.Model):
    _name = 'crm.lead.external.link'
    _description = 'Lead External Link'
    _order = 'date desc, id desc'

    lead_id = fields.Many2one('crm.lead', ondelete='cascade')
    name = fields.Char(string="Title")
    url = fields.Char(string="URL")
    date = fields.Date(string="Date")

    def action_open_link(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.url,
            'target': 'new',
        }