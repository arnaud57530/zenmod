# -*- coding: utf-8 -*-
###############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech-Receptives(<http://www.techreceptives.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################


from openerp import models, fields, api


class Client(models.Model):
    _name = "client"

    name = fields.Char(string="Raison social")
    contact = fields.Char(string="Nom du Contact")
    phone = fields.Char(string="Telephone contact")
    fax = fields.Char(string="Numero Fax")
    adresse = fields.Char(string="Adresse")
    mail = fields.Char(string='Email')
    projet = fields.Many2one('projet',store=True)


