#!/usr/bin/python
# -*- coding: utf-8 -*-

import xlwt

from openerp_connection import openerp

import time

tps1 = time.clock()

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-d", "--db", dest="db", default='terp', help="Nom de la base ")
parser.add_option("-U", "--user", dest="user", default='terp', help="User Openerp")
parser.add_option("-W", "--passwd", dest="passwd", default='terp', help="mot de passe Openerp ")
parser.add_option("-H", "--host", dest="host", default='127.0.0.1', help="Adresse  Serveur")
parser.add_option("-p", "--port", dest="port", default='8069', help="port du serveur")
parser.add_option("-P", "--protocole", dest="protocole", default='https', help="protocole http/https")

(options, args) = parser.parse_args()
user = options.user
pwd = options.passwd
base = options.db
host = options.host
port = options.port
prot = options.protocole

connection = openerp(prot + '://', serveur, port, base, user, pwd)
compte_de_banque = connection.search('account.account', [('code', 'like', '51%')], 0, 80000, 'code')
compte_partenaire = connection.search('account.account',
                                      [('code', 'like', '4%'), ('type', 'in', ('payable', 'receivable'))], 0, 80000,
                                      'code')
tva_ids = connection.search('account.account', [('code', 'like', '445%')], 0, 80000, 'code')
compte_retenue = connection.search('account.account', [('code', 'like', '341200%')], 0, 80000, 'code')


class Memoize:
    def __init__(self, fonction):
        self.fonction = fonction
        self.memoized = {}

    def __call__(self, *args):
        try:
            return self.memoized[args]
        except KeyError:
            self.memoized[args] = self.fonction(*args)
            return self.memoized[args]


@Memoize
def reconciliation(move_id):
    """ recherche lettrage """
    retour = {'reconcile_ids': [], 'partial_reconcile_ids': [], 'move_ids': [], 'lettrage': ""}
    line_ids = connection.search('account.move.line', [('move_id', '=', move_id)])
    for line_id in line_ids:
        ligne = connection.read('account.move.line', line_id, ['reconcile_id', 'reconcile_partial_id', 'move_id'])
        if ligne['reconcile_id']:
            rec_ids = connection.search('account.move.line',
                                        [('date', '<=', '31/12/2012'), ('account_id', 'in', compte_partenaire),
                                         ('reconcile_id', '=', ligne['reconcile_id'][0])])
            #print "rec ids ", rec_ids
            for rec_id in rec_ids:
                rec_line = connection.read('account.move.line', rec_id, ['move_id'])
                if rec_line['move_id'][0] not in retour['move_ids'] and rec_line['move_id'][0] != move_id:
                    retour['move_ids'].append(rec_line['move_id'][0])

                retour['lettrage'] = ligne['reconcile_id'][1]
                retour['reconcile_ids'].append(rec_id)

        if ligne['reconcile_partial_id']:
            id_partial_reconcile = ligne['reconcile_partial_id'][0]
            rec_partial_ids = connection.search('account.move.line',
                                                [('date', '<=', '31/12/2012'), ('account_id', 'in', compte_partenaire),
                                                 ('reconcile_partial_id', '=', id_partial_reconcile)])
            total = {'debit': 0, 'credit': 0}
            retour['partial_reconcile_ids'] = {}

            retour['partial_reconcile_ids']['line_ids'] = []
            for rec_partial_id in rec_partial_ids:
                rec_line = connection.read('account.move.line', rec_partial_id, ['move_id', 'debit', 'credit'])
                if rec_line['move_id'][0] not in retour['move_ids'] and rec_line['move_id'][0] != move_id:
                    retour['move_ids'].append(rec_line['move_id'][0])
                total['debit'] = total['debit'] + rec_line['debit']
                total['credit'] = total['credit'] + rec_line['credit']
                retour['lettrage'] = ligne['reconcile_partial_id'][1]
                retour['partial_reconcile_ids']['line_ids'].append(rec_partial_id)
            retour['partial_reconcile_ids']['total'] = total
    return retour


@Memoize
def autres(move_id):
    lignes = []
    line_ids = connection.search('account.move.line', [('move_id', '=', move_id)])
    for line_id in line_ids:
        ligne = connection.read('account.move.line', line_id,
                                ['move_id', 'account_id', 'name', 'debit', 'credit', 'date'])
        ligne['account_id'] = ligne['account_id'][1]
        lignes.append(ligne)
    return lignes


