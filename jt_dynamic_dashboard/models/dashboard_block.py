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
from odoo import models, fields, _, api
from odoo.exceptions import ValidationError
from odoo.osv import expression
from ast import literal_eval
import base64
import io
from PIL import Image
import sys


class DashboardBlock(models.Model):
    """Creates the model Dashboard Blocks"""
    _name = "dashboard.block"
    _description = "Dashboard Blocks"

    def get_default_action(self):

        action_id = self.env.ref(
            'jt_dynamic_dashboard.jt_dynamic_dashboard_action')
        if action_id:
            return action_id.id
        return False

    name = fields.Char(string="Name", help='Name of the block',default="New Block")
    field_id = fields.Many2one('ir.model.fields', string='Measured Field',
                               domain="[('store', '=', True), ('model_id', '=', model_id), ('ttype', 'in', ['float','integer','monetary'])]",
                               help='Measured field for the block')
    fa_icon = fields.Selection([
                                ('fa fa-star','Star'),
                                ('fa fa-pencil','Pencil'),
                                ('fa fa-address-book','Address Book'),
                                ('fa fa-user-circle-o','User'),
                                ('fa fa-car','Car'),
                                ('fa fa-book','Book'),
                                ('fa fa-bookmark','Bookmark'),
                                ('fa fa-calendar-plus-o','Calendar'),
                                ('fa fa-check-circle','Check Circle'),
                                ('fa fa-circle','Circle'),

                                ('fa fa-check-square-o','Check Square'),
                                ('fa fa-cloud-upload','Cloud Upload'),
                                ('fa fa-cubes','Cubes'),
                                ('fa fa-eye','Eye'),
                                ('fa fa-folder-open','Folder Open'),
                                ('fa fa-minus','Minus'),
                                ('fa fa-phone','Phone'),
                                ('fa fa-picture-o','Picture'),
                                ('fa fa-plus','Plus'),
                                ('fa fa-server','Server'),

                                ('fa fa-sign-in','Sign In'),
                                ('fa fa-plus-circle','Plus Circle'),
                                ('fa fa-signal','Signal'),
                                ('fa fa-tags','Tags'),
                                ('fa fa-trash','Trash'),
                                ('fa fa-file','File'),
                                ('fa fa-cog','Cog'),
                                ('fa fa-money','Money'),
                                ('fa fa-usd','USD'),
                                ('fa fa-inr','Rupee'),

                                ('fa fa-adjust','Adjust'),
                                ('fa fa-area-chart','Area'),
                                ('fa fa-bars','Bars'),
                                ('fa fa-bell','Bell'),
                                ('fa fa-briefcase','Briefcase'),
                                ('fa fa-calculator','Calculator'),
                                ('fa fa-calendar-o','Calendar 2'),
                                ('fa fa-clock-o','Clock'),
                                ('fa fa-users','Users'),
                                ('fa fa-hourglass-start','Hourglass'),

                                ('fa fa-star-half-o','Star Half'),
                                ('fa fa-sun-o','Sun'),
                                ('fa fa-toggle-on','Toggle'),
                                ('fa fa-archive','Archive'),
                                ('fa fa-envelope-o','Envelope'),
                                ('fa fa-flag','Flag'),
                                ('fa fa-info-circle','Info-Circle'),
                                ('fa fa-commenting-o','Commenting'),
                                ('fa fa-history','History'),
                                ('fa fa-recycle','Recycle'),

                                ('fa fa-chain-broken','Chain'),
                                ('fa fa-paperclip','Paperclip'),
                                ('fa fa-windows','Windows'),
                                ('fa fa-share-alt','Share'),
                                ('fa fa-android','Android'),
                                ('fa fa-superpowers','Superpowers'),
                                ('fa fa-window-restore','Restore'),
                                ('fa fa-podcast','Podcast'),
                                ('fa fa-handshake-o','Handshake'),
                                ('fa fa-window-maximize','Maximize'),
                                ],string="Icon", help='Icon for the block')
    icon_picker = fields.Char(string="Icon Picker")
    graph_size = fields.Selection(
        selection=[("col-lg-4", "Small"), ("col-lg-6", "Medium"),
                   ("col-lg-12", "Large")],
        string="Graph Size", default='col-lg-4', help="Size of the graph")
    operation = fields.Selection(
        selection=[("sum", "Sum"), ("avg", "Average"), ("count", "Count")],
        string="Operation",
        help='Tile Operation that needs to bring values for tile')
    graph_type = fields.Selection(
        selection=[("bar", "Bar"), ("radar", "Radar"), ("pie", "Pie"),
                   ("line", "Line"), ("doughnut", "Doughnut"),("list", "List")],
        string="Chart Type", help='Type of Chart')
    measured_field = fields.Many2one("ir.model.fields", string="Measured Field",
                                     help='Measure field for the chart')
    client_action = fields.Many2one('ir.actions.client',
                                    default=get_default_action,
                                    string="Client Action",
                                    help='Client Action for the dashboard '
                                         'block')
    type = fields.Selection(
        selection=[("graph", "Chart"), ("tile", "Tile")], string="Type",
        help='Type of Block ie, Chart or Tile')
    x_axis = fields.Char(string="X-Axis", help="X-axis for the chart")
    y_axis = fields.Char(string="Y-Axis", help="Y-axis for the chart")
    group_by = fields.Many2one("ir.model.fields", store=True,
                               string="Group by(Y-Axis)",
                               help='Field value for Y-Axis',
                               domain="[('store', '=', True)]")
    tile_color = fields.Char(string="Tile Color", help='Primary Color of Tile')
    tile_color2 = fields.Char(string="Tile Color", help='Primary Color of Tile')

    text_color = fields.Char(string="Text Color", help='Text Color of Tile')
    fa_color = fields.Char(string="Icon Color", help='Icon Color of Tile')
    filter = fields.Char(string="Filter", help='Filter for Tile')
    model_id = fields.Many2one('ir.model', string='Model',
                               help='Model for Tile')
    model_name = fields.Char(related='model_id.model', readonly=True,
                             string="Model Name", help='Model Name of Tile')
    filter_by = fields.Many2one("ir.model.fields", string=" Filter By",
                                help="Filter By for Tile")
    filter_values = fields.Char(string="Filter Values",
                                help="Filter Values for tiles accordingly")
    sequence = fields.Integer(string="Sequence",
                              help="sequence of the dashboard")
    edit_mode = fields.Boolean(default=False, invisible=True,
                               string="Edit Mode", help="Edit mode of the tile")
    tiles_type = fields.Selection([('1','Tile 1'),('3','Tile 2'),('4','Tile 3')], string="Tile Type", default="1")
    optional_tile_color = fields.Char(string="Optional Tile Color", help='Primary Color of Tile')
    is_demo_data = fields.Boolean(string="Demo Data")
    custom_icon = fields.Binary(string="Custom Icon")
    icon_image = fields.Binary(string="Image")
    file_name = fields.Char(string="FileName")
    icon_type = fields.Selection([('custom','Custom'),('default','Default')], default="default", string="Icon Type")

    def get_dashboard_vals(self, action_id, date_from=False, date_to=False):
  
        block_id = []
        for rec in self.env['dashboard.block'].sudo().search(
                [('client_action', '=', int(action_id))]):
            vals = {
                'id': rec.id,
                'name': rec.name,
                'type': rec.type,
                'graph_type': rec.graph_type,
                'icon': rec.fa_icon,
                'cols': rec.graph_size,
                'color': rec.tile_color if rec.tile_color else '#1f6abb;',
                'text_color': rec.text_color if rec.text_color else '#FFFFFF;',
                'icon_color': rec.fa_color if rec.fa_color else '#1f6abb;',
                'tile_color': rec.tile_color if rec.tile_color else '#FFFFFF;',
                'model_name': rec.model_name,
                'measured_field': rec.measured_field.field_description if rec.measured_field else None,
                'y_field': rec.measured_field.name,
                'x_field': rec.group_by.name,
                'operation': rec.operation,
                'tiles_type':rec.tiles_type,
                'optional_tile_color':rec.optional_tile_color,
                'icon_type':rec.icon_type,
                'file_name':rec.file_name,
                'icon_image':rec.icon_image,
            }
            domain = []
            if rec.filter:
                domain = expression.AND([literal_eval(rec.filter)])
            if rec.model_name == 'fleet.lr.entry':
                date_field = 'date' 
            else:
                date_field = 'create_date' 
    

            if date_from:
                domain = expression.AND([domain, [(date_field, '>=', date_from)]])
            if date_to:
                domain = expression.AND([domain, [(date_field, '<=', date_to)]])
           
            if rec.model_name:
                Model = self.env[rec.model_name].sudo()
                if rec.type == 'graph' and rec.group_by and rec.measured_field:
                    data = Model.read_group(
                        domain,
                        [rec.measured_field.name],
                        [rec.group_by.name]
                    )

                    x_axis = []
                    y_axis = []

                    for d in data:
                        group_val = d.get(rec.group_by.name)

                        if isinstance(group_val, tuple):
                            group_val = group_val[1]

                        x_axis.append(group_val)
                        y_axis.append(d.get(rec.measured_field.name, 0))

                    vals.update({'x_axis': x_axis, 'y_axis': y_axis})
                else:
                    if rec.operation == 'count':
                        value = Model.search_count(domain)

                    else:
                        records = Model.search(domain)
                        field_name = rec.measured_field.name if rec.measured_field else False

                        if not field_name:
                            value = 0
                        else:
                            values = records.mapped(field_name)
                            value = sum(v for v in values if isinstance(v, (int, float)))
                    magnitude = 0
                    total = value
                    while abs(total) >= 1000:
                        magnitude += 1
                        total /= 1000.0

                    val = '%.2f%s' % (total, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])
                    vals.update({'value': val})

            block_id.append(vals)

        return block_id

    @api.model
    def get_models(self):
        models = []
        ir_model_records = self.env['ir.model'].search([])
        for model_id in ir_model_records.ids:
            model = self.env['ir.model'].browse(model_id)
            models.append({'id': model.id, 'name': model.name})
        return models

    @api.model
    def get_fields(self, model_id):
        fields_data = []
        if model_id:
            fields_records = self.env['ir.model.fields'].search([
                ('model_id', '=', int(model_id)),
                ('store', '=', True),
                ('ttype', 'in', ['float', 'integer', 'monetary','selection'])
            ])
        else:
            fields_records = self.env['ir.model.fields'].search([])

        for field in fields_records:
            fields_data.append({'id': field.id, 'name': field.name})
        return fields_data

    @api.model
    def get_field_type(self, field_id=None):
        if not field_id or not field_id.isdigit():
            return {'field_type': None, 'field_name': None}
        
        field = self.env['ir.model.fields'].browse(int(field_id))
        if not field.exists():
            return {'field_type': None, 'field_name': None}

        return {'field_type': field.ttype, 'field_name': field.name}

    @api.model
    def groupby_fields(self, model_id):
        fields_data = []
        if model_id:
            fields_records = self.env['ir.model.fields'].search([
                ('model_id', '=', int(model_id)),
                ('store', '=', True),
                ('ttype', 'not in',['one2many','many2one','many2many'])
            ])
        else:
            fields_records = self.env['ir.model.fields'].search([])

        for field in fields_records:
            fields_data.append({'id': field.id, 'name': field.name})
        return fields_data

    @api.onchange('model_id')
    def _onchange_name(self):
        if self.model_id:
            self.name = self.model_id.name
            if self.measured_field or self.group_by:
                self.measured_field = False
                self.group_by = False
            

    @api.onchange('icon_image')
    def onchange_image_name(self):
        for rec in self:
            if rec.icon_image:
                rec.file_name = rec.icon_image

    def update_filename(self):
        for rec in self:
            if rec.icon_image:
                rec.write({'file_name':rec.icon_image})

    @api.constrains('icon_image')
    def check_icon_image_size(self):
        sudo = self.env['ir.config_parameter'].sudo()
        res_image_size = int(sudo.get_param('jt_dynamic_dashboard.image_size')) if sudo.get_param('jt_dynamic_dashboard.image_size') else 2000
        res_gif_size = int(sudo.get_param('jt_dynamic_dashboard.gif_size')) if sudo.get_param('jt_dynamic_dashboard.gif_size') else 5000
        if self.icon_image:
            file_image = base64.b64decode(self.icon_image)
            stream = io.BytesIO(file_image)
            try:
                img = Image.open(stream)
                image_size = sys.getsizeof(file_image) * 0.0009765625
                image_format = img.format
                allowed_formats = ['PNG', 'JPG', 'JPEG', 'GIF']
                if image_format not in allowed_formats:
                    raise ValidationError(_("Only the following image formats are allowed: %s. Uploaded format: %s" % (
                        ', '.join(allowed_formats), image_format)))

                max_size_kb = res_image_size if image_format in ['PNG', 'JPG', 'JPEG'] else res_gif_size if image_format == 'GIF' else None
                if max_size_kb and image_size > max_size_kb:
                    raise ValidationError(_("You can't upload a %s image with a size more than %d KB.\nUploaded Image Size: %.2f KB" % (
                        image_format, max_size_kb, image_size)))

            except (OSError, IOError):
                raise ValidationError(_("Invalid image file. Please upload a valid image in PNG, JPG, JPEG, or GIF format."))


    # def get_lr_financial_total(self, date_from=False, date_to=False, calc_type=False):
    #     if 'fleet.lr.entry' not in self.env:
    #         return 0
            
    #     domain = []
    #     if date_from:
    #         domain.append(('date', '>=', date_from))
    #     if date_to:
    #         domain.append(('date', '<=', date_to))
            
    #     lr_entries = self.env['fleet.lr.entry'].sudo().search(domain)
        
    #     if not lr_entries:
    #         return 0

    #     if calc_type == 'cost':
    #         return sum(lr_entries.mapped('total_cost'))
    #     elif calc_type == 'revenue':
    #         return sum(lr_entries.mapped('total_revenue'))
    #     elif calc_type == 'profit':
    #         return sum(lr_entries.mapped('total_profit'))
            
    #     return 0


