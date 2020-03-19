import re
import sys
import requests
import json
from docassemble.base.util import get_config, DAFile
from datetime import datetime, timedelta

# Busca Key do Cliente
url_base = 'https://agnes-api.preambulo.com.br/api/v1/platform/'


def get_cliente_key(cliente):
    config = get_config('clientes', None)
    return config[cliente]['key']


# Requests para a api.agnes
def get_data_api(endpoint, params, cliente):
    url = url_base + endpoint + '?' + params
    headers = {'content-type': 'application/json',
               'Authorization': 'Bearer ' + get_cliente_key(cliente)}
    try:
        r = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        return e
    return r.json()


# Request set execution completed
def set_interview_completed(cliente, params):
    url = url_base + 'execution?' + params
    headers = {'content-type': 'application/json',
               'Authorization': 'Bearer ' + get_cliente_key(cliente)}
    try:
        r = requests.put(url, headers=headers)
    except requests.exceptions.RequestException as e:
        return e
    return ''


# Validate token
def validate_token(token):
    url = url_base + 'token_validate'
    headers = {'content-type': 'application/json',
               'Authorization': 'Bearer ' + token}
    user = {'token': token}
    try:
        r = requests.post(url, data=json.dumps(user), headers=headers)
    except requests.exceptions.RequestException as e:
        return e
    return r.text


# Gera código de barras para a entrevista.
def get_barcode(typeBarcode='ean', code='1'):
    file = DAFile()
    file.initialize(extension='png')
    EAN = barcode.get_barcode_class(typeBarcode)
    ean = EAN(code, writer=ImageWriter())
    name = ean.save(file.path()[:-4])
    return file

# Busca valor extenso
# Tipo = numerico, monetario, porcentagem


def get_extenso(tipo='numerico', valor='0', cliente=''):
    url = 'https://agnes-api.preambulo.com.br/api/v1/extenso?tipo=' + tipo + '&valor=' + valor
    headers = {'content-type': 'application/json',
               'Authorization': 'Bearer ' + get_cliente_key(cliente)}
    try:
        r = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        return e
    return r.json()


# Contagem de data
def contagem_de_prazos_dias(data, dias_contagem, dias_uteis=False):
    dias_para_adicionar = dias_contagem
    data_ajustada = data
    while dias_para_adicionar > 0:
        data_ajustada += timedelta(days=1)
        dia_semana = data_ajustada.weekday()
        if (dia_semana >= 5) and (not dias_uteis):  # sunday = 6
            continue
        dias_para_adicionar -= 1
    return data_ajustada


# Converter String para date
def str_to_date(date):
    try:
        return datetime.strptime(date, '%d/%m/%Y %H:%M:%S').date()
    except Exception as E:
        return E


# Comparador de datas
'''
  SEQUENCE_COMPARATOR 0 => valida se a primeira data é maior que a segunda
  SEQUENCE_COMPARATOR 1 => valida se a segunda data é maior que a primeira
  SEQUENCE_COMPARATOR 2 => valida se as datas são iguais
'''
def date_compare(date1, date2, sequence_comparator=0):
    try:
        if sequence_comparator == 0:
            return date1 > date2
        elif sequence_comparator == 1:
            return date1 < date2
        elif sequence_comparator == 2:
            return date1 == date2
    except Exception as E:
        return E


'''
  array = Lista de items.
  separator_default = Separa dados até o penultimo item.
  separator_final = Separa os dados do penultimo e ultimo item.
'''
def separatorItems(array, separator_default=',', separator_final=' e '):
    strReturn = ''
    for item in range(len(array)):
        if item == 0:
            strReturn += array[item]
        elif item < len(array) - 1 and item > 0:
            strReturn += separator_default + array[item]
        else:
            strReturn += separator_final + array[item]

    return strReturn


