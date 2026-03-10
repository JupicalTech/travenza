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

class CustomerBooking(models.Model):
    _name = 'customer.booking'
    _description = 'Customer Bookings'
    _rec_name = 'sequence'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Char(string='Reference', copy=False, default=lambda self: ('New'))    
    customer_id = fields.Many2one('res.partner', string='Customer')
    source = fields.Char(string='Source')
    destination = fields.Char(string='Destination')
    from_date = fields.Date(string='From')
    to_date = fields.Date(string='To')
    booking_type = fields.Selection([
        ('hotel', 'Hotel'),
        ('flight', 'Flight')
    ], string='Booking Type')
    sales_price = fields.Float(string='Sales Price')
    cost_price = fields.Float(string='Cost Price')
    profit = fields.Float(string='Profit', compute='_compute_profit', store=True)

    booking_status = fields.Selection([
        ('new', 'New'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('delayed', 'Delayed')
    ], string='Status', default='new', tracking=True)

    is_travelling = fields.Boolean(
    string="Currently Travelling",
    compute="_compute_is_travelling",
    store=True
)

    @api.depends('from_date', 'to_date', 'booking_status')
    def _compute_is_travelling(self):
        today = fields.Date.today()
        for rec in self:
            if (
                rec.booking_status == 'confirmed'
                and rec.from_date
                and rec.to_date
                and rec.from_date <= today <= rec.to_date
            ):
                rec.is_travelling = True
            else:
                rec.is_travelling = False

    def action_confirm_booking(self):
        for rec in self:
            rec.booking_status = 'confirmed'

    def action_cancel_booking(self):
        for rec in self:
            rec.booking_status = 'cancelled'

    def action_delay_booking(self):
        for rec in self:
            rec.booking_status = 'delayed'

    @api.depends('sales_price', 'cost_price')
    def _compute_profit(self):
        for record in self:
            record.profit = record.sales_price - record.cost_price

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('sequence', ('New')) == ('New'):
                vals['sequence'] = self.env['ir.sequence'].next_by_code('customer.booking') or ('New')
        return super(CustomerBooking, self).create(vals_list)