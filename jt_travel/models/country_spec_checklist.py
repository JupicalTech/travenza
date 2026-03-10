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

class CountrySpecificChecklist(models.Model):
    _name = 'country.specific.checklist'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'country_id'

    country_id = fields.Many2one('res.country', string='Country')
    has_aadhar = fields.Boolean(string='Aadhar Card')
    has_pan = fields.Boolean(string='PAN Card')
    has_passport = fields.Boolean(string='Passport')
    has_photo = fields.Boolean(string='Passport Size Photo')
    has_bank_statement = fields.Boolean(string='Bank Statement')
    has_voter_id = fields.Boolean(string='Voter ID')
