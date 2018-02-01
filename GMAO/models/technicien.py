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

import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from operator import itemgetter
import time
from openerp import models, fields, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
from openerp.tools.translate import _
from openerp import SUPERUSER_ID, api
from openerp import tools
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
import openerp.addons.decimal_precision as dp
import os


class Tech(models.Model):
    _name = 'technicien'

    @api.multi
    def return_action_to_open(self):
        """ This opens the xml view specified in xml_id for the current machine """
        context = self._context.copy()
        if context.get('xml_id'):
            res = self.pool['ir.actions.act_window'].for_xml_id(self._cr, self._uid, 'GMAO', context['xml_id'])
            res['context'] = context
            res['context'].update({'default_intervenant': self.id})
            res['domain'] = [('intervenant', '=', self.id)]
            return res
        return False

    @api.multi
    def _count_all(self):
        intervention_obj = self.env['intervention']
        for r in self:
            r.intervention_count = intervention_obj.search_count([('intervenant', '=', r.id)])

    name = fields.Char(string ='Nom du Technicien')
    photo = fields.Binary('Photo')
    poste = fields.Char(string='Poste Occuper')
    nombre_inver = fields.Integer(string='Nombre d\'intervention')
    intervention_count = fields.Integer(compute=_count_all, string='Intervention')

