import requests
import configparser
import os
from flask import Flask, request, redirect, url_for, render_template


config = configparser.ConfigParser()
config.read('database.ini')
application = Flask(__name__)
API_ENDPOINT = "https://discord.com/api/v9"

CLIENT_ID = config['apiinfo']['CLIENT_ID']
CLIENT_SECRET = config['apiinfo']['CLIENT_SECRET']
CLIENT_TOKEN = config['botinfo']['bottoken']
DOMAIN = config['apiinfo']['DOMAIN']
exchangepass = config['apiinfo']['exchangepass']
SCOPE = "identify guilds guilds.join"
REDIRECT_URI = f"{DOMAIN}/discordauth"
welcomechannel = str(config['botinfo']['welcome_channel'])
memberrole = str(config['botinfo']['memberrole'])
restorekey = str(config['botinfo']['therestorekey'])
guildid = config['info']['guildid']

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

@application.route('/working', methods=['GET', 'POST'])
def working():
    return 'true'

@application.route('/discordauth', methods=['GET', 'POST'])
def discord():
    print("In discordauth")
    code = request.args.get('code')
    data = exchange_code(code)
    state = request.args.get('state')
    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    data2 = getid(access_token)
    userid = str(data2.get("id"))
    username = data2.get("username")
    country = data2.get("locale")
    if userid in config['useridsincheck']:  
        config['users'][userid] = 'NA'
        config[userid] = {}
        config[userid]['refresh_tokens'] = refresh_token
        config[userid]['refresh'] = 'true'
        config[userid]['country'] = country
        with open('database.ini', 'w') as configfile:
            config.write(configfile)
        if request.method == 'POST':
            return 'success'
        if request.method == 'GET':
            jso1={"userid": userid,"userip": request.remote_addr}
            r=requests.post("http://localhost:3550/verified",json=jso1)
            return render_template('Authcomplete.html')
    elif userid in config['users']:
        if request.method == 'POST':
            return 'success'
        if request.method == 'GET':
            jso1={"userid": userid,"userip": request.remote_addr}
            r=requests.post("http://localhost:3550/verified",json=jso1)
            return render_template('Authcomplete.html')
    else:
        return 'fail'

@application.route('/restore', methods=['GET', 'POST'])
def restore():
    password = request.json['code']
    if password == exchangepass:
        restoreserver()
        return 'succsess'
    else:
        print("Invalid password" + password)
        return 'wrong password'    

@application.route('/', methods=['GET', 'POST'])
def testbuild():
    return render_template('index.html')

def getid(info):
    url = "https://discord.com/api/v9/users/@me"
    payload={}
    accsestokentoget = info
    headers = {
        'Authorization': 'Bearer ' + accsestokentoget,
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    response.raise_for_status()
    return response.json()

#error to fix in here
@application.route('/requestid', methods=['GET', 'POST'])
def requestid():
    print("Part requestid")
    key = request.json['key']
    id = str(request.json['id'])
    print(id)
    print(key)
    if key == exchangepass:
        if id in config['users']:
            return 'succsess'
        else:
            print("key was correct")
            #check if the category is in the config
            config['useridsincheck'] = {}
            config['useridsincheck'][id] = 'waiting'
            with open('database.ini', 'w') as configfile:
                config.write(configfile)
            return 'succsess'
    else:
        print("key was wrong")
        return 'wrong key'





@application.route('/data', methods=['GET', 'POST'])
def data():
    key = request.json['key']
    dataset = request.json['dataset']
    print("part data")
    if config['apiinfo']['botsetupcomplete'] == 'no':
        if dataset == 'pass':
            config['apiinfo']['botsetupcomplete'] = 'yes'
            with open('database.ini', 'w') as configfile:
                config.write(configfile)
            return config['apiinfo']['tempkey']
        else:
            return 'fail wrong pass u wanker'
    elif key == config['apiinfo']['tempkey']:
        if dataset == 'CLIENT_ID':
            return CLIENT_ID
        if dataset == 'guildid':
            return guildid
        if dataset == 'CLIENT_SECRET':
            return CLIENT_SECRET
        if dataset == 'bottoken':
            return CLIENT_TOKEN
        if dataset == 'exchangepass':
            return exchangepass
        if dataset == 'welcomechannel':
            return welcomechannel
        if dataset == 'verifiedrole':
            return memberrole
        if dataset == 'restorekey':
            return restorekey
        else:
            return 'fail datasetval needed'
    else:
        return 'fail key needed'

        
@application.route('/checkifverifydone', methods=['GET', 'POST'])
def checkifverifydone():
    print("Part checkifverifydone")
    key = request.json['key']
    id = str(request.json['id'])
    print(id)
    print(key)
    if key == exchangepass:
        print("key was correct")
        if id in config['users']:
            config['useridsincheck'][id] = 'verified'
            with open('database.ini', 'w') as configfile:
                config.write(configfile)
                print("corect")
                return 'true'
        else:
            print("id was not found")
            return 'false'
    else:
        return 'false'

def exchange_code(code):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE
    }
    r = requests.post(
        f"{API_ENDPOINT}/oauth2/token",
        data=data,
        headers=headers
    )
    r.raise_for_status()
    return r.json()


def get_new_token(old_token): # gets new refresh_token
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': old_token
    }
    r = requests.post(
        f"{API_ENDPOINT}/oauth2/token",
        data=data,
        headers=headers
    )
    r.raise_for_status()
    return r.json()


def add_to_guild(access_token, user_id, guild_id):
    headers = {
        "Authorization" : f"Bot {CLIENT_TOKEN}",
        'Content-Type': 'application/json'
    }
    data = {
        "access_token" : access_token
    }
    response = requests.put(
        url=f"{API_ENDPOINT}/guilds/{guild_id}/members/{user_id}",
        headers=headers,
        json=data
    )



def restoreserver():
    userids = config['users']
    guildid = config['info']['guildid']

    for idsinlist in userids:
        print(idsinlist)
        code = config[idsinlist]['refresh_tokens']
        if config[idsinlist]['refresh'] == "false":
            try:
                data = exchange_code(code)
                access_token = data.get("access_token")
                add_to_guild(access_token, idsinlist, guildid)
                config[idsinlist]['refresh_tokens'] = data.get("refresh_token")
                config[idsinlist]['refresh'] = 'true'
                with open('database.ini', 'w') as configfile:
                    config.write(configfile)
            except:
                print("error")
        if config[idsinlist]['refresh'] == "true":
            try:
                data = get_new_token(code)
                access_token = data.get("access_token")
                add_to_guild(access_token, idsinlist, guildid)
                config[idsinlist]['refresh_tokens'] = data.get("refresh_token")
                with open('database.ini', 'w') as configfile:
                    config.write(configfile)
            except:
                print("error")
        else:
            print("Refresh status is invalid")
            print(code)
        
if __name__ == '__main__':
    cls()
    application.run(host='0.0.0.0', port=80) #change to your port default port is 80
