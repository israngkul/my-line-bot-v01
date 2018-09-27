from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,JoinEvent, ImageSendMessage, StickerSendMessage)
from random import seed
from random import randint
import json
import requests
import datetime
import http.client

url = "https://notify-api.line.me/api/notify"
token = "TBoCEqfOfILQXJ9K9E3Siww01EJne0FKH7fCUz2N5fB"
headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+token}
seed(1)
def linenotify(msg):
    global url,headers,token
    r = requests.post(url,headers=headers, data={'message':msg})

def  openweather(city):
    key = 'b088ff769dfd7ce58868390c0009532c'
    openurl='http://api.openweathermap.org/data/2.5/weather'
    querystring = {'q': city, 'appid': key, 'units':'metric','format':'json'}
    response = requests.request('GET', openurl,params=querystring)
    data = json.loads(response.text)
    resulttext=""
    try:
        if data['message']:
            resulttext= "ไม่พบชื่อดังกล่าว"
            return(resulttext)
    except KeyError as error:
        #d = json.dumps(data).decode('unicode-escape').encode('utf8')
        #print d
        resulttext= "ข้อมูลจาก Openweather.org - \n"
        resulttext = resulttext+"\nสภาพภูมิอากาศ : "+ data['name']+" ["+data['sys']['country']+"]\n"
        resulttext = resulttext+"ปริมาณเมฆ ฝน: "+ data['weather'][0]['description']+"\n"
        resulttext = resulttext+"อุณหภูมิปัจจุบัน: "+ str(data['main']['temp'])+" Celsius\n"
        resulttext = resulttext+"อุณหภูมิสูงสุด: "+ str(data['main']['temp_max'])+" Celsius\n"
        resulttext = resulttext+"อุณหภูมิต่ำสุด: "+ str(data['main']['temp_min'])+" Celsius\n"
        resulttext = resulttext+"ความเร็วลม: "+ str(data['wind']['speed'])+" km/h\n"
        resulttext = resulttext+"ทิศทางลม: "+ str(data['wind']['deg'])+" degree\n"
        resulttext = resulttext+"ความชื้นสัมพัทธ์: "+ str(data['main']['humidity'])+" %\n"
        return(resulttext)
  
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
    #linenotify('keywords:'+searchtext+" "+searchtext.upper())
    found = False
    resulttext= "ข้อมูลจากกรมอุตุนิยมวิทยา - "+str(data['Header']['LastBuiltDate']) + "\n"
    count = 0
    for item in data['Stations']:
        if count > 5:
            break
        if searchtext in item["StationNameTh"] or searchtext.upper() in item["StationNameEng"]:
            resulttext = resulttext+"\nสภาพภูมิอากาศ : "+ item['StationNameTh']+" ["+item['StationNameEng']+"]\n"
            resulttext = resulttext+"อุณหภูมิปัจจุบัน : "+str(item['Observe']['Temperature']['Value']) +" "+str(item['Observe']['Temperature']['Unit'])+"\n"
            resulttext = resulttext+"อุณหภูมิสูงสุด : "+str(item['Observe']['MaxTemperature']['Value']) +" "+str(item['Observe']['MaxTemperature']['Unit'])+"\n"
            resulttext = resulttext+"อุณหภูมิต่ำสุด : "+str(item['Observe']['MinTemperature']['Value']) +" "+str(item['Observe']['MinTemperature']['Unit'])+"\n"
            resulttext = resulttext+"ปริมาณน้ำฝน : "+str(item['Observe']['Rainfall']['Value']) +" "+str(item['Observe']['Rainfall']['Unit'])+"\n"
            resulttext = resulttext+"ความเร็วลม : "+str(item['Observe']['WindSpeed']['Value']) +" "+str(item['Observe']['WindSpeed']['Unit'])+"\n"
            resulttext = resulttext+"ทิศทางลม : "+str(item['Observe']['WindDirection']['Value']) +" "+str(item['Observe']['WindDirection']['Unit'])+"\n"
            resulttext = resulttext+"ความชื้นสัมพัทธ์ : "+str(item['Observe']['RelativeHumidity']['Value']) +" "+str(item['Observe']['RelativeHumidity']['Unit'])+"\n"
            found = True
            count = count + 1
    if found == False:
        resulttext = openweather(searchtext)
        return(resulttext)
    else:
        return(resulttext)

