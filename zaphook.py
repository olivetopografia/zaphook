#
from flask import Flask, request
import os
import requests
from datetime import date


app=Flask(__name__)

processed_messages=set()

current_date=date.today()

set_date=date.today()


VERIFY_TOKEN=os.getenv('VERIFY_TOKEN')

WHATSAPP_TOKEN=os.getenv('WHATSAPP_TOKEN')

ADMIN_PHONE=os.getenv('ADMIN_PHONE')

PHONE_NUMBER_ID=os.getenv('PHONE_NUMBER_ID')

RESPOSTA_AUTOMATICA=os.getenv('RESPOSTA_AUTOMATICA')

print('')

print(f'Resposta Automática: {RESPOSTA_AUTOMATICA}')

if not all ([VERIFY_TOKEN, WHATSAPP_TOKEN, ADMIN_PHONE,PHONE_NUMBER_ID, RESPOSTA_AUTOMATICA]):

	print('')

	raise RuntimeError('Variáveis de ambientes não configuradas')

def ZAP_TXT(phone,texto):

	url=f'https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages'

	headers={	'Authorization':f'Bearer {WHATSAPP_TOKEN}',

		'Content-Type':'application/json' }

	payload={	'messaging_product':'whatsapp',

		'to':phone,

		'type': 'text',

		'text': { 'body': texto} }

	requests.post(url, json=payload, headers=headers)

def MEDIA_ZAP(phone, media_id, media_type):

	url=f'https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages'

	headers={	'Authorization':f'Bearer {WHATSAPP_TOKEN}',

		'Content-Type':'application/json' }

	payload={ "messaging_product":"whatsapp",

		"to":phone,

		"type":media_type,

		media_type: {"id": media_id} }

	response=requests.post(url, json=payload, headers=headers)

	print('')

	print("Status media:", response.status_code)

	print('')

	print("Resposta:", response.text)



@app.route('/zaphook', methods=['GET', 'POST'])

def zaphook():	

	if request.method=='GET':

		verify_token2=request.args.get('hub.verify_token')

		challenge=request.args.get('hub.challenge')

		if VERIFY_TOKEN==verify_token2:

			print('Acesso validado.')

			return challenge

		else:

			return 'Acesso negado', 403

	if request.method=='POST':

		global processed_messages

		global set_date	

		if date.today()!=set_date:

			processed_messages.clear()

			set_date=date.today()		

		data=request.json

		print(data)

		try:

			value=data['entry'][0]['changes'][0]['value']

		except (KeyError, IndexError, TypeError):

			return 'EVENT_RECEIVED', 200

		if 'messages' not in value:

			return 'EVENT_RECEIVED', 200

		mensagem=value['messages'][0]			

		message_id=mensagem['id']

		if message_id in processed_messages:

			return 'EVENT_RECEIVED', 200
			
		processed_messages.add(message_id)			

		phone= mensagem['from']		
				
		print(f'Atividade detectada: {phone}')

		texto=('Olá, obrigado por usar o canal oficial da Olive Topografia.\n'

		'Para atendimento clique no link abaixo: \n'

		'https://api.whatsapp.com/send/?phone=5511973354380&text&type=phone_number&app_absent=0')

		if RESPOSTA_AUTOMATICA=='ativada':

			ZAP_TXT(phone, texto)				

		if phone!=ADMIN_PHONE and mensagem['type']=='text':

			body=mensagem['text']['body']

			body=f'{phone}: \n{body}'

			ZAP_TXT(ADMIN_PHONE, body)			

		if phone!=ADMIN_PHONE and mensagem['type'] in ['audio', 'image', 'video', 'document']:

			media_type=mensagem['type']

			media_id=mensagem[media_type]['id']

			

			ZAP_TXT(ADMIN_PHONE, phone)

			MEDIA_ZAP(ADMIN_PHONE, media_id, media_type)	
		

if __name__ == '__main__':

	app.run(port=5000, debug=True)