#
from flask import Flask, request
import os
import requests
from datetime import date


app=Flask(__name__)

processed_messages=set()

current_date=date.today()

set_date=date.today()

###Variáveis de ambiente

VERIFY_TOKEN=os.getenv('VERIFY_TOKEN')

WHATSAPP_TOKEN=os.getenv('WHATSAPP_TOKEN')

ADMIN_PHONE=os.getenv('ADMIN_PHONE')

PHONE_NUMBER_ID=os.getenv('PHONE_NUMBER_ID')

RESPOSTA_AUTOMATICA=os.getenv('RESPOSTA_AUTOMATICA')

###Retorna o estado da resposta automática

print('')

print(f'Resposta Automática: {RESPOSTA_AUTOMATICA}')

###Checagem das variáveis de ambiente

if not all ([VERIFY_TOKEN, WHATSAPP_TOKEN, ADMIN_PHONE,PHONE_NUMBER_ID, RESPOSTA_AUTOMATICA]):

	print('')

	raise RuntimeError('Variáveis de ambientes não configuradas')

###Envia mensagens de texto para um determinado número

def ZAP_TXT(phone,texto):

	url=f'https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages'

	headers={	'Authorization':f'Bearer {WHATSAPP_TOKEN}',

		'Content-Type':'application/json' }

	payload={	'messaging_product':'whatsapp',

		'to':phone,

		'type': 'text',

		'text': { 'body': texto} }

	requests.post(url, json=payload, headers=headers)

###Envia mensagens de media para um determinado número

def MEDIA_ZAP(phone, media_id, media_type, filename):

	url=f'https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages'

	headers={	'Authorization':f'Bearer {WHATSAPP_TOKEN}',

		'Content-Type':'application/json' }

	media_payload={'id': media_id}

	if media_type=='document' and filename:

		media_payload['filename']=filename

	payload={ "messaging_product":"whatsapp",

		"to":phone,

		"type":media_type,

		media_type: media_payload }

	response=requests.post(url, json=payload, headers=headers)

	print('')

	print("Status media:", response.status_code)

	print('')

	print("Resposta:", response.text)

###Cabeçalho do zaphook setando os métodos GET e POST

@app.route('/zaphook', methods=['GET', 'POST'])

def zaphook():	

	###Método get para verificar as chaves de acesso e liberar o recebimento dos pacotes.

	if request.method=='GET':

		verify_token2=request.args.get('hub.verify_token')

		challenge=request.args.get('hub.challenge')

		if VERIFY_TOKEN==verify_token2:

			print('Acesso validado.')

			return challenge

		else:

			return 'Acesso negado', 403

	if request.method=='POST':

		###Verifica se a data atual coincide com a data do set para limpar o set

		global processed_messages

		global set_date

		###Na virada do dia o processer_messages é limpo

		if date.today()!=set_date:

			processed_messages.clear()

			set_date=date.today()

		###Captura e printa o pacote jason	

		data=request.json

		print(data)

		###Qualquer pacote que chega que não seja mensagem é ignorado

		try:

			value=data['entry'][0]['changes'][0]['value']

		except (KeyError, IndexError, TypeError):

			return 'EVENT_RECEIVED', 200

		if 'messages' not in value:

			return 'EVENT_RECEIVED', 200

		###Captura os dados da mensagem e processa

		mensagem=value['messages'][0]			

		message_id=mensagem['id']

		if message_id in processed_messages:

			return 'EVENT_RECEIVED', 200
			
		processed_messages.add(message_id)			

		phone= mensagem['from']

		print('')
				
		print(f'Atividade detectada: {phone}.........................................................................')

		print('')

		texto=('Olá, obrigado por usar o canal oficial da Olive Topografia.\n'

		'Para atendimento clique no link abaixo: \n'

		'https://api.whatsapp.com/send/?phone=5511973354380&text&type=phone_number&app_absent=0')

		###Envia a resposata automática se estivar ativada.

		if RESPOSTA_AUTOMATICA=='ativada':

			ZAP_TXT(phone, texto)

		###Não repassa a mensagem se o pacote vier do admin phone.	

		###Trata mensagens de texto

		if phone!=ADMIN_PHONE and mensagem['type']=='text':

			body=mensagem['text']['body']

			body=f'{phone}: \n{body}'

			ZAP_TXT(ADMIN_PHONE, body)

		###Trata mensagens de midia.	

		if phone!=ADMIN_PHONE and mensagem['type'] in ['audio', 'image', 'video', 'document']:

			filename=None

			media_type=mensagem['type']

			media_id=mensagem[media_type]['id']

			caption=mensagem[media_type].get('caption', '')

			filename=mensagem[media_type].get('filename','')			

			ZAP_TXT(ADMIN_PHONE, phone)

			MEDIA_ZAP(ADMIN_PHONE, media_id, media_type, filename)

			if caption!='':
			
				ZAP_TXT(ADMIN_PHONE, caption)	
		

if __name__ == '__main__':

	app.run(port=5000, debug=True)