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

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TravelTeamType(models.Model):
    _name = 'travel.team.type'
    _description = 'Travel Team Type'

    name = fields.Char(string="Type Name")

    @api.constrains('name')
    def _check_duplicate_type(self):
        for rec in self:
            if rec.name:
                clean_name = rec.name.strip()
                duplicate = self.search([
                    ('id', '!=', rec.id), 
                    ('name', '=ilike', clean_name)
                ], limit=1)
                if duplicate:
                    raise ValidationError(f"The Team Type '{clean_name}' already exists. Please select the existing one instead of creating a duplicate.")

class TravelTeam(models.Model):
    _name = 'travel.team'
    _description = 'Travel Team'

    name = fields.Char(string="Team Name")
    team_type_id = fields.Many2one('travel.team.type', string="Team Type")
    
    assigned_user_ids = fields.Many2many(
        'res.users',
        compute='_compute_assigned_user_ids'
    )

    team_leader_id = fields.Many2one('res.users', string='Team Leader', tracking=True)
    member_ids = fields.Many2many(
        'res.users',
        'travel_team_user_rel',
        'team_id',
        'user_id',
        string='Members',
        tracking=True
    )

    @api.depends('member_ids', 'team_leader_id')
    def _compute_assigned_user_ids(self):
        for rec in self:
            # Simply set to empty to allow all users in all teams
            rec.assigned_user_ids = [(6, 0, [])]



    @api.constrains('name')
    def _check_duplicate_name(self):
        for rec in self:
            if rec.name:
                duplicate = self.search([('id', '!=', rec.id), ('name', '=ilike', rec.name)], limit=1)
                if duplicate:
                    raise ValidationError(f"Team name '{rec.name}' already exists.")

