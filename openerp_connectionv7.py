
import xmlrpclib
import sys



class module(object):
    connection = None

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

                print
                "Sur base %10s module %40s Latest Version %10s Installed Version %10s state %15s " % (
                    dbname, module['name'] + ('' * (20 - len(module['name']))), module['installed_version'],
                    module['latest_version'], module['state']),
                if module['state'] == "installed" and module['installed_version'] != module['latest_version']:
                    print
                    "upgradable"
                elif module['state'] == "uninstalled":
                    print
                    "installable "
                elif module['state'] == "installed":
                    print
                    "up to date "
                else:
                    print
            else:
                print
                "installable "

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
            res = wizard.execute(dbname, uid, pwd, wiz_id, form, 'start')
            print
            "res ", res
        except Exception, e:
            print
            e

    def remove(self, module_name=None, module_id=None):
        objet = self.connection.objet
        dbname = self.connection.dbname
        uid = self.connection.uid
        pwd = self.connection.pwd

        model_data_ids = objet.execute(dbname, uid, pwd, 'ir.model.data', 'search',
                                        [('module', "=", module_name), ('noupdate', '=', False)])

        nbr = len(model_data_ids)
        x = 0
        for model_data_id in model_data_ids:
            x += 1
            print
            "%s/%s" % (x, nbr), model_data_id
            model_data = objet.execute(dbname, uid, pwd, 'ir.model.data', 'read', model_data_id)
            try:
                objet.execute(dbname, uid, pwd, model_data['model'], 'unlink', model_data['res_id'])
            except Exception, e:
                print
                "Erreur Supression ", model_data['model'], e
                pass
            objet.execute(dbname, uid, pwd, 'ir.model.data', 'unlink', [model_data_id])
        objet.execute(dbname, uid, pwd, 'ir.module.module', 'write', module_id, {'state': 'uninstalled'})
        objet.execute(dbname, uid, pwd, 'ir.module.module', 'unlink', module_id)
        print
        "%s removed" % module_name

    def uninstall(self, module_name=None, module_id=None):
        objet = self.connection.objet
        dbname = self.connection.dbname
        uid = self.connection.uid
        pwd = self.connection.pwd
        if not module_id and module_name:
            module_id = objet.execute(dbname, uid, pwd, 'ir.module.module', 'search', [('name', '=', module_name)])
            if module_id:
                module_id = module_id[0]

        if module_id:
            print
            "Module ID ", module_id
            module = objet.execute(dbname, uid, pwd, 'ir.module.module', 'read', module_id)
            module_dependency_ids = objet.execute(dbname, uid, pwd, 'ir.module.module.dependency', 'search',
                                                   [('name', '=', module['name'])])

            if module_dependency_ids:
                for id in module_dependency_ids:
                    module_dependency = objet.execute(dbname, uid, pwd, 'ir.module.module.dependency', 'read', id)
                    dependant = objet.execute(dbname, uid, pwd, 'ir.module.module', 'read',
                                               module_dependency['module_id'][0])
                    if dependant['state'] == 'installed':
                        print
                        "Module", module_dependency['module_id'][1]
                        objet.execute(dbname, uid, pwd, 'ir.module.module', 'button_uninstall',
                                       [module_dependency['module_id'][0]])
                        self.upgrade()
                        print
                        "Uninstall dependance %s " % dependant['name']
            print
            "Uninstall Module  %s " % module['name']
            objet.execute(dbname, uid, pwd, 'ir.module.module', 'button_uninstall', [module_id])
            self.upgrade()
        else:
            return None

    def install(self, module_name=None, module_id=None):
        objet = self.connection.objet
        dbname = self.connection.dbname
        uid = self.connection.uid
        pwd = self.connection.pwd
        self.update_list()
        if not module_id and module_name:
            module_id = objet.execute(dbname, uid, pwd, 'ir.module.module', 'search', [('name', '=', module_name)])
        if module_id:
            if not module_name:
                module = objet.execute(dbname, uid, pwd, 'ir.module.module', 'read', module_id, ['name'])
                module_name = module[0]['name']
            print
            "Install %s " % module_name
            objet.execute(dbname, uid, pwd, 'ir.module.module', 'button_install', module_id)
            objet.execute(dbname, uid, pwd, 'base.module.upgrade', 'upgrade_module', [1])
            print
            "Install %s OK" % module_name
        else:
            return None

    def update_list(self):
        objet = self.connection.objet
        dbname = self.connection.dbname
        uid = self.connection.uid
        pwd = self.connection.pwd
        try:
            res = objet.execute(dbname, uid, pwd, 'base.module.update', 'create', {})
            objet.execute(dbname, uid, pwd, 'base.module.update', 'update_module', [res])

        except Exception, e:
            print
            "Update Error "
            print
            e
            sys.exit(0)

    def clean_all(self):
        objet = self.connection.objet
        dbname = self.connection.dbname
        uid = self.connection.uid
        pwd = self.connection.pwd
        self.update_list()
        self.connection.clean_ir_values()
        self.connection.clean_ir_model_data()
        module_ids = objet.execute(dbname, uid, pwd, 'ir.module.module', 'search', [], 0, 9000)
        for module_id in module_ids:
            module = objet.execute(dbname, uid, pwd, 'ir.module.module', 'read', module_id)
            if module['latest_version'] is None or module['installed_version'].replace(' ', '') == '':
                print
                module['name'], module['installed_version'], module['latest_version'], "ready to remove"
                self.remove(module_name=module['name'], module_id=module_id)
                self.connection.clean_ir_values()
                self.connection.clean_ir_model_data()

    def update_all(self, ):
        objet = self.connection.objet
        dbname = self.connection.dbname
        uid = self.connection.uid
        pwd = self.connection.pwd
        self.update_list()
        module_ids = objet.execute(dbname, uid, pwd, 'ir.module.module', 'search', [('state', '=', 'installed')], 0,
                                    9000)
        for module_id in module_ids:
            module = objet.execute(dbname, uid, pwd, 'ir.module.module', 'read', module_id,
                                    ['installed_version', 'latest_version'])
            if module['latest_version'] is not None and module['installed_version'] is not None and module[
                'installed_version'] != module['latest_version']:
                self.update(module_id=module_id)
        return True

    def update(self, module_name=None, module_id=None, force=None):
        objet = self.connection.objet
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
        print module['state']
        if module['state'] in ('installed', 'to upgrade'):
            objet.execute(dbname, uid, pwd, 'ir.module.module', 'button_immediate_upgrade', [module_id])
            module = objet.execute(dbname, uid, pwd, 'ir.module.module', 'read', module_id)
            print "fin update %s  la version est maintenant %s  " % (module['name'], module['installed_version'])