@Memoize
def tva(move_id):
    lignes = []
    line_ids = connection.search('account.move.line', [('date', '<=', '31/12/2012'), ('move_id', '=', move_id),
                                                       ('account_id', 'in', tva_ids)])
    for line_id in line_ids:
        ligne = connection.read('account.move.line', line_id, ['account_id', 'name', 'debit', 'credit', 'date'])
        ligne['account_id'] = ligne['account_id'][1]
        lignes.append(ligne)
    return lignes


@Memoize
def product(move_id):
    lignes = []
    ligne_product_ids = connection.search('account.move.line', [('move_id', '=', move_id)])
    for ligne_product_id in ligne_product_ids:
        ligne_produit = connection.read('account.move.line', ligne_product_id,
                                        ['account_id', 'name', 'debit', 'credit', 'date'])
        ligne_produit['account_id'] = ligne_produit['account_id'][1]
        lignes.append(ligne_produit)
    return lignes


wb = xlwt.Workbook()

Gris = xlwt.easyxf(
    'font: name Times New Roman size 10, color-index black, bold on;pattern: pattern solid, fore-colour grey25',
    num_format_str='#,##0.00')
Ratio = xlwt.easyxf(
    'font: name Times New Roman size 10, color-index black, bold on;pattern: pattern solid, fore-colour grey25',
    num_format_str='#,##0.00%')
Bleu = xlwt.easyxf(
    'font: name Times New Roman size 10, color-index black, bold off;pattern: pattern solid, fore-colour light_blue',
    num_format_str='#,##0.00')
Orange = xlwt.easyxf(
    'font: name Times New Roman size 10, color-index black, bold off;pattern: pattern solid, fore-colour light_orange',
    num_format_str='#,##0.00')
Lettrage = xlwt.easyxf(
    'font: name Times New Roman size 12, color-index black, bold off;pattern: pattern solid, fore-colour ice_blue',
    num_format_str='#,##0.00')
Total = xlwt.easyxf(
    'font: name Times New Roman size 12, color-index black, bold off;pattern: pattern solid, fore-colour sky_blue',
    num_format_str='#,##0.00')
Vert = xlwt.easyxf(
    'font: name Times New Roman size 10, color-index black, bold off;pattern: pattern solid, fore-colour light_green',
    num_format_str='#,##0.00')


def retenue(limit=10):
    row = -1
    used_lines = []
    total = {}
    ws_detail = wb.add_sheet("Retenue")
    ws_detail.col(0).width = 256 * 15
    ws_detail.col(1).width = 256 * 80
    ws_detail.col(2).width = 256 * 50
    ws_detail.col(3).width = 256 * 50
    ws_detail.col(4).width = 256 * 50
    ws_detail.col(5).width = 256 * 50
    ws_detail.col(6).width = 256 * 50
    line_ids = connection.search('account.move.line', [('name', 'ilike', 'retenue de garantie%')], 0, limit,
                                 'date,move_id')

    for line_id in line_ids:

        if line_id not in used_lines:
            ligne = connection.read('account.move.line', line_id)
            row += 1
            if not ligne['account_id'][1] in total:
                total[ligne['account_id'][1]] = {}
                total[ligne['account_id'][1]]['debit'] = ligne['debit']
                total[ligne['account_id'][1]]['credit'] = ligne['credit']
            else:
                total[ligne['account_id'][1]]['debit'] = total[ligne['account_id'][1]]['debit'] + ligne['debit']
                total[ligne['account_id'][1]]['credit'] = total[ligne['account_id'][1]]['credit'] + ligne['credit']
            ws_detail.write(row, 0, ligne['move_id'][1], Gris)
            ws_detail.write(row, 1, ligne['date'], Gris)
            ws_detail.write(row, 2, ligne['account_id'][1], Gris)
            ws_detail.write(row, 3, ligne['name'], Gris)
            ws_detail.write(row, 4, ligne['debit'], Gris)
            ws_detail.write(row, 5, ligne['credit'], Gris)
            other_line_ids = autres(ligne['move_id'][1])
            for other_line in other_line_ids:
                #other_line =   connection.read('account.move.line', other_line_id)
                row += 1
                ws_detail.write(row, 1, other_line['move_id'][1], Vert)
                ws_detail.write(row, 2, other_line['date'], Vert)
                ws_detail.write(row, 3, other_line['account_id'], Vert)
                ws_detail.write(row, 4, other_line['name'], Vert)
                ws_detail.write(row, 5, other_line['debit'], Vert)
                ws_detail.write(row, 6, other_line['credit'], Vert)
                used_lines.append(other_line['id'])
                if not other_line['account_id'] in total:
                    total[other_line['account_id']] = {}
                    total[other_line['account_id']]['debit'] = other_line['debit']
                    total[other_line['account_id']]['credit'] = other_line['credit']
                else:
                    total[other_line['account_id']]['debit'] = total[other_line['account_id']]['debit'] + other_line[
                        'debit']
                    total[other_line['account_id']]['credit'] = total[other_line['account_id']]['credit'] + other_line[
                        'credit']

    row += 1
    cles = total.keys()
    cles.sort()
    for k in cles:
        row += 1
        ws_detail.write(row, 1, 'Total %s' % k, Total)
        ws_detail.write(row, 2, total[k]['debit'], Total)
        ws_detail.write(row, 3, total[k]['credit'], Total)


