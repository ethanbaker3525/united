'''This Module allows for simple sending of sms messaging without subscribing to a third party service.
The SMSLoginCreds class is a class that allows for simple authentication of the SMSServer class.
The SMSServer class starts a thread of an smtplib server object that can send sms messages through an email adress.
The SMSServer class can send sms messages to numbers on At&t, T-Mobile, Verizon, Page-plus, Sprint, Virgin Mobile, Metro PCS, Boost Mobile, Cricket Wireless, Republic Wireless, Google Fi, US Cellular, Ting, Consumer Cellular, and C Spire.'''
import smtplib
import json

class SMSLoginCreds:
	'''This class allows for easy authenticaiton of the SMSServer class'''

	def __init__(self):
		self.address = None
		self.password = None

	def to_json(self, file_name):
		with open(file_name, 'w') as file:
			file.write(json.dumps({
				'address':self.address,
				'password':self.password
				}))

	def from_json(self, file_name):
		with open(file_name, 'r') as file:
			creds = json.loads(file.read())
			self.address = creds['address']
			self.password = creds['password']
			return self

	def from_text(self, address, password):
		self.address = address
		self.password = password
		return self

class SMSServer:
	'''This class allows for the sending of sms messages through different carrier's sms gateways.
	For speedy delivery, it is advantageous to specify the carrier of the phone you are sending a message to when you initalize the object.
	To get the dictionary of carriers use the variable SMSServer.carriers_dict'''
	def __init__(self, creds, receipient, carrier=None):
		assert creds.address != None or creds.password != None
		self.carriers_dict = {
			'AT&T':'@txt.att.net',
			'T_MOBILE':'@tmomail.net',
			'VERIZON':'@vtext.com',
			'PAGE_PLUS':'@vtext.com',
			'SPRINT':'@messaging.sprintpcs.com',
			'VIRGIN_MOBILE':'@vmobl.com',
			'METRO_PCS':'@mymetropcs.com',
			'BOOST_MOBILE':'@sms.myboostmobile.com',
			'CRICKET':'@sms.cricketwireless.net',
			'REPUBLIC_WIRELESS':'@text.republicwireless.com',
			'GOOGLE_FI':'@msg.fi.google.com',
			'US_CELLULAR':'@email.uscc.net',
			'TING':'@message.ting.com',
			'CONSUMER_CELLULAR':'@mailmymobile.net',
			'C_SPIRE':'@cspire1.com'
			}
		assert carrier in self.carriers_dict.keys() or carrier == None
		self.addrs = []
		if carrier != None:
			self.addrs.append(receipient+self.carriers_dict[carrier])
		else:
			for carrier_address in self.carriers_dict.values():
				self.addrs.append(receipient+carrier_address)
		self.creds = creds
		self.server = smtplib.SMTP('smtp.gmail.com', 587)
		self.server.starttls()
		self.server.login(self.creds.address, self.creds.password)

	def send(self, message):
		for addr in self.addrs:
			self.server.sendmail(self.creds.address, addr, message)

	def quit(self):
		self.server.quit()