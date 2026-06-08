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
import base64
import json
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

try:
    import openpyxl
except ImportError:
    openpyxl = None


class SpreadsheetSpreadsheet(models.Model):
    _inherit = ['spreadsheet.spreadsheet', 'mail.thread', 'mail.activity.mixin']

    lead_id = fields.Many2one(
        'crm.lead',
        string="Lead",
        ondelete='cascade',
        index=True,
    )

    project_id = fields.Many2one(
        'project.project',
        string="Project",
        ondelete='cascade',
        index=True,
    )

    lead_type_id = fields.Many2one(
        'lead.type',
        string="Lead Type",
    )

    available_assignee_ids = fields.Many2many(
        'res.users',
        compute='_compute_available_assignee_ids',
        string="Available Assignees",
    )
    assignee_ids = fields.Many2many(
        'res.users',
        'spreadsheet_spreadsheet_assignee_rel',
        'spreadsheet_id',
        'user_id',
        string="Assignees",
    )
    is_done = fields.Boolean(string="Confirmed?", default=False)

    @api.depends('lead_type_id')
    def _compute_available_assignee_ids(self):
        for rec in self:
            if rec.lead_type_id and rec.lead_type_id.team_ids:
                teams = rec.lead_type_id.team_ids
                users = teams.mapped('member_ids') | teams.mapped('team_leader_id')
                rec.available_assignee_ids = users
            else:
                rec.available_assignee_ids = self.env['res.users']

    @api.onchange('lead_type_id')
    def _onchange_lead_type_id(self):
        self.assignee_ids = [(5, 0, 0)]


    def write(self, vals):
        res = super().write(vals)
        if 'is_done' in vals and vals['is_done']:
            for rec in self:
                if rec.lead_id:
                    project = self.env['project.project'].search([
                        ('lead_id', '=', rec.lead_id.id)
                    ], limit=1)
                    if project:
                        project._sync_confirmed_quotation_lines()
        return res

    @api.constrains('is_done', 'lead_id')
    def _check_single_confirmed_per_lead(self):
        for rec in self:
            if rec.is_done and rec.lead_id:
                others = self.search([
                    ('lead_id', '=', rec.lead_id.id),
                    ('is_done', '=', True),
                    ('id', '!=', rec.id),
                ])
                if others:
                    raise ValidationError("Only one confirmed quotation is allowed per lead.")

    def open_spreadsheet(self):
        action = super().open_spreadsheet()
        action['target'] = 'main'
        return action
    
    def _serial_to_date_str(self, val):
        try:
            serial = float(val)
            if serial > 1000:
                from datetime import date, timedelta
                dt = date(1899, 12, 30) + timedelta(days=int(serial))
                return dt.strftime('%m/%d/%Y')
            return val
        except (ValueError, TypeError):
            return val

    def _parse_spreadsheet_rows(self):
        attachment = self.env['ir.attachment'].sudo().search([
            ('res_model', '=', 'spreadsheet.spreadsheet'),
            ('res_id', '=', self.id),
            ('res_field', '=', 'spreadsheet_binary_data'),
        ], limit=1)

        spreadsheet_data = None

        if attachment:
            raw = attachment.raw
            if raw:
                try:
                    if isinstance(raw, bytes):
                        raw = raw.decode('utf-8')
                    spreadsheet_data = json.loads(raw)
                except Exception:
                    pass

            if not spreadsheet_data and attachment.datas:
                try:
                    decoded = base64.b64decode(attachment.datas)
                    spreadsheet_data = json.loads(base64.decodebytes(decoded).decode('utf-8'))
                except Exception:
                    try:
                        spreadsheet_data = json.loads(base64.b64decode(attachment.datas).decode('utf-8'))
                    except Exception:
                        pass

        if spreadsheet_data is not None:
            self.env.cr.execute("""
                SELECT commands FROM spreadsheet_oca_revision
                WHERE model = 'spreadsheet.spreadsheet' AND res_id = %s
                ORDER BY id ASC
            """, (self.id,))
            revisions = self.env.cr.fetchall()
            for (commands_json,) in revisions:
                try:
                    cmd = json.loads(commands_json)
                    if cmd.get('type') == 'SNAPSHOT':
                        data = cmd.get('data') or cmd.get('snapshot')
                        if data and isinstance(data, dict) and data.get('sheets'):
                            spreadsheet_data = data
                except Exception:
                    pass

        if not spreadsheet_data:
            raise UserError("No spreadsheet data found. Please open the spreadsheet via Edit first.")

        sheets = spreadsheet_data.get('sheets', [])
        if not sheets:
            raise UserError("No sheets found. Please open the spreadsheet via Edit, make any change, then try again.")

        cells = sheets[0].get('cells', {})
        # print("SAMPLE CELLS:", dict(list(cells.items())[:5]))
        # def get_cell_content(cell):
        #     if isinstance(cell, dict):
        #         return str(cell.get('content', '') or '').strip()
        #     elif isinstance(cell, str):
        #         return cell.strip()
        #     return ''

        def get_cell_content(cell):
            if isinstance(cell, dict):
                value = cell.get('content', '') or cell.get('value', '') or ''
                return str(value).strip()
            elif isinstance(cell, str):
                return cell.strip()
            elif isinstance(cell, (int, float)):
                return str(cell)
            return ''

        cell_map = {}
        for cell_ref, cell_data in cells.items():
            row = ''.join(filter(str.isdigit, cell_ref))
            col = ''.join(filter(str.isalpha, cell_ref))
            if row and col:
                cell_map.setdefault(int(row), {})[col] = get_cell_content(cell_data)

        if not cell_map:
            raise UserError("The spreadsheet appears to be empty.")

        header_row = None
        date_col = desc_col = remarks_col = price_col = booked_price_col = vendor_ref_col = mode_of_payment_col = None
        for row_num in sorted(cell_map.keys()):
            row_cells = cell_map[row_num]
            found_desc = False
            for col, val in row_cells.items():
                lower = val.lower().strip()
                if lower == 'description':
                    desc_col = col
                    found_desc = True
                elif lower == 'date':
                    date_col = col
                elif lower in ('remarks', 'remark'):
                    remarks_col = col
                elif lower in ('price', 'amount', 'cost'):
                    price_col = col
                elif lower in ('booked price', 'booked_price', 'booked'):
                    booked_price_col = col
                elif lower in ('vendor reference', 'vendor ref', 'vendor_reference', 'vendor_ref'):
                    vendor_ref_col = col
                elif lower in ('mode of payment', 'payment mode', 'mode_of_payment', 'payment_mode'):
                    mode_of_payment_col = col
            if found_desc:
                header_row = row_num
                break

        if not desc_col:
            raise UserError("No 'Description' column header found in the spreadsheet.")

        def _to_float(v):
            if v is None or v == '':
                return 0.0
            try:
                return float(str(v).replace(',', '').strip())
            except (ValueError, TypeError):
                return 0.0

        rows_raw = {}
        for row_num in sorted(cell_map.keys()):
            if row_num <= header_row:
                continue
            row_cells = cell_map[row_num]
            rows_raw[row_num] = {
                'date': self._serial_to_date_str(row_cells.get(date_col, '')) if date_col else '',
                'description': row_cells.get(desc_col, ''),
                'remarks': row_cells.get(remarks_col, '') if remarks_col else '',
                'price': _to_float(row_cells.get(price_col, '')) if price_col else 0.0,
                'booked_price': _to_float(row_cells.get(booked_price_col, '')) if booked_price_col else 0.0,
                'vendor_reference': row_cells.get(vendor_ref_col, '') if vendor_ref_col else '',
                'mode_of_payment': row_cells.get(mode_of_payment_col, '') if mode_of_payment_col else '',
            }

        last_date = ''
        for row_num in sorted(rows_raw.keys()):
            if rows_raw[row_num]['date']:
                last_date = rows_raw[row_num]['date']
            else:
                rows_raw[row_num]['date'] = last_date

        result = [
            rows_raw[r]
            for r in sorted(rows_raw.keys())
            if rows_raw[r]['description']
        ]
        return result

    def action_create_tasks(self):
        self.ensure_one()
        project = self.project_id
        if not project and self.lead_id:
            project = self.env['project.project'].search(
                [('lead_id', '=', self.lead_id.id)], limit=1
            )
            if project:
                self.sudo().write({'project_id': project.id})

        if not project:
            raise UserError("No project is linked to this spreadsheet or its lead. Cannot create tasks.")


        rows = self._parse_spreadsheet_rows()

        if not rows:
            raise UserError("No data rows found in the 'Description' column of the spreadsheet.")

        existing_names = set(
            self.env['project.task'].sudo().search([
                ('project_id', '=', project.id),
            ]).mapped('name')
        )

        default_lead_type = self.lead_type_id if self.lead_type_id else False
        default_assignees = self.assignee_ids if self.assignee_ids else self.env['res.users']

        wizard_lines = []
        for row in rows:
            if row['description'] in existing_names:
                continue
            line_vals = {
                'date': row['date'],
                'description': row['description'],
                'remarks': row['remarks'],
                'price': row['price'],
                'already_exists': False,
                'lead_type_id': default_lead_type.id if default_lead_type else False,
                'assignee_ids': [(6, 0, default_assignees.ids)] if default_assignees else [(5, 0, 0)],
            }
            wizard_lines.append((0, 0, line_vals))

        if not wizard_lines:
            raise UserError("All rows in this spreadsheet already have tasks created. No new rows to process.")

        wizard = self.env['spreadsheet.task.wizard'].create({
            'spreadsheet_id': self.id,
            'project_id': project.id,
            'line_ids': wizard_lines,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Tasks',
            'res_model': 'spreadsheet.task.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
