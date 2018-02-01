from openerp import models, fields, api

class classa(models.Model):
    _name = 'zentest.a'
    name = fields.Char('Document Type')
    zenint = fields.Integer('Integer') 
    classB = fields.Many2one('zentest.b',string = 'Class B')
    
    @api.multi   
    def write(self, vals):
        print "write values : ", vals
        rec = super(classa, self).write(vals)
        self.classB.test_compute()
        return rec

    @api.model  
    def create(self, vals):
        print "create values : ", vals
        rec = super(classa, self).create(vals)
        rec.classB.test_compute()
        return rec


class classb(models.Model):
    _name = 'zentest.b'
    name = fields.Char('Document Type')
    mysum_store = fields.Integer(string = "mysum_store")
    mysum_notstore = fields.Integer(compute = 'test_compute',store=False,string = "mysum_notstore")
    classA_ids = fields.One2many('zentest.a','classB','liste Class B')
    
    #@api.depends('meter', 'date_ser', 'deadlinegar_2')
    
    @api.one
    @api.depends('mysum_store', 'classA_ids')
    def test_compute(self):
        print "argarg", self.id
        res = 0
        for o in self.classA_ids:
            res = res + o.zenint
            print "res : ", o, res
        print res
        self.mysum_store = res
        self.mysum_notstore = res