def detail(limit=10):
    row = -2
    used_lines = []
    total = {}
    ws_detail = wb.add_sheet("Detail 2012")
    ws_detail.col(0).width = 256 * 15
    ws_detail.col(1).width = 256 * 80
    ws_detail.col(2).width = 256 * 50
    ws_detail.col(3).width = 256 * 50
    ws_detail.col(4).width = 256 * 50
    ws_detail.col(5).width = 256 * 50
    ws_detail.col(6).width = 256 * 50
    line_ids = connection.search('account.move.line', [('date', '>=', '01/01/2012'), ('date', '<=', '31/12/2012'),
                                                       ('account_id', 'in', compte_de_banque)], 0, limit, 'move_id')

    for line_id in line_ids:

        if line_id not in used_lines:
            bnk_move_id = []
            ligne = connection.read('account.move.line', line_id)
            bnk_move_id.append(ligne['move_id'][0])
            reconcile = reconciliation(ligne['move_id'][0])
            if reconcile['reconcile_ids'] or reconcile['partial_reconcile_ids']:
                row += 2
                ws_detail.write(row, 0, reconcile['lettrage'], Lettrage)
                ws_detail.write(row, 1, "", Lettrage)
                ws_detail.write(row, 2, "", Lettrage)
                ws_detail.write(row, 3, "", Lettrage)
                row += 1
                if not ligne['account_id'][1] in total:
                    total[ligne['account_id'][1]] = {}
                    total[ligne['account_id'][1]]['debit'] = ligne['debit']
                    total[ligne['account_id'][1]]['credit'] = ligne['credit']
                else:
                    total[ligne['account_id'][1]]['debit'] = total[ligne['account_id'][1]]['debit'] + ligne['debit']
                    total[ligne['account_id'][1]]['credit'] = total[ligne['account_id'][1]]['credit'] + ligne['credit']
                ws_detail.write(row, 0, ligne['date'], Gris)
                ws_detail.write(row, 1, ligne['account_id'][1], Gris)
                ws_detail.write(row, 2, ligne['name'], Gris)
                ws_detail.write(row, 3, ligne['debit'], Gris)
                ws_detail.write(row, 4, ligne['credit'], Gris)

                if reconcile['move_ids']:
                    for move_bnk_line_id in connection.search('account.move.line',
                                                              [('move_id', 'in', reconcile['move_ids']),
                                                               ('date', '>=', '01/01/2012'),
                                                               ('date', '<=', '31/12/2012'),
                                                               ('account_id', 'in', compte_de_banque)], 0, 800000,
                                                              'move_id'):
                        paiement_line = connection.read('account.move.line', move_bnk_line_id)
                        bnk_move_id.append(paiement_line['move_id'][0])
                        used_lines.append(move_bnk_line_id)
                        row += 1
                        #print "ligne de paiement ", paiement_line['account_id'], paiement_line['name'], paiement_line['debit'], paiement_line['credit']
                        ws_detail.write(row, 0, paiement_line['date'], Gris)
                        ws_detail.write(row, 1, paiement_line['account_id'][1], Gris)
                        ws_detail.write(row, 2, paiement_line['name'], Gris)
                        ws_detail.write(row, 3, paiement_line['debit'], Gris)
                        ws_detail.write(row, 4, paiement_line['credit'], Gris)

                        if not paiement_line['account_id'][1] in total:
                            total[paiement_line['account_id'][1]] = {}
                            total[paiement_line['account_id'][1]]['debit'] = paiement_line['debit']
                            total[paiement_line['account_id'][1]]['credit'] = paiement_line['credit']
                        else:
                            total[paiement_line['account_id'][1]]['debit'] = total[paiement_line['account_id'][1]][
                                'debit'] + paiement_line['debit']
                            total[paiement_line['account_id'][1]]['credit'] = total[paiement_line['account_id'][1]][
                                'credit'] + paiement_line['credit']

                if reconcile['reconcile_ids']:
                    ligne_initiales = connection.read('account.move.line', reconcile['reconcile_ids'],
                                                      ['id', 'account_id', 'name', 'debit', 'credit', 'move_id',
                                                       'date'])
                elif reconcile['partial_reconcile_ids']:

                    ligne_initiales = connection.read('account.move.line',
                                                      reconcile['partial_reconcile_ids']['line_ids'],
                                                      ['id', 'account_id', 'name', 'debit', 'credit', 'move_id',
                                                       'date'])
                    row += 1
                    ws_detail.write(row, 0, "Restant du ", Gris)
                    ws_detail.write(row, 1, " ", Gris)
                    ws_detail.write(row, 2, reconcile['partial_reconcile_ids']['total']['debit'], Gris)
                    ws_detail.write(row, 3, reconcile['partial_reconcile_ids']['total']['credit'], Gris)
                    ws_detail.write(row, 4, reconcile['partial_reconcile_ids']['total']['debit'] -
                    reconcile['partial_reconcile_ids']['total']['credit'], Gris)
                for ligne_initiale in ligne_initiales:

                    if ligne_initiale['move_id'][0] not in bnk_move_id:

                        ligne_initiale['account_id'] = ligne_initiale['account_id'][1]
                        if not ligne_initiale['account_id'] in total:
                            total[ligne_initiale['account_id']] = {}
                            total[ligne_initiale['account_id']]['debit'] = ligne_initiale['debit']
                            total[ligne_initiale['account_id']]['credit'] = ligne_initiale['credit']
                        else:
                            total[ligne_initiale['account_id']]['debit'] = total[ligne_initiale['account_id']][
                            'debit'] + ligne_initiale['debit']
                            total[ligne_initiale['account_id']]['credit'] = total[ligne_initiale['account_id']][
                            'credit'] + ligne_initiale['credit']
                        ligne_tvas = tva(ligne_initiale['move_id'][0])
                        row += 1
                        ws_detail.write(row, 0, ligne_initiale['date'], Bleu)
                        ws_detail.write(row, 1, ligne_initiale['account_id'], Bleu)
                        ws_detail.write(row, 2, ligne_initiale['name'], Bleu)
                        ws_detail.write(row, 3, ligne_initiale['debit'], Bleu)
                        ws_detail.write(row, 4, ligne_initiale['credit'], Bleu)

                        for ligne_tva in ligne_tvas:
                            row += 1
                            ws_detail.write(row, 0, ligne_tva['date'], Orange)
                            ws_detail.write(row, 1, ligne_tva['account_id'], Orange)
                            ws_detail.write(row, 2, ligne_tva['name'], Orange)
                            ws_detail.write(row, 3, ligne_tva['debit'], Orange)
                            ws_detail.write(row, 4, ligne_tva['credit'], Orange)

                            if not ligne_tva['account_id'] in total:
                                total[ligne_tva['account_id']] = {}
                                total[ligne_tva['account_id']]['debit'] = ligne_tva['debit']
                                total[ligne_tva['account_id']]['credit'] = ligne_tva['credit']
                            else:
                                total[ligne_tva['account_id']]['debit'] = total[ligne_tva['account_id']]['debit'] + \
                                    ligne_tva['debit']
                                total[ligne_tva['account_id']]['credit'] = total[ligne_tva['account_id']]['credit'] + \
                                    ligne_tva['credit']
                        ligne_products = product(ligne_initiale['move_id'][0])
                        for ligne_product in ligne_products:
                            row += 1
                            ws_detail.write(row, 0, ligne_product['date'], Vert)
                            ws_detail.write(row, 1, ligne_product['account_id'], Vert)
                            ws_detail.write(row, 2, ligne_product['name'], Vert)
                            ws_detail.write(row, 3, ligne_product['debit'], Vert)
                            ws_detail.write(row, 4, ligne_product['credit'], Vert)

                            if not ligne_product['account_id'] in total:
                                total[ligne_product['account_id']] = {}
                                total[ligne_product['account_id']]['debit'] = ligne_product['debit']
                                total[ligne_product['account_id']]['credit'] = ligne_product['credit']
                            else:
                                total[ligne_product['account_id']]['debit'] = total[ligne_product['account_id']][
                                    'debit'] + ligne_product['debit']
                                total[ligne_product['account_id']]['credit'] = total[ligne_product['account_id']][
                                    'credit'] + ligne_product['credit']

    row += 1
    cles = total.keys()
    cles.sort()
    for k in cles:
        row += 1
        ws_detail.write(row, 1, 'Total %s' % k, Total)
        ws_detail.write(row, 2, total[k]['debit'], Total)
        ws_detail.write(row, 3, total[k]['credit'], Total)


