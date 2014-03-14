from xml.dom.minidom import parse
import xmlrpclib
import sys


class module(object):
    connection = None

    def __init__(self, connection):
        if not connection:
            raise "Parametre connection vide"
        self.connection = connection

    def upgrade(self):
        wizard = self.connection.wizard
        dbname = self.connection.dbname
        uid = self.connection.uid
        pwd = self.connection.pwd
        wiz_id = wizard.create(dbname, uid, pwd, 'module.upgrade')
        form = {'form': {}, 'id': wiz_id, 'report_type': 'pdf', 'ids': [wiz_id]}
        try:
            wizard.execute(dbname, uid, pwd, wiz_id, form, 'start')
        except Exception, e:
            print e

    def remove(self, module_name=None, module_id=None):
        connection = self.connection
        model_data_ids = connection.search('ir.model.data', [('module', "=", module_name), ('noupdate', '=', False)])
        nbr = len(model_data_ids)
        x = 0
        for model_data_id in model_data_ids:
            x += 1
            print "%s/%s" % (x, nbr), model_data_id
            model_data = connection.read('ir.model.data', model_data_id)
            try:
                connection.unlink(model_data['model'], model_data['res_id'])
            except Exception, e:
                print "Erreur Supression ", model_data['model'], e
                pass
            connection.unlink('ir.model.data', [model_data_id])
        try:
            connection.unlink('ir.module.module', module_id)
        except:
            pass
        print "%s removed" % module_name

    def versioncourante(self, module_name):
        dbname = self.connection.dbname
        connection = self.connection
        module_ids = []
        if module_name != 'all':
            module_id = connection.search('ir.module.module', [('name', '=', module_name)])
            if module_id:
                module_ids.append(module_id[0])
        else:
            module_ids = connection.search('ir.module.module', [], 0, 100000, 'name asc')

        for module_id in module_ids:
            if module_id:
                module = connection.read('ir.module.module', module_id)

                print "Sur base %10s module %40s Latest Version %10s Installed Version %10s state %15s " % (
                    dbname, module['name'] + ('' * (20 - len(module['name']))), module['installed_version'],
                    module['latest_version'], module['state']),
                if module['state'] == "installed" and module['installed_version'] != module['latest_version']:
                    print "upgradable"
                elif module['state'] == "uninstalled":
                    print "installable "
                elif module['state'] == "installed":
                    print "up to date "
                else:
                    print
            else:
                print "installable "

    def uninstall(self, module_name=None, module_id=None):
        connection = self.connection
        objet = self.connection.object
        dbname = self.connection.dbname
        uid = self.connection.uid
        pwd = self.connection.pwd
        if not module_id and module_name:
            module_id = connection.search('ir.module.module', [('name', '=', module_name)])
            if module_id:
                module_id = module_id[0]

        if module_id:
            print "Module ID ", module_id
            module = connection.read('ir.module.module', module_id)
            if module['state'] == 'installed':
                module_dependency_ids = connection.search('ir.module.module.dependency',
                                                          [('name', '=', module['name'])])

                if module_dependency_ids:
                    for module_dependency_id in module_dependency_ids:
                        module_dependency = connection.read('ir.module.module.dependency', [module_dependency_id])
                        if module_dependency:
                            module_dependency = module_dependency[0]

                        dependant = connection.read('ir.module.module', [module_dependency['module_id'][0]])
                        if dependant:
                            dependant = dependant[0]
                            if dependant['state'] == 'installed':
                                print "Module", module_dependency['module_id'][1]
                                self.uninstall(module_id=module_dependency['module_id'][0])
                                self.upgrade()
                                print "Uninstall dependance %s " % dependant['name']

                group_model_ids = connection.search('ir.model.data',
                                                    [('model', '=', 'res.groups'), ('module', '=', module['name'])])
                group_ids = []
                for group_model_id in group_model_ids:
                    data = connection.read('ir.model.data', [group_model_id])
                    if data and data[0] and data[0]['res_id']:
                        group_ids.append(data[0]['res_id'])
                if group_ids:
                    connection.write('res.groups', group_ids, {'users': [(6, 0, [])]})
                print "Uninstall Module  %s " % module['name']
                objet.execute(dbname, uid, pwd, 'ir.module.module', 'button_uninstall', [module_id])
                self.upgrade()
        else:
            return None

    def install(self, module_name=None, module_id=None):
        objet = self.connection.object
        wizard = self.connection.wizard
        dbname = self.connection.dbname
        uid = self.connection.uid
        pwd = self.connection.pwd
        self.update_list()
        if not module_id and module_name:
            module_id = self.connection.search('ir.module.module',
                                               [('name', '=', module_name), ('state', '!=', 'installed')])
            if module_id:
                module_id = module_id[0]
        if module_id:
            objet.execute(dbname, uid, pwd, 'ir.module.module', 'button_install', [module_id])
            form = {'form': {}, 'id': module_id, 'report_type': 'pdf', 'ids': [module_id]}
            wiz_id = wizard.create(dbname, uid, pwd, 'module.upgrade.simple')
            print " Install %s " % module_name
            try:
                wizard.execute(dbname, uid, pwd, wiz_id, form, 'start')
            except Exception, e:
                print e
            print " Install %s OK" % module_name
        else:
            return None

    def update_list(self):
        wizard = self.connection.wizard
        dbname = self.connection.dbname
        uid = self.connection.uid
        pwd = self.connection.pwd
        connection = self.connection
        menu_id = connection.search('ir.ui.menu', [('name', '=', 'Update Modules List')])
        if menu_id:
            form = {'form': {'repositories': False}, 'ids': menu_id, 'report_type': 'pdf', 'model': 'ir.ui.menu',
                    'id': menu_id[0]}
            wiz_id = wizard.create(dbname, uid, pwd, 'module.module.update')
            try:
                wizard.execute(dbname, uid, pwd, wiz_id, form, 'update')
                print "Update list ok "
            except Exception, e:
                print "Update Error "
                print e
                sys.exit(0)

    def clean_all(self):
        connection = self.connection
        self.update_list()
        self.connection.clean_ir_values()
        self.connection.clean_ir_model_data()
        module_ids = connection.search('ir.module.module', [], 0, 9000)
        for module_id in module_ids:
            module = connection.read('ir.module.module', module_id)
            if module['latest_version'] is None or module['installed_version'].replace(' ', '') == '':
                print
                module['name'], module['installed_version'], module['latest_version'], "ready to remove"
                self.remove(module_name=module['name'], module_id=module_id)
                self.connection.clean_ir_values()
                self.connection.clean_ir_model_data()
        print
        "Clean OK"

    def update_all(self, ):
        connection = self.connection
        self.update_list()
        module_ids = connection.search('ir.module.module', [('state', '=', 'installed')], 0, 9000)
        for module_id in module_ids:
            module = connection.read('ir.module.module', module_id, ['installed_version', 'latest_version'])
            if module['latest_version'] is not None and module['installed_version'] is not None and module[
                'installed_version'] != module['latest_version']:
                self.update(module_id=module_id)
        return True

    def update(self, module_name=None, module_id=None, force=None):
        objet = self.connection.object
        wizard = self.connection.wizard
        dbname = self.connection.dbname
        uid = self.connection.uid
        pwd = self.connection.pwd
        if not module_id and module_name:
            module_id = objet.execute(dbname, uid, pwd, 'ir.module.module', 'search', [('name', '=', module_name)])
            if module_id:
                module_id = module_id[0]

        module = objet.execute(dbname, uid, pwd, 'ir.module.module', 'read', module_id)
        print "Module %s Latest Version %s Installed Version %s " % (
            module['name'], module['installed_version'], module['latest_version'])
        if module['state'] == 'installed':
            if (module['latest_version'] is not None and module['installed_version'] is not None and (
                module['installed_version'] != module['latest_version'])) or force:
                objet.execute(dbname, uid, pwd, 'ir.module.module', 'button_upgrade', [module_id])
                form = {'form': {}, 'id': module_id, 'report_type': 'pdf', 'ids': [module_id]}
                wiz_id = wizard.create(dbname, uid, pwd, 'module.upgrade')
                try:
                    wizard.execute(dbname, uid, pwd, wiz_id, form, 'start')
                except Exception, e:
                    print "-" * 50
                    print "Update Module Error %s " % module['name']
                    print e
                    print "-" * 50
                module = objet.execute(dbname, uid, pwd, 'ir.module.module', 'read', module_id)
                print "fin update %s  la version est maintenant %s  " % (module['name'], module['installed_version'])