class openerp(object):
    def __init__(self, protocole="http://", host="127.0.0.1", port="8069", dbname="terp", user="admin", pwd="admin"):
        if protocole not in ('http://', 'https://'):
            raise Exception('Error', 'Protocole non valide')
        self.dbname = dbname
        self.user = user
        self.pwd = pwd
        self.host = host
        self.protocole = protocole
        self.url = protocole + host + ":" + str(port)
        self.server = xmlrpclib.ServerProxy(self.url + '/xmlrpc/common', allow_none=True)
        self.uid = self.server.login(self.dbname, self.user, self.pwd)
        self.objet = xmlrpclib.ServerProxy(self.url + '/xmlrpc/object', allow_none=True)
        self.wizard = xmlrpclib.ServerProxy(self.url + '/xmlrpc/wizard', allow_none=True)
        self.report = xmlrpclib.ServerProxy(self.url + '/xmlrpc/report', allow_none=True)

    def clean_ir_values(self):
        print
        "Clean ir.values"
        values_ids = self.objet.execute(self.dbname, self.uid, self.pwd, 'ir.values', 'search', [], 0, 80000, 'value')
        for value in self.objet.execute(self.dbname, self.uid, self.pwd, 'ir.values', 'read', values_ids):
            if "ir.actions" in value['value']:
                (model, id) = value['value'].split(',')
                res = self.objet.execute(self.dbname, self.uid, self.pwd, model, 'search', [('id', '=', int(id))])
                if not res:
                    print
                    "Supression %s , id : %s" % (model, id)
                    self.objet.execute(self.dbname, self.uid, self.pwd, "ir.values", 'unlink', value['id'])

    def clean_ir_model_data(self):
        print
        "Clean ir.model.data"
        model_ids = self.objet.execute(self.dbname, self.uid, self.pwd, 'ir.model', 'search',
                                        [('model', '!=', 'res_users')])
        models = self.objet.execute(self.dbname, self.uid, self.pwd, 'ir.model', 'read', model_ids, ['model'])
        models.sort(lambda x, y: cmp(x['model'], y['model']))
        for model in models:
            print
            model['model']
            model_data_ids = self.objet.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'search',
                                                 [('model', "=", model['model'])])
            for id in model_data_ids:
                model_data = self.objet.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'read', id,
                                                 ['model', 'res_id'])
                #~ print model['model']
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
                    print
                    "Suppression", self.dbname, id, model_data['model'], model_data['res_id']
                    self.objet.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'unlink', model_data['id'])
                    ir_values_ids = self.objet.execute(self.dbname, self.uid, self.pwd, 'ir.values', 'search', [
                        ('value', "=", "%s,%s" % (model_data['model'], model_data['res_id']))])
                    self.objet.execute(self.dbname, self.uid, self.pwd, 'ir.values', 'unlink', ir_values_ids)

    def __str__(self):
        return '%s [%s]' % (self.url, self.dbname)

    def exec_act(self, module, action):
        return self.objet.execute(self.dbname, self.uid, self.pwd, module, action)

    def execute(self, module, action, ids=None, *args, **kwargs):
        if ids:
            return self.objet.execute(self.dbname, self.uid, self.pwd, module, action, ids, *args, **kwargs)
        else:
            return self.objet.execute(self.dbname, self.uid, self.pwd, module, action, args, kwargs)

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

    def write(self, module, ids, value, context=None):
        return self.objet.execute(self.dbname, self.uid, self.pwd, module, 'write', ids, value, context)


class openerp_db(object):
    def __init__(self, protocole="http://", host="127.0.0.1", port="8069"):
        if protocole not in ('http://', 'https://'):
            raise Exception('Error', 'Protocole non valide')
        self.host = host
        self.protocole = protocole
        self.url = protocole + host + ":" + str(port)
        self.sock = xmlrpclib.ServerProxy(self.url + '/xmlrpc/db')



