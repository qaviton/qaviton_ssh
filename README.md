# Qaviton SSH
![logo](https://www.qaviton.com/wp-content/uploads/logo-svg.svg)  
[![version](https://img.shields.io/pypi/v/qaviton_ssh.svg)](https://pypi.python.org/pypi)
[![license](https://img.shields.io/pypi/l/qaviton_ssh.svg)](https://pypi.python.org/pypi)
[![open issues](https://img.shields.io/github/issues/qaviton/qaviton_ssh)](https://github/issues-raw/qaviton/qaviton_ssh)
[![downloads](https://img.shields.io/pypi/dm/qaviton_ssh.svg)](https://pypi.python.org/pypi)
![code size](https://img.shields.io/github/languages/code-size/qaviton/qaviton_ssh)
-------------------------  
  
making ssh super easy  
  
## Installation  
```sh  
pip install --upgrade qaviton_ssh
```  

### Requirements
- Python 3.6+  
  
## Features  
* simple ssh send-recieve api ✓  
* async requests ✗ (coming soon)  
* multi-session workflow ✗ (coming soon)  
  
## Usage  
  
#### creating an ssh client  
```python
from qaviton_ssh import SSH
# hostname is a reachable address for the machine
# username is the allowed user to have ssh access
# private_key is the file path or string of the private key
client = SSH(hostname='x.x.x.x', username='username', private_key='pkey.pem')

response = client.send('echo "hello world"')
print(response.data, response.error)  # server will respond with b'hello world', b''
```

#### create a python script on the server
```python
cd = 'cd myproject'
file = 'script.py'
response = client.send_many([cd, f'touch {file}', f'echo "print(\"script success\")" > {file}'])
assert not response.error
```  

#### execute the script
```python
response = client.send_many([cd, f'python {file}'])
assert not response.error
print(response.data)  # server will respond with b'script success'
```  