class openerp(object):
    def __init__(self, protocole="http://", host="127.0.0.1", port="8069", dbname="terp", user="admin", pwd="admin",
                 otp=None):
        if protocole not in ('http://', 'https://'):
            raise Exception('Error', 'Protocole non valide')
        self.dbname = dbname
        self.user = user
        self.pwd = pwd
        self.host = host
        self.protocole = protocole
        self.otp = otp
        self.url = protocole + host + ":" + str(port)
        self.server = xmlrpclib.ServerProxy(self.url + '/xmlrpc/common', allow_none=True)
        self.uid = self.server.login(self.dbname, self.user, self.pwd, otp)
        self.objet = xmlrpclib.ServerProxy(self.url + '/xmlrpc/object', allow_none=True)
        self.wizard = xmlrpclib.ServerProxy(self.url + '/xmlrpc/wizard', allow_none=True)
        self.report = xmlrpclib.ServerProxy(self.url + '/xmlrpc/report', allow_none=True)

    def logout(self):
        self.uid = self.server.logout(self.dbname, self.user, self.pwd)

    def clean_ir_values(self):
        print "Clean ir.values"
        values_ids = self.objet.execute(self.dbname, self.uid, self.pwd, 'ir.values', 'search', [], 0, 80000, 'value')
        for value in self.objet.execute(self.dbname, self.uid, self.pwd, 'ir.values', 'read', values_ids):
            if "ir.actions" in value['value']:
                (model, id) = value['value'].split(',')
                res = self.objet.execute(self.dbname, self.uid, self.pwd, model, 'search', [('id', '=', int(id))])
                if not res:
                    print "Supression %s , id : %s" % (model, id)
                    self.objet.execute(self.dbname, self.uid, self.pwd, "ir.values", 'unlink', value['id'])

    def clean_ir_model_data(self):
        print "Clean ir.model.data"
        model_ids = self.objet.execute(self.dbname, self.uid, self.pwd, 'ir.model', 'search',
                                        [('model', '!=', 'res_users')])
        models = self.objet.execute(self.dbname, self.uid, self.pwd, 'ir.model', 'read', model_ids, ['model'])
        models.sort(lambda x, y: cmp(x['model'], y['model']))
        for model in models:
            print model['model']
            model_data_ids = self.objet.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'search',
                                                 [('model', "=", model['model'])])
            for model_data_id in model_data_ids:
                model_data = self.objet.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'read', model_data_id,
                                                 ['model', 'res_id'])

                try:
                    if "active" in self.objet.execute(self.dbname, self.uid, self.pwd, model_data['model'],
                                                       'fields_get'):
                        recherche = [('id', '=', model_data['res_id']), ('active', 'in', ('True', 'False'))]
                    else:
                        recherche = [('id', '=', model_data['res_id'])]
                except:
                    pass
                res = False
                try:
                    res = self.objet.execute(self.dbname, self.uid, self.pwd, model_data['model'], 'search', recherche)
                except:
                    pass
                if not res:
                    print "Suppression", self.dbname, model_data_id, model_data['model'], model_data['res_id']
                    self.objet.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'unlink', model_data['id'])
                    ir_values_ids = self.objet.execute(self.dbname, self.uid, self.pwd, 'ir.values', 'search', [
                        ('value', "=", "%s,%s" % (model_data['model'], model_data['res_id']))])
                    self.objet.execute(self.dbname, self.uid, self.pwd, 'ir.values', 'unlink', ir_values_ids)

    def __str__(self):
        return '%s [%s]' % (self.url, self.dbname)

    def exec_act(self, module, action, context=None):
        return self.objet.execute(self.dbname, self.uid, self.pwd, module, action, context)

    def execute(self, module, action, ids=None, context=None):
        return self.objet.execute(self.dbname, self.uid, self.pwd, module, action, ids, context)

    def search(self, module, pattern=None, offset=0, limit=9999999, order=False, context=None):
        if not pattern:
            pattern = []
        return self.objet.execute(self.dbname, self.uid, self.pwd, module, 'search', pattern, offset, limit, order,
                                   context)

    def browse(self, module, ids, fields=None):
        return self.objet.execute(self.dbname, self.uid, self.pwd, module, 'browse', ids, fields)

    def read(self, module, ids, fields=None, context=None):
        return self.objet.execute(self.dbname, self.uid, self.pwd, module, 'read', ids, fields, context)

    def readall(self, module, fields=None, context=None):
        ids = self.objet.execute(self.dbname, self.uid, self.pwd, module, 'search', [], 0, 10000000, 'name')
        return self.objet.execute(self.dbname, self.uid, self.pwd, module, 'read', ids, fields, context)

    def unlink(self, module, ids):
        return self.objet.execute(self.dbname, self.uid, self.pwd, module, 'unlink', ids)

    def create(self, module, value):
        return self.objet.execute(self.dbname, self.uid, self.pwd, module, 'create', value)

    def write(self, module, ids, value):
        return self.objet.execute(self.dbname, self.uid, self.pwd, module, 'write', ids, value)


class openerp_db(object):
    def __init__(self, protocole="http://", host="127.0.0.1", port="8069"):
        if protocole not in ('http://', 'https://'):
            raise Exception('Error', 'Protocole non valide')
        self.host = host
        self.protocole = protocole
        self.url = protocole + host + ":" + str(port)
        self.sock = xmlrpclib.ServerProxy(self.url + '/xmlrpc/db')