# Send email PTL
def send_email_PTL(email_to, email_cc, email_cco, email_subject, email_body, cliente='', file=None):
    headers = {'Authorization': 'Bearer ' + get_cliente_key(cliente)}
    contentEmail = {
        'email_to': email_to,
        'email_cc': email_cc,
        'email_cco': email_cco,
        'email_subject': email_subject,
        'email_body': email_body
    }
    url = url_base + 'email'
    try:
        if file:
            files = {'file': open(file, 'rb')}
            r = requests.post(url, headers=headers, files=files, data=contentEmail)
        else:
            r = requests.post(url, headers=headers, data=contentEmail)
    except requests.exceptions.RequestException as e:
        return e
    return ''


# Send request
def send_request(url, method='GET', headers={}, data={}):
    try:
        r = requests.request(method, headers=headers, url=url, data=data)
        return r
    except requests.exceptions.RequestException as e:
        return e


def get_UF_extenso(chave):
  dicionario = {
    'AC':{
      'descricao':"ACRE",
      'preposicao':'DO ESTADO DO'
    },
    'AL':{
      'descricao':"ALAGOAS",
      'preposicao':'DO ESTADO DE'
    },
    'AP':{
      'descricao':"AMAPÁ",
      'preposicao':'DO ESTADO DO'
    },
    'AM':{
      'descricao':"AMAZONAS",
      'preposicao':'DO ESTADO DO'
    },
    'BA':{
      'descricao':"BAHIA",
      'preposicao':'DO ESTADO DA'
    },
    'CE':{
      'descricao':"CEARÁ",
      'preposicao':'DO ESTADO DO'
    },
    'DF':{
      'descricao':"DISTRITO FEDERAL",
      'preposicao':'DO'
    },
    'ES':{
      'descricao':"ESPÍRITO SANTO",
      'preposicao':'DO ESTADO DO'
    },
    'GO':{
      'descricao':"GOIÁS",
      'preposicao':'DO ESTADO DE'
    },
    'MA':{
      'descricao':"MARANHÃO",
      'preposicao':'DO ESTADO DO'
    },
    'MT':{
      'descricao':"MATO GROSSO",
      'preposicao':'DO ESTADO DO'
    },         
    'MS':{
      'descricao':"MATO GROSSO DO SUL",
      'preposicao':'DO ESTADO DO'
    },
    'MG':{
      'descricao':"MINAS GERAIS",
      'preposicao':'DO ESTADO DE'
    },
    'PA':{
      'descricao':"PARÁ",
      'preposicao':'DO ESTADO DO'
    },
    'PB':{
      'descricao':"PARAÍBA",
      'preposicao':'DO ESTADO DA'
    },
    'PR':{
      'descricao':"PARANÁ",
      'preposicao':'DO ESTADO DO'
    },
    'PE':{
      'descricao':"PERNAMBUCO",
      'preposicao':'DO ESTADO DE'
    },
    'PI':{
      'descricao':"PIAUÍ",
      'preposicao':'DO ESTADO DO'
    },
    'RJ':{
      'descricao':"RIO DE JANEIRO",
      'preposicao':'DO ESTADO DO'
    },
    'RN':{
      'descricao':"RIO GRANDE DE NORTE",
      'preposicao':'DO ESTADO DO'
    },
    'RS':{
      'descricao':"RIO GRANDE DO SUL",
      'preposicao':'DO ESTADO DO'
    },
    'RO':{
      'descricao':"RONDÔNIA",
      'preposicao':'DO ESTADO DE'
    },
    'RR':{
      'descricao':"RORAIMA",
      'preposicao':'DO ESTADO DE'
    },
    'SC':{
      'descricao':"SANTA CATARINA",
      'preposicao':'DO ESTADO DE'
    },
    'SP':{
      'descricao':"SÃO PAULO",
      'preposicao':'DO ESTADO DE'
    },
    'SE':{
      'descricao':"SERGIPE",
      'preposicao':'DO ESTADO DE'
    },
    'TO':{
      'descricao':"TOCANTINS",
      'preposicao':'DO ESTADO DE'
    }
  }
  return dicionario.get(chave)