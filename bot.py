from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,JoinEvent, ImageSendMessage)
import json
import requests

url = "https://notify-api.line.me/api/notify"
token = "TBoCEqfOfILQXJ9K9E3Siww01EJne0FKH7fCUz2N5fB"
headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+token}

def linenotify(msg):
    global url,headers,token
    r = requests.post(url,headers=headers, data={'message':msg})

def weather(city):
    # สำหรับ TMD กรมอุตุนิยมวิทยา API
    tmdurl = 'http://data.tmd.go.th/api/WeatherToday/V1/'
    # response เป็น json
    querystring = {'uid': 'u61worawit.isr', 'ukey': '766a8cda17410d36dc835300743126d9', 'format':'json'}
    # หรือต้องการ response เป็น XML
    # querystring = {'uid': 'demo', 'ukey': 'demokey'}
    response = requests.request('GET', tmdurl,params=querystring)
    data = json.loads(response.text)
    #d = json.dumps(data).decode('unicode-escape').encode('utf8')
    #thaidata = d
    searchtext = city
    found = False
    resulttext= "ข้อมูลจากกรมอุตุนิยมวิทยา - "+str(data['Header']['LastBuiltDate']) + "\n"
    for item in data['Stations']:
        if searchtext in item["StationNameTh"] or searchtext.upper() in item["StationNameEng"]:
            resulttext = resulttext+"\nสภาพภูมิอากาศ : "+ item['StationNameTh']+" ["+item['StationNameEng']+"]\n"
            resulttext = resulttext+"อุณหภูมิปัจจุบัน : "+str(item['Observe']['Temperature']['Value']) +" "+str(item['Observe']['Temperature']['Unit'])+"\n"
            resulttext = resulttext+"อุณหภูมิสูงสุด : "+str(item['Observe']['MaxTemperature']['Value']) +" "+str(item['Observe']['MaxTemperature']['Unit'])+"\n"
            resulttext = resulttext+"อุณหภูมิต่ำสุด : "+str(item['Observe']['MinTemperature']['Value']) +" "+str(item['Observe']['MinTemperature']['Unit'])+"\n"
            resulttext = resulttext+"ปริมาณน้ำฝน : "+str(item['Observe']['Rainfall']['Value']) +" "+str(item['Observe']['Rainfall']['Unit'])+"\n"
            resulttext = resulttext+"ความเร็วลม : "+str(item['Observe']['WindSpeed']['Value']) +" "+str(item['Observe']['WindSpeed']['Unit'])+"  "
            resulttext = resulttext+"ทิศทางลม : "+str(item['Observe']['WindDirection']['Value']) +" "+str(item['Observe']['WindDirection']['Unit'])+"\n"
            resulttext = resulttext+"ความชื้นสัมพัทธ์ : "+str(item['Observe']['RelativeHumidity']['Value']) +" "+str(item['Observe']['RelativeHumidity']['Unit'])+"\n"
            found = True
    if found == False:
        return('ไม่พบชื่อดังกล่าว')
    return(resulttext)

app = Flask(__name__)

line_bot_api = LineBotApi('LtooZVH2hypDa0NM8b4hy/Cj9tTxaS5WkMnRk959IKbL/8lH80juoRcRV263I3/uj18hz6RShvplHeXFmP5kHLM514LJyQ5gq53gmOmOY1VtN1P8X3FVTl9FkGH8C7ptSnAissMNCs3bgWTe4voeEQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('28eb0ef0b53631f1581716b309b1acbb')

body = ""

@app.route("/")
def hello():
    return "Hello AJoy Linebot v2 World!"

@app.route("/webhook", methods=['GET','POST'])
def webhook():
    global body
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    result = json.loads(body)
    user_id = result['events'][0]['source']['userId']
    profile = line_bot_api.get_profile(user_id)
    linenotify('มีการส่งข้อความจาก -'+ profile.display_name +':\n'+str(body))
    #linenotify(profile.picture_url)
    #linenotify(profile.status_message)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    if request.method == 'POST':
        pass
    return '200 OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global body
    result = json.loads(body)
    user_id = result['events'][0]['source']['userId']
    profile = line_bot_api.get_profile(user_id)
    #text = str(result['events'][0]['message']['text'])
    #linenotify(profile.display_name)
    #linenotify(profile.picture_url)
    #line_bot_api.reply_message(event.reply_token,TextSendMessage(text='ข้อความจาก :'+profile.display_name))
    #line_bot_api.reply_message(event.reply_token,TextSendMessage(text=profile.display_name+' \nภาพโปร์ไฟล์ของผู้ส่งข้อความ:'+profile.picture_url))
    text = str(event.message.text)
    words = text.split()
    linenotify("Message typed:"+str(words))
    if words[0] == "@":
        if len(words) < 3:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='คำขอไม่ครบถ้วน'))
            return
        if words[1] =="อากาศ" or words[1].upper() == "WEATHER":
            searchtext = words[2]
            res = weather(searchtext)
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='ตอบกลับ:'+ str(res)))
        else:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='คำขอไม่ถูกต้อง'))
            
@handler.add(JoinEvent)
def handle_join(event):
    wplog.logger.info("Got join event")
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Joined this ' + event.source.type))
    
if __name__ == "__main__":
    app.run()
