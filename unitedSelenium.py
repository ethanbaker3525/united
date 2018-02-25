# Import Everything
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import json
import pickle
from getpass import getpass
from simplecrypt import decrypt
import time
from argon2 import PasswordHasher
import SMS

def wait_until_ready(my_id, delay=3):
	try:
		myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, my_id)))
		return True
	except TimeoutException:
		return False

# Constants
UNITED_CREDS_DIR = 'chris_united_creds.json'
COOKIE_DIR = 'chris_cookies.pkl'
SMS_CREDS_DIR = 'sms_creds.json'
HASH_DIR = 'chris_hashed_password.json'
SMS_NUMBER = '2038018297'
SMS_CARRIER = 'VERIZON'
LAST_NAME = 'Baker'

# Get password and checking to see if the password is correct
given_hash = json.loads(open(HASH_DIR).read())['hash']
ph = PasswordHasher()
while 1:
	password = getpass()
	try:
		ph.verify(given_hash, password)
		break
	except:
		print('your password is incorrect')

# Get flight number
while 1:
	ConfermationNum = input('Confermation Number: ')
	if len(ConfermationNum) != 6:
		print('Error, input your confermation number again...')
	else:
		break

# Setting up an sms server
sms_creds = SMS.SMSLoginCreds().from_json(SMS_CREDS_DIR)
server = SMS.SMSServer(sms_creds, SMS_NUMBER, carrier=SMS_CARRIER)

# Getting Encrypted Creds
file = open(UNITED_CREDS_DIR, 'r')
creds = json.loads(file.read())
creds['l'] = decrypt(password, creds['l'].encode('ISO-8859-1')).decode('utf8')
print('decrypted login')
creds['p'] = decrypt(password, creds['p'].encode('ISO-8859-1')).decode('utf8')
print('decrypted password')
file.close()

# Starting Chrome
driver = webdriver.Chrome()
driver.get('https://www.united.com/ual/en/us/account/account/signin')

# Adding cookies
cookies = pickle.load(open(COOKIE_DIR, "rb"))
for cookie in cookies:
    driver.add_cookie(cookie)

# Logging in
driver.find_element_by_name('MpNumber').send_keys(creds['l'])
driver.find_element_by_name('Password').send_keys(creds['p'])
driver.find_element_by_id('btnSignIn').click()

# Getting to the desired flight
while 1:
	try:
		driver.find_element_by_id('confirmationNo').send_keys(ConfermationNum)
		break
	except:
		time.sleep(0.1)
driver.find_element_by_id('lastName').send_keys(LAST_NAME)
driver.find_element_by_id('butMTSearch').click()
try:
	driver.find_element_by_id('ctl00_ContentInfo_ViewRes_linkUpgrade').click()
except Exception as e:
	print('there are no upgrades avalible for the flight you gave')
	print(e)
	driver.quit()
	quit()

# Refreshing the page
while 1:
	assert wait_until_ready('ctl00_ContentInfo_btnUpgrade')
	soup = BeautifulSoup(driver.page_source, 'lxml')
	prices = soup.findAll('span', class_='fareCurrency')
	if len(prices) == 0:
		break
	driver.refresh()

# Once script is finished, an sms is sent
server.send('Your flight has been upgraded! Return to your computer to complete the upgrade.')

# To end the script, the user must press enter
input('The flight has been upgraded. Press enter to end the session.')
server.quit()
driver.quit()
quit()






