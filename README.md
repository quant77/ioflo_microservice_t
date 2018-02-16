# ioflo_microservice_t
# ioflo_microservice_t
How to setup the environment and run an app: <br />
Load ioflo_microservice_example as zip, extract it and put into the folder <br />
$ cd folder <br />
$ pip3 install -e .   <br />
Open new terminal and do: <br />
$ microservice <br />
in python console, run a following:<br />
>>> import libnacl 
>>> from microservice.help.helping import makeUserReg 
>>> seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES) 
>>> verkey, sigkey = libnacl.crypto_sign_seed_keypair(seed)
>>> signature, registration = makeUserReg(verkey, sigkey,username='user_name') 
get signature and registration:  <br />
>>> signature 
>>> print(registration)
{  <br />
  "username": "user_name", <br />
  "key": "u3gMTa9qlH1NgMtUyzvFtLVXT8quNk64Po5WfI_Zn2s=", <br />
  "changed": "" <br />
} <br />
use this data at next step<br />

then using the app Postman, do the registration: <br />
select POST using url http://localhost:8080/register, select Body -> raw -> and from drowpdown JSON(application/json), <br />
{ <br />
  "username": "user_name",<br />
  "key": "u3gMTa9qlH1NgMtUyzvFtLVXT8quNk64Po5WfI_Zn2s=",<br />
  "changed": ""<br />
}<br />
in Headers, add Key Signature and in value field add(previously obtained signature) signer="pGwKWO8PMkP3bWdlwbB41dj6gpPEqrBcEE3O9k708nAoQu7j-XG7Oq5y5udLjrhKGVrwmapXdvOFQmWotcTHDw=="
 and hit SEND <br />

For POST request, go to python console:<br />
>>> from microservice.help import helping<br />
>>> request=b'{   "reputee": "user_name", "repute": {    "rid" : "rid32", "feature": "reach", "value": 5 }}'<br />
>>> helping.signRequest(sigkey, request)<br />
'amHoV3D1l3r1CyJVRisyM1joNtaEaHA6sa4uwmV6E601JWQ2HMbhxdxhxzSp8lyMMxq4QKY9woWMJpXFmKNcBg=='<br />

then using the app Postman,: <br />
select POST using url http://localhost:8080/register, select Body -> raw -> and from drowpdown JSON(application/json), <br />
{   "reputee": "user_name", "repute": {    "rid" : "rid32", "feature": "reach", "value": 5 }}<br />
(this string has to be identical to the one used in python console )<br />
in header:<br />
add Signature with value:<br />
signer="amHoV3D1l3r1CyJVRisyM1joNtaEaHA6sa4uwmV6E601JWQ2HMbhxdxhxzSp8lyMMxq4QKY9woWMJpXFmKNcBg=="<br />


then for GET request select GET: <br />
and change url to http://localhost:8000/reputee/user_name and click SEND