def paiement(limit=10):
    ws = wb.add_sheet("Paiement 2012")
    used_lines = []
    total = {}

    row = -2
    line_ids = connection.search('account.move.line', [('date', '>=', '01/01/2012'), ('date', '<=', '31/12/2012'),
                                                       ('account_id', 'in', compte_de_banque)], 0, limit, 'move_id')

    ws.col(0).width = 256 * 80
    ws.col(1).width = 256 * 20
    ws.col(2).width = 256 * 20
    ws.col(3).width = 256 * 20
    ws.col(4).width = 256 * 20
    ws.col(5).width = 256 * 20
    ws.col(6).width = 256 * 20

    for line_id in line_ids:

        if line_id not in used_lines:
            bnk_move_id = []
            ligne = connection.read('account.move.line', line_id)
            bnk_move_id.append(ligne['move_id'][0])
            reconcile = reconciliation(ligne['move_id'][0])
            total_banque = {"debit": 0, "credit": 0}
            total_partenaire = {"debit": 0, "credit": 0}
            total_produit = {"debit": 0, "credit": 0}
            total_tva = {}

            if reconcile['reconcile_ids'] or reconcile['partial_reconcile_ids']:
                row += 2
                if not ligne['account_id'][1] in total:
                    total[ligne['account_id'][1]] = {}
                    total[ligne['account_id'][1]]['debit'] = ligne['debit']
                    total[ligne['account_id'][1]]['credit'] = ligne['credit']
                else:
                    total[ligne['account_id'][1]]['debit'] = total[ligne['account_id'][1]]['debit'] + ligne['debit']
                    total[ligne['account_id'][1]]['credit'] = total[ligne['account_id'][1]]['credit'] + ligne['credit']
                total_banque['debit'] = total_banque['debit'] + ligne['debit']
                total_banque['credit'] = total_banque['credit'] + ligne['credit']

                if reconcile['move_ids']:
                    for move_bnk_line_id in connection.search('account.move.line', [('date', '>=', '01/01/2012'),
                                                                                    ('date', '<=', '31/12/2012'), (
                                'move_id', 'in', reconcile['move_ids']), ('account_id', 'in', compte_de_banque)], 0,
                                800000,
                                'move_id'):
                        paiement_line = connection.read('account.move.line', move_bnk_line_id)
                        bnk_move_id.append(paiement_line['move_id'][0])
                        used_lines.append(move_bnk_line_id)
                        total_banque['debit'] = total_banque['debit'] + paiement_line['debit']
                        total_banque['credit'] = total_banque['credit'] + paiement_line['credit']
                        if not paiement_line['account_id'][1] in total:
                            total[paiement_line['account_id'][1]] = {}
                            total[paiement_line['account_id'][1]]['debit'] = paiement_line['debit']
                            total[paiement_line['account_id'][1]]['credit'] = paiement_line['credit']
                        else:
                            total[paiement_line['account_id'][1]]['debit'] = total[paiement_line['account_id'][1]][
                            'debit'] + paiement_line['debit']
                            total[paiement_line['account_id'][1]]['credit'] = total[paiement_line['account_id'][1]][
                            'credit'] + paiement_line['credit']

                if reconcile['reconcile_ids']:
                    ligne_initiales = connection.read('account.move.line', reconcile['reconcile_ids'],
                                                      ['id', 'account_id', 'name', 'debit', 'credit', 'move_id'])
                    ratio = 0
                elif reconcile['partial_reconcile_ids']:
                    ligne_initiales = connection.read('account.move.line',
                                                      reconcile['partial_reconcile_ids']['line_ids'],
                                                      ['id', 'account_id', 'name', 'debit', 'credit', 'move_id'])
                    debit = reconcile['partial_reconcile_ids']['total']['debit']
                    credit = reconcile['partial_reconcile_ids']['total']['credit']
                    if debit > 0.0001:
                        solde = debit - credit
                        ratio = solde / debit * 100
                    else:
                        solde = credit - debit
                        ratio = solde / credit * 100

                for ligne_initiale in ligne_initiales:
                    if ligne_initiale['move_id'][0] not in bnk_move_id:

                        ligne_initiale['account_id'] = ligne_initiale['account_id'][1]
                        if not ligne_initiale['account_id'] in total:
                            total[ligne_initiale['account_id']] = {}
                            total[ligne_initiale['account_id']]['debit'] = ligne_initiale['debit']
                            total[ligne_initiale['account_id']]['credit'] = ligne_initiale['credit']
                        else:
                            total[ligne_initiale['account_id']]['debit'] = total[ligne_initiale['account_id']][
                                'debit'] + ligne_initiale['debit']
                            total[ligne_initiale['account_id']]['credit'] = total[ligne_initiale['account_id']][
                                'credit'] + ligne_initiale['credit']

                        total_partenaire['debit'] = total_partenaire['debit'] + ligne_initiale['debit']
                        total_partenaire['credit'] = total_partenaire['credit'] + ligne_initiale['credit']
                        ligne_tvas = tva(ligne_initiale['move_id'][0])
                        for ligne_tva in ligne_tvas:
                            if not ligne_tva['account_id'] in total:
                                total[ligne_tva['account_id']] = {}
                                total[ligne_tva['account_id']]['debit'] = ligne_tva['debit']
                                total[ligne_tva['account_id']]['credit'] = ligne_tva['credit']
                                total[ligne_tva['account_id']]['debit-reel'] = ligne_tva['debit'] - (
                                    ligne_tva['debit'] * ratio / 100)
                                total[ligne_tva['account_id']]['credit-reel'] = ligne_tva['credit'] - (
                                    ligne_tva['credit'] * ratio / 100)
                            else:
                                total[ligne_tva['account_id']]['debit'] = total[ligne_tva['account_id']]['debit'] + \
                                    ligne_tva['debit']
                                total[ligne_tva['account_id']]['credit'] = total[ligne_tva['account_id']]['credit'] + \
                                    ligne_tva['credit']
                                total[ligne_tva['account_id']]['debit-reel'] = total[ligne_tva['account_id']][
                                                                                   'debit-reel'] + (
                                                                                   ligne_tva['debit'] - (
                                                                                   ligne_tva[
                                                                                   'debit'] * ratio / 100))
                                total[ligne_tva['account_id']]['credit-reel'] = total[ligne_tva['account_id']][
                                                                                    'credit-reel'] + (
                                                                                    ligne_tva['credit'] - (
                                                                                    ligne_tva[
                                                                                    'credit'] * ratio / 100))

                            #print ligne_tva['account_id'],total[ligne_tva['account_id']]
                            if not ligne_tva['account_id'] in total_tva:
                                total_tva[ligne_tva['account_id']] = {"debit": ligne_tva['debit'],
                                                                      "credit": ligne_tva['credit']}
                            else:
                                total_tva[ligne_tva['account_id']]['debit'] = total_tva[ligne_tva['account_id']][
                                                                                  'debit'] + ligne_tva['debit']
                                total_tva[ligne_tva['account_id']]['credit'] = total_tva[ligne_tva['account_id']][
                                                                                   'credit'] + ligne_tva['credit']

                        ligne_products = product(ligne_initiale['move_id'][0])
                        for ligne_product in ligne_products:
                            total_produit['debit'] = total_produit['debit'] + ligne_product['debit']
                            total_produit['credit'] = total_produit['credit'] + ligne_product['credit']
                            if not ligne_product['account_id'] in total:
                                total[ligne_product['account_id']] = {}
                                total[ligne_product['account_id']]['debit'] = ligne_product['debit']
                                total[ligne_product['account_id']]['credit'] = ligne_product['credit']
                            else:
                                total[ligne_product['account_id']]['debit'] = total[ligne_product['account_id']][
                                                                                  'debit'] + ligne_product['debit']
                                total[ligne_product['account_id']]['credit'] = total[ligne_product['account_id']][
                                                                                   'credit'] + ligne_product['credit']

                ws.write(row, 0, reconcile['lettrage'], Lettrage)
                ws.write(row, 1, "", Lettrage)
                ws.write(row, 2, "", Lettrage)
                ws.write(row, 3, "", Lettrage)

                row += 1
                ws.write(row, 0, "Banque ", Gris)
                ws.write(row, 1, total_banque['debit'], Gris)
                ws.write(row, 2, total_banque['credit'], Gris)
                ws.write(row, 3, total_banque['debit'] - total_banque['credit'], Gris)

                row += 1
                ws.write(row, 0, "Partenaire ", Bleu)
                ws.write(row, 1, total_partenaire['debit'], Bleu)
                ws.write(row, 2, total_partenaire['credit'], Bleu)
                ws.write(row, 3, total_partenaire['debit'] - total_partenaire['credit'], Bleu)

                for k in total_tva.keys():
                    row += 1
                    ws.write(row, 0, k, Orange)
                    ws.write(row, 1, total_tva[k]['debit'], Orange)
                    ws.write(row, 2, total_tva[k]['credit'], Orange)
                    solde_tva = total_tva[k]['debit'] - total_tva[k]['credit']
                    ws.write(row, 3, solde_tva, Orange)
                    solde_prorata_tva = solde_tva - (solde_tva * ratio / 100)
                    if ratio > 0.00001:
                        ws.write(row, 4, solde_prorata_tva, Orange)

                row += 1
                ws.write(row, 0, "Produit ", Vert)
                ws.write(row, 1, total_produit['debit'], Vert)
                ws.write(row, 2, total_produit['credit'], Vert)
                ws.write(row, 3, total_produit['debit'] - total_produit['credit'], Vert)

                if reconcile['partial_reconcile_ids']:
                    row += 1
                    ws.write(row, 0, "Restant du ", Gris)

                    ws.write(row, 1, debit, Gris)
                    ws.write(row, 2, credit, Gris)
                    ws.write(row, 3, solde, Gris)
                    ws.write(row, 5, ratio / 100, Ratio)

    row += 2
    ws.write(row, 0, 'Compte', Total)
    ws.write(row, 1, 'Debit', Total)
    ws.write(row, 2, 'Credit', Total)
    ws.write(row, 3, 'Solde', Total)
    ws.write(row, 4, 'Debit au prorata ', Total)
    ws.write(row, 5, 'Credit au prorata', Total)
    ws.write(row, 6, 'Solde au prorata', Total)
    row += 1
    cles = total.keys()
    cles.sort()
    for k in cles:
        row += 1
        ws.write(row, 0, 'Total %s' % k, Total)
        ws.write(row, 1, total[k]['debit'], Total)
        ws.write(row, 2, total[k]['credit'], Total)
        ws.write(row, 3, total[k]['debit'] - total[k]['credit'], Total)
        if 'debit-reel' in total[k]:
            ws.write(row, 4, total[k]['debit-reel'], Total)
            ws.write(row, 5, total[k]['credit-reel'], Total)
            ws.write(row, 6, total[k]['debit-reel'] - total[k]['credit-reel'], Total)



retenue(10000000)

wb.save("retenue.xls")
tps2 = time.clock()
print(tps2 - tps1)


