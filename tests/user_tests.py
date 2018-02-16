import sys
import json
import unittest
import requests
import libnacl
import random
import string
import base64
import time
import os
from microservice.help.helping import makeUserReg, signRequest

class UserRegistrationsTest(unittest.TestCase):
	
	def test_RegisterUser(self, username=None):
		if username is None:
			username = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
		seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
		verkey, sigkey = libnacl.crypto_sign_seed_keypair(seed)
		signature, registration = makeUserReg(verkey, sigkey, username=username)
		url = 'http://localhost:8080/register'
		headers = {'Signature': 'signer="' + signature + '"', 'content-type': 'application/json'}
		r = requests.post(url, headers=headers, data=registration)
		self.assertEqual(r.status_code, 201)
		return username, sigkey

	def test_userDoubleRegistration(self):
		username, _ = self.test_RegisterUser()
		seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
		verkey, sigkey = libnacl.crypto_sign_seed_keypair(seed)
		signature, registration = makeUserReg(verkey, sigkey, username=username)
		url = 'http://localhost:8080/register'
		headers = {'Signature': 'signer="' + signature + '"', 'content-type': 'application/json'}
		r = requests.post(url, headers=headers, data=registration)
		self.assertEqual(r.status_code, 409)

	def test_UserRegInvalidSignature(self):
		username = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
		seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
		verkey, sigkey = libnacl.crypto_sign_seed_keypair(seed)
		signature, registration = makeUserReg(verkey, sigkey, username=username)
		decoded = base64.urlsafe_b64decode(signature.encode('utf-8'))
		decoded = decoded + os.urandom(4)
		signature = str(base64.urlsafe_b64encode(decoded))
		url = 'http://localhost:8080/register'
		headers = {'Signature': 'signer="' + signature + '"', 'content-type': 'application/json'}
		r = requests.post(url, headers=headers, data=registration)
		self.assertEqual(r.status_code, 400)
		self.assertEqual(r.content, b'{"title": "Invalid signature"}')

	def test_UserRegMissingSinature(self):
		username = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
		seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
		verkey, sigkey = libnacl.crypto_sign_seed_keypair(seed)
		signature, registration = makeUserReg(verkey, sigkey, username=username)
		url = 'http://localhost:8080/register'
		headers = {'content-type': 'application/json'}
		r = requests.post(url, headers=headers, data=registration)
		self.assertEqual(r.status_code, 400)
		self.assertEqual(r.content, b'{"title": "Missing signature"}')

	def test_addSignedReputationRecord(self, username=None, sigkey=None, rid=None, feature="reach", value=5):
		valuecheck = False
		if username is None:
			username, sigkey = self.test_RegisterUser()
			valuecheck = True
		#generate random rid
		if rid is None:
			rid = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10)) 
		request = {"reputee": username,
			"repute": 
			{
				"rid" : rid,
				"feature": feature,
				"value": value
			}
		}

		request = json.dumps(request).encode('utf-8')

		signature = signRequest(sigkey, request)
		url = 'http://localhost:8080/reputee'
		headers = {'Signature': 'signer="' + signature + '"', 'content-type': 'application/json'}
		r = requests.post(url, headers=headers, data=request)
		self.assertEqual(r.status_code, 201)

		time.sleep(2)
		url = 'http://localhost:8080/reputee/' + username
		headers = {'content-type': 'application/json'}
		r = requests.get(url, headers=headers)
		self.assertEqual(r.status_code, 200)
		body = json.loads(r.content.decode())
		if valuecheck:
			self.assertEqual(body['reach']['score'], value)

		return username, sigkey
				
	def test_addReputationRecordRidDuplicateRid(self, username=None, sigkey=None, rid=None, feature="reach", value=5):
		if username is None:
			username, sigkey = self.test_RegisterUser()
		#generate random rid
		if rid is None:
			rid = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10)) 
		request = {"reputee": username,
			"repute": 
			{
				"rid" : rid,
				"feature": feature,
				"value": value
			}
		}

		request = json.dumps(request).encode('utf-8')

		signature = signRequest(sigkey, request)
		url = 'http://localhost:8080/reputee'
		headers = {'Signature': 'signer="' + signature + '"', 'content-type': 'application/json'}
		r = requests.post(url, headers=headers, data=request)
		self.assertEqual(r.status_code, 201)
		
		time.sleep(2)
		request = {"reputee": username,
			"repute": 
			{
				"rid" : rid,
				"feature": "reach",
				"value": 8 
			}
		}

		request = json.dumps(request).encode('utf-8')

		signature = signRequest(sigkey, request)
		url = 'http://localhost:8080/reputee'
		headers = {'Signature': 'signer="' + signature + '"', 'content-type': 'application/json'}
		r = requests.post(url, headers=headers, data=request)
		self.assertEqual(r.status_code, 201)

		time.sleep(2)
		url = 'http://localhost:8080/reputee/' + username
		headers = {'content-type': 'application/json'}
		r = requests.get(url, headers=headers)
		self.assertEqual(r.status_code, 200)
		body = json.loads(r.content.decode())
		self.assertEqual(body['reach']['score'], 5)

	def test_invalidReputationRecord(self, username=None, sigkey=None, rid=None, feature="reach", value=5):
		if username is None:
			username, sigkey = self.test_RegisterUser()
		#generate random rid
		if rid is None:
			rid = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10)) 
		
		request = {"resdfputee": username,
			"repusfte": 
			{
				"risd" : rid,
				"feazture": feature,
				"valufe": value
			}
		}

		request = json.dumps(request).encode('utf-8')

		signature = signRequest(sigkey, request)
		url = 'http://localhost:8080/reputee'
		headers = {'Signature': 'signer="' + signature + '"', 'content-type': 'application/json'}
		r = requests.post(url, headers=headers, data=request)
		self.assertEqual(r.status_code, 201)

		time.sleep(2)
		url = 'http://localhost:8080/reputee/' + username
		headers = {'content-type': 'application/json'}
		r = requests.get(url, headers=headers)
		self.assertEqual(r.status_code, 404)
			
	def test_invalidSignedRecord(self, username=None, sigkey=None, rid=None, feature="reach", value=5):
		if username is None:
			username, sigkey = self.test_RegisterUser()
		#generate random rid
		if rid is None:
			rid = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10)) 
		request = {"reputee": username,
			"repute": 
			{
				"rid" : rid,
				"feature": feature,
				"value": value
			}
		}

		request = json.dumps(request).encode('utf-8')

		signature = signRequest(sigkey, request)

		decoded = base64.urlsafe_b64decode(signature.encode('utf-8'))
		decoded = decoded + os.urandom(4)
		signature = str(base64.urlsafe_b64encode(decoded))
		url = 'http://localhost:8080/reputee'
		headers = {'Signature': 'signer="' + signature + '"', 'content-type': 'application/json'}
		r = requests.post(url, headers=headers, data=request)
		self.assertEqual(r.status_code, 201)

		time.sleep(2)
		url = 'http://localhost:8080/reputee/' + username
		r = requests.get(url, headers=headers)
		self.assertEqual(r.status_code, 404)
		
	def test_reachClarityCloutCalculations(self):
		username, sigkey = self.test_addSignedReputationRecord(value=1)
		self.test_addSignedReputationRecord(username=username, sigkey=sigkey, value=10, feature='clarity')
		self.test_addSignedReputationRecord(username=username, sigkey=sigkey, value=11, feature='clarity')
		self.test_addSignedReputationRecord(username=username, sigkey=sigkey, value=4, feature='clarity')
		self.test_addSignedReputationRecord(username=username, sigkey=sigkey, value=1, feature='clarity')
		self.test_addSignedReputationRecord(username=username, sigkey=sigkey, value=3, feature='clarity')
		self.test_addSignedReputationRecord(username=username, sigkey=sigkey, value=10)
		self.test_addSignedReputationRecord(username=username, sigkey=sigkey, value=11)


		time.sleep(10)

		url = 'http://localhost:8080/reputee/' + username
		headers = {'content-type': 'application/json'}
		r = requests.get(url, headers=headers)

		self.assertEqual(r.status_code, 200)
		body = json.loads(r.content.decode())
		self.assertEqual(body['reach']['score'], 7.333333333333333)
		self.assertEqual(body['reach']['confidence'], 0.125)
		self.assertEqual(body['clarity']['score'], 5.8)
		self.assertEqual(body['clarity']['confidence'], 0.125)
		self.assertEqual(body['clout']['score'], 0.6566666666666667)
		self.assertEqual(body['clout']['confidence'], 0.125)

		
if __name__ == '__main__':
    unittest.main()
