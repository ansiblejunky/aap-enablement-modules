import requests

headers = {
    'Content-Type': 'application/vnd.ibm.powervm.uom+xml;Type=LogicalPartition',
    'X-API-Session': 'evVrj6ukcgnMkuf16_XHXE_rZXPW2MXQKTbUj56rXQZ_yKAL8w08bycQnslVXxUyze5bVx5pr3ROVYTidpKt-Jjed5kG3s8JUSb71NPAwMS-kb-Ty9v_5JGNOsoFLuadDfI9AaH3CKmpGVKA-X5aNa1uXaDCMmyO_JRdjPdxF869E1cF6bXiE1onIbkC0BT7lePKSQhJCZ5aJtt4rQartYa5nsB1OuTZSpF2Y3xk1rg=',
}

response = requests.get('https://twauslhmc1.app.test.hcscint.net:12443/rest/api/uom/LogicalPartition', headers=headers, verify=False)

print response.content

