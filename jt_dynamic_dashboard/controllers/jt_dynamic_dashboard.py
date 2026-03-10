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
from odoo import http
from odoo.http import request


class DynamicDashboard(http.Controller):

    @http.route('/create/tile', type='json', auth='user')
    def tile_creation(self, **kw):
        """This is the method to create the tile when create on the button
        ADD BLOCK"""
        tile_type = kw.get('type')
        action_id = kw.get('action_id')
        color = kw.get('color')
        icon_color = kw.get('icon_color')
        text_color = kw.get('text_color')
        icon = kw.get('icon')
        chart_type = kw.get('chart_type')
        graph_size = kw.get('graph_size')
        model_id = kw.get('model_id')
        operation_type = kw.get('operation_type')
        group_by_field_id = kw.get('group_by_field_id')
        field_id = kw.get('field_id')
        chart_type = kw.get('chart_type')
        request.env['dashboard.block'].get_dashboard_vals(action_id)
        if field_id:
            field_name = request.env['ir.model.fields'].sudo().browse(int(field_id)).name
        else:
            field_name = None

        if group_by_field_id:
            grp_field_name = request.env['ir.model.fields'].sudo().browse(int(group_by_field_id)).name
        else:
            grp_field_name = None

        if model_id:
            model = request.env['ir.model'].sudo().browse(int(model_id)).name
        else:
            model = None

        if tile_type == 'tile':
            tile_id = request.env['dashboard.block'].sudo().create({
                'name':model,
                'type': tile_type,
                'tile_color': color,
                'text_color': text_color,
                'fa_icon': icon or "fa fa-star",
                'fa_color': icon_color,
                'edit_mode': True,
                'client_action': int(action_id),
                'model_id': model_id,
                'measured_field': field_id,
                'operation': operation_type,
            })
            return {'id': tile_id.id, 'name': tile_id.name, 'type': tile_type, 'icon': icon or "fa fa-star",
                    'color': color,
                    'tile_color': color,
                    'text_color': text_color,
                    'icon_color': icon_color,
                    'model_id': model_id,
                    'measured_field': field_id,
                    'operation': operation_type,
                }
        else:
            tile_id = request.env['dashboard.block'].sudo().create({
                'name':model,
                'type': tile_type,
                'tile_color': color,
                'text_color': text_color,
                'fa_icon': icon or "fa fa-star",
                'fa_color': icon_color,
                'edit_mode': True,
                'client_action': int(action_id),
                'model_id': model_id,
                'measured_field': field_id,
                'group_by':group_by_field_id,
                'operation': operation_type,
                'graph_size':graph_size,
                'graph_type':chart_type
            })
            return True


    @http.route('/get/values', type='json', auth='user')
    def get_value(self, **kw):
        action_id = kw.get('action_id')
        date_from = kw.get('date_from')
        date_to = kw.get('date_to')
        
        datas = request.env['dashboard.block'].get_dashboard_vals(
            action_id, 
            date_from=date_from, 
            date_to=date_to
        )
        return datas

    @http.route('/remove/record', type='json', auth='user')
    def remove_record(self, id=None):
        # Check if 'id' is provided and valid
        if id is None:
            return {'success': False, 'error': 'No ID provided'}

        try:
            record = request.env['dashboard.block'].browse(id)
            if record.exists():
                record.unlink()
                return {'success': True}
            else:
                return {'success': False, 'error': 'Record not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/duplicate/record', type='json', auth='user')
    def duplicate_record(self, id):
        try:
            record = request.env['dashboard.block'].browse(id)
            if record.exists():
                record.copy()
                return {'success': True}
            else:
                return {'success': False, 'error': 'Record not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # @http.route('/get/financials', type='json', auth='user')
    # def get_financials(self, **kw):
    #     action_id = kw.get('action_id')
    #     date_from = kw.get('date_from')
    #     date_to = kw.get('date_to')
    #     calc_type = kw.get('calc_type')
        
    #     try:
    #         res = request.env['dashboard.block'].get_lr_financial_total(date_from, date_to, calc_type)
    #         return {'total': res}
    #     except Exception as e:
    #         return {'error': str(e), 'total': 0}



