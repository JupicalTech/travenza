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

class ProjectCreateWizard(models.TransientModel):
    _name = 'project.create.wizard'
    _description = 'Project Creation Wizard'

    name = fields.Char("Project Name")
    package_name = fields.Char("Package Name")
    number_of_passengers = fields.Integer("Number of number_of_passengers")
    destination = fields.Char("Destination")
    travel_date_from = fields.Date("Travel Date From")
    travel_date_to = fields.Date("Travel Date To")
    client_price = fields.Float("Client Selling Price")
    advance_payment = fields.Float("Advance / Payment Received")
    lead_currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id,)

    def action_create_project(self):
        self.ensure_one()

        project = self.env['project.project'].create({
            'name': self.name,
            'package_name': self.package_name,
            'number_of_passengers': self.number_of_passengers,
            'destination': self.destination,
            'travel_date_from': self.travel_date_from,
            'travel_date_to': self.travel_date_to,
            'client_price': self.client_price,
            'advance_payment': self.advance_payment,
            'lead_currency_id': self.lead_currency_id.id,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'view_mode': 'form',
            'res_id': project.id,
            'target': 'current',
        }