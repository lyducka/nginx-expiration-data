import sys
import configparser
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from encrypt import decrypt_config, load_key
import datetime

# * Read config.ini
# config = configparser.ConfigParser()
# config.read('config.ini')

# * get aliyun sms config from config.ini file, this is not secure
# access_key = config.get('aliyun', 'access_key')
# secret_key = config.get('aliyun', 'secret_key')
# sign_name = config.get('aliyun', 'sign_name')
# template_code = config.get('aliyun', 'template_code')

# * Load key
key = load_key()

# * Get aliyun sms config from encrypted config file, this is secure

decrypted_config = decrypt_config('encrypted_config.ini', key)
access_key = decrypted_config.get('aliyun', 'access_key')
secret_key = decrypted_config.get('aliyun', 'secret_key')
sign_name = decrypted_config.get('aliyun', 'sign_name')
template_code = decrypted_config.get('aliyun', 'template_code')

phone_number = sys.argv[1]
vhost_name = sys.argv[2]
days_remaining = sys.argv[3]

client = AcsClient(access_key, secret_key, 'default')
request = CommonRequest()
request.set_domain('dysmsapi.aliyuncs.com')
request.set_version('2017-05-25')
request.set_action_name('SendSms')
request.set_method('POST')
request.add_query_param('SignName', sign_name)
request.add_query_param('TemplateCode', template_code)
request.add_query_param('PhoneNumbers', phone_number)
request.add_query_param('TemplateParam', '{"vhost_name":"' + vhost_name + '","days_remaining":"' + days_remaining + '"}')

response = client.do_action_with_exception(request)

# * Record log to sms_log.log with current time Phone number and response
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
log_message = f"{current_time}: Phone number: {phone_number}, Response: {response.decode()}"
with open('sms_log.log', 'a') as log_file:
    log_file.write(log_message + '\n')

sys.stdout.write(response.decode())