def exchange(currency):
    #linenotify("Currency Called")
    t = datetime.date.today()-datetime.timedelta(1)
    conn = http.client.HTTPSConnection("apigw1.bot.or.th")
    headers = {'x-ibm-client-id': "fece3acb-3332-4d9f-8fd0-8598740c684b",'accept': "application/json"}
    conn.request("GET", "/bot/public/Stat-ExchangeRate/v2/DAILY_AVG_EXG_RATE/?start_period="+str(t)+"&end_period="+str(t)+"&currency="+str(currency), headers=headers)
    res = conn.getresponse()
    data = res.read()
    rate = json.loads(data)
    #linenotify(str(data.decode("utf-8")))
    resulttext = "ที่มาของข้อมูลตอบกลับ ณ เวลา :"+str(rate['result']['timestamp'])+"\n"
    resulttext = resulttext+ str(rate['result']['data']['data_header']['report_name_th'])+"\n"
    resulttext = resulttext+ str(rate['result']['data']['data_header']['report_uoq_name_th'])+"\n"
    resulttext = resulttext+ "แหล่งข้อมูลจาก : "+str(rate['result']['data']['data_header']['report_source_of_data'][0]['source_of_data_th'])+"\n"
    resulttext = resulttext+ "สกุลเงิน - "+str(rate['result']['data']['data_detail'][0]['currency_name_eng'])+" "+str(rate['result']['data']['data_detail'][0]['currency_name_th'])+"\n"
    # อัตราขายถั่วเฉลี่ย
    resulttext = resulttext+ "อัตราขายถั่วเฉลี่ย : "+str(rate['result']['data']['data_detail'][0]['selling'])+"\n"
    # อัตราซื้อ ตั๋วเงิน
    resulttext = resulttext+ "อัตราซื้อ ตั๋วเงิน Buying Sight : "+str(rate['result']['data']['data_detail'][0]['buying_sight'])+"\n"
    # อัตราซื้อ เงินโอน
    resulttext = resulttext+ "อัตราซื้อ เงินโอน Buying Transfer : "+str(rate['result']['data']['data_detail'][0]['buying_transfer'])+"\n"
    # อัตราขายถั่วเฉลี่ยถ่วงน้ำหนักระหว่างธนาคาร
    resulttext = resulttext+ "อัตราขายถั่วเฉลี่ยถ่วงน้ำหนักระหว่างธนาคาร Mid Rate: "+str(rate['result']['data']['data_detail'][0]['mid_rate'])+"\n"
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
    #app.logger.info("Request body: " + body)
    result = json.loads(body)
    user_id = result['events'][0]['source']['userId']
    profile = line_bot_api.get_profile(user_id)
    msgtext = "\nEvent type:"+result['events'][0]['type'] + "\n"
    if result['events'][0]['source']['type'] == "user":
        msgtext = msgtext + "User ID: " + str(user_id) + "\n"
        msgtext = msgtext + "User Name: " + profile.display_name + "\n"
    elif result['events'][0]['source']['type'] == "group" or result['events'][0]['source']['type'] == "room":
        #linenotify("group detected")
        msgtext = msgtext + "User ID: " + str(user_id) + "\n"
        msgtext = msgtext + "User Name: " + profile.display_name + "\n"
        group_id = str(result['events'][0]['source']['groupId'])
        #profile = line_bot_api.get_group_member_profile(group_id,user_id)
        msgtext = msgtext + "Group ID: " + str(group_id) + "\n"
        #msgtext = msgtext + "Group Name: " + str(profile.display_name) + "\n"
    msgtext = msgtext + "message: " + str(result['events'][0]['message'])
    linenotify(msgtext)
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
    #linenotify("Message typed:"+str(words))
    if words[0] == "@":
        if len(words) < 2:
            line_bot_api.reply_message(event.reply_token,[TextSendMessage(text='คำขอไม่ครบถ้วน ลอง @ help'),StickerSendMessage(package_id='1', sticker_id='101')])
            return
        if words[1].upper() == "HELP":
            line_bot_api.reply_message(event.reply_token,[TextSendMessage(text="ตรวจสอบอากาศ:\n @ อากาศ(หรือ weather) {ชื่อเมือง}\nดูอัตราแลกเปลี่ยนสกุลเงิน:\n @ exchange {สกุลเงิน}"),StickerSendMessage(package_id='1', sticker_id='402')])
            return
        if len(words) < 3:
            line_bot_api.reply_message(event.reply_token,[TextSendMessage(text='คำขอไม่ครบถ้วน ลอง @ help'),StickerSendMessage(package_id='1', sticker_id='104')])
            return
        if words[1] =="อากาศ" or words[1].upper() == "WEATHER":
            searchtext = words[2]
            res = weather(searchtext)
            stickerid = randint(1,406)
            linenotify(str(stickerid))
            line_bot_api.reply_message(event.reply_token,[TextSendMessage(text=str(res)),StickerSendMessage(package_id='1', sticker_id=str(stickerid))])
        elif words[1].upper() == "EXCHANGE":
            currencies = "USD GBP EUR JPY HKD MYR SGD BND PHP IDR INR CHF AUD NZD CAD SEK DKK NOK CNY MXN ZAR KRW TWD KWD SAR AED MMK BDT CZK KHR KES LAK RUB VND EGP PLN LKR IQD BHD OMR JOD QAR MVR PGK ILS HUF PKR"
            if not(words[2].upper() in currencies):
                cur = " สหรัฐอเมริกา USD\n สหราชอาณาจักร GBP\n ยูโรโซน EUR\n ญี่ปุ่น(ต่อ 100เยน) JPY\n ฮ่องกง HKD\n มาเลเซีย MYR\n สิงคโปร์ SGD\n บรูไน BND\n ฟิลิปปินส์ PHP\n อินโดนิเซีย(ต่อ 1000 รูเปีย) IDR\n อินเดีย INR\n สวิตเซอร์แลนด์ CHF\n ออสเตรเลีย AUD\n นิวซีแลนด์ NZD\n แคนนาดา CAD\n สวีเดน SEK\n เดนมาร์ก DKK\n นอร์เวย์ NOK\n จีน CNY\n เม็กซิโก MXN\n แอฟริกาใต้ ZAR\n เกาหลีใต้ KRW\n ไต้หวัน TWD\n คูเวต KWD\n ซาดุดิอาระเบีย SAR\n สหรัฐอาหรับเอมิเรตส์ AED\n พม่า MMK\n บังกลาเทศ BDT\n สาธารณรัฐเช็ก CZK\n กัมพูชา(ต่อ 100 เรียล) KHR\n เคนยา KES\n ลาว(ต่อ 100 กีบ) LAK\n รัสเซีย RUB\n เวียดนาม(ต่อ 100 ดอง) VND\n อียิปต์ EGP\n โปแลนด์ PLN\n ศรีลังกา LKR\n อีรัก IQD\n บาห์เรน BHD\n โอมาน OMR\n จอร์แดน JOD\n กาตาร์ QAR\n มัลดีฟล์ MVR\n เนปาล NPR\n ปาปัวนิวกินี PGK\n อิสราเอล ILS\n ฮังการี HUF\n ปากีสถาน PKR\n"
                stickerid = randint(1,406)
                linenotify(str(stickerid))
                line_bot_api.reply_message(event.reply_token,[TextSendMessage(text='สกุลเงิน ที่ใช้ได้ 3 ตัวอักษร:\n'+ str(cur)),StickerSendMessage(package_id='1', sticker_id=str(stickerid))])
            else:
                searchtext = words[2]
                res = exchange(searchtext.upper())
                stickerid = randint(1,406)
                linenotify(str(stickerid))
                line_bot_api.reply_message(event.reply_token,[TextSendMessage(text=str(res)),StickerSendMessage(package_id='1', sticker_id=str(stickerid))])
        else:
            line_bot_api.reply_message(event.reply_token,[TextSendMessage(text='คำขอไม่ถูกต้อง'),StickerSendMessage(package_id='4', sticker_id='295')])
            
@handler.add(JoinEvent)
def handle_join(event):
    wplog.logger.info("Got join event")
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Joined this ' + event.source.type))
    
if __name__ == "__main__":
    app.run()
