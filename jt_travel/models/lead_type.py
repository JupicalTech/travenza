# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
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

class LeadType(models.Model):
    _name = 'lead.type'
    _description = 'Lead Type'
    _order = 'sequence'

    name = fields.Char(string='Lead Type')
    # team_id = fields.Many2one('travel.team', string='Assigned Team')
    sequence = fields.Integer(string="Sequence", default=10)
    team_ids = fields.Many2many(
        'travel.team',
        'lead_type_travel_team_rel',
        'lead_type_id',
        'team_id',
        string='Assigned Teams'
    )
    is_project_type = fields.Boolean(string='Requires Project')
    tag_ids = fields.Many2many('crm.tag', string='Default Tags')