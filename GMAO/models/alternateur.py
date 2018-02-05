from openerp import models, fields, api

class alternateur(models.Model):
    _name = 'alternateur'
    name = fields.Char (string=' Type alternateur')
    constr = fields.Char(string='Constructeur')
    