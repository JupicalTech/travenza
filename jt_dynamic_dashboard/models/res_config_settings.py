# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2024-TODAY Jupical Technologies(<http://www.jupical.io>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.io>)
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
from odoo import fields, models, api

class InheritResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    image_size = fields.Integer(string="Image Size")
    gif_size = fields.Integer(string="GIF Icon Size")

    def set_values(self):
        res = super(InheritResConfigSettings, self).set_values()
        sudo = self.env['ir.config_parameter'].sudo()
        sudo.set_param('jt_dynamic_dashboard.image_size', self.image_size)
        sudo.set_param('jt_dynamic_dashboard.gif_size', self.gif_size)
        return res

    @api.model
    def get_values(self):
        res = super(InheritResConfigSettings, self).get_values()
        sudo = self.env['ir.config_parameter'].sudo()
        image_size = sudo.get_param('jt_dynamic_dashboard.image_size')
        gif_size = sudo.get_param('jt_dynamic_dashboard.gif_size')
        res.update(
            image_size=image_size,
            gif_size=gif_size,
        )
        return res