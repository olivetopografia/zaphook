from flask import Flask, request
import os
import requests


app=Flask(__name__)

VERIFY_TOKEN=os.getenv('VERIFY_TOKEN')

WHATSAPP_TOKEN=os.getenv('WHATSAPP_TOKEN')

PHONE_NUMBER_ID=os.getenv('PHONE_NUMBER_ID')

if not all ([VERIFY_TOKEN, WHATSAPP_TOKEN, PHONE_NUMBER_ID]):

	print('')

	raise RuntimeError('Variáveis de ambientes não configuradas')

def ZAP_TXT(phone, texto):

	url=f'https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages'

	headers={	'Authorization':f'Bearer {WHATSAPP_TOKEN}',

		'Content-Type':'application/json' }

	payload={	'messaging_product':'whatsapp',

		'to':phone,

		'type': 'text',

		'text': { 'body': texto} }

	requests.post(url, json=payload, headers=headers)



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

		data=request.json

		print(data)

		try:

			value=data['entry'][0]['changes'][0]['value']

			if 'messages' in value:

				mensagem=value['messages'][0]

				phone= mensagem['from']		
				
				print(f'Atividade detectada: {phone}')

				texto=('Olá, obrigado por usar o canal oficial da Olive Topografia.\n'

				'Para atendimento clique no link abaixo: \n'

				'https://api.whatsapp.com/send/?phone=5511973354380&text&type=phone_number&app_absent=0')

				ZAP_TXT(phone, texto)
				

		except (KeyError, IndexError):

			pass

		return 'EVENT_RECEIVED', 200

if __name__ == '__main__':

	app.run(port=5000, debug=True)