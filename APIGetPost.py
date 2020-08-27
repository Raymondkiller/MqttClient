########################################################################
#API face detect setup
########################################################################
import json
import requests
import base64

import threading
from MqttClient import MQTTClient

Mqtt = MQTTClient()
Mqtt.MqttPathPublish = "your path to publish"
Mqtt.MqttPathSubcribe = "APIGetPost"


class myThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        Mqtt.mqttSubcribe()

queueLock = threading.Lock()
thread = myThread(1, "thread1")
thread.start()

#login infomation
# urlLogin = "http://new-thd.ddns.net:4000/v1/auth"
urlLogin = "https://api.deepkafe.com/faceid/v1/auth"
typeHeaderLogin = {'Content-Type': 'application/json'}
userData = {"username": "deepkafe1",  "password": "deepkafedemo1"}

#API Upload
# urlDac = "http://new-thd.ddns.net:4000/v1/dac"
urlDac = "https://api.deepkafe.com/faceid/v1/dac"

#Get access data
# urlGetAccess = "http://new-thd.ddns.net:4000/v1/fetch"
urlGetAccess = "https://api.deepkafe.com/faceid/v1/fetch"
dataGetAccess = {"start_time": "01/01/1992 1:1:1", "end_time": "06/03/2019 1:1:1"}

#Verification API
# urlVerify = "http://new-thd.ddns.net:4000/v1/verify"
urlVerify = "https://api.deepkafe.com/faceid/v1/verify"
dataVerify = {'image': '',  'verify_id' : ''}

#Get all user API
# urlGetUsers = "http://new-thd.ddns.net:4000/v1/get_users"
urlGetUsers = "https://api.deepkafe.com/faceid/v1/get_users"

#Register User API
# urlRegister = "http://new-thd.ddns.net:4000/v1/register"
urlRegister = "https://api.deepkafe.com/faceid/v1/register"
dataRegister = {"user_name": "",  "user_id" : "",  "face_images" : "", "overwrite": True}

#Retrain API
# urlRetrain = "http://new-thd.ddns.net:4000/v1/retrain"
urlRetrain = "https://api.deepkafe.com/faceid/v1/retrain"

#Delete User API
# urlDeleteUser = "http://new-thd.ddns.net:4000/v1/delete_user"
urlDeleteUser = "https://api.deepkafe.com/faceid/v1/delete_user"
dataDeleteUser = {"user_id" : ""}

typeHeaderApi = {'Content-Type': 'application/json', 'Authorization':''}


def getToken():
    responseDecodedJson = requests.post(urlLogin, data=json.dumps(userData), headers=typeHeaderLogin)
    responseJson = responseDecodedJson.json()
    if responseJson["message"] == "SUCCESS":
        return responseJson["data"]["authToken"].encode("ascii","replace")
    else:
        return "False"
def getAccess(_startTime, _endTime):
    dataGetAccess["start_time"] = _startTime
    dataGetAccess["end_time"] = _endTime

    typeHeaderApi['Authorization'] = 'Bearer ' + getToken()
    responseDecodedJson = requests.post(urlGetAccess, data=json.dumps(dataGetAccess), headers=typeHeaderApi)
    responseJson = responseDecodedJson.json()
    return responseJson

def verifyFace(_base64Image, _id):
    dataVerify['image'] = _base64Image
    dataVerify['verify_id'] = _id
    _token = getToken()
    if _token == "False":
        return "False"
    typeHeaderApi['Authorization'] = 'Bearer ' + _token
    responseDecodedJson = requests.post(urlVerify, data=json.dumps(dataVerify), headers=typeHeaderApi)
    responseJson = responseDecodedJson.json()
    return responseJson

def getAllUsers():
    typeHeaderApi['Authorization'] = 'Bearer ' + getToken()
    responseDecodedJson = requests.get(urlGetUsers, headers=typeHeaderApi)
    responseJson = responseDecodedJson.json()
    return responseJson

def registerUser(_username, _userId, _faceImage, _overwrite):
    typeHeaderApi['Authorization'] = 'Bearer ' + getToken()
    dataRegister["user_name"] = _username
    dataRegister["user_id"] = _userId
    dataRegister["face_images"] = _faceImage
    dataRegister["overwrite"] = _overwrite
    responseDecodedJson = requests.post(urlRegister, data=json.dumps(dataRegister), headers=typeHeaderApi)
    responseJson = responseDecodedJson.json()
    return responseJson

def deleteUser(_userId):
    typeHeaderApi['Authorization'] = 'Bearer ' + getToken()
    dataDeleteUser["user_id"] = _userId
    responseDecodedJson = requests.post(urlDeleteUser, data=json.dumps(dataDeleteUser), headers=typeHeaderApi)
    responseJson = responseDecodedJson.json()
    return responseJson

########################################################################
flag_1 = False
flag_2 = False
_dataWriteMainApp = {"source":"APIGetPost","func":"screen","data":{"company":"","name":"","ID":"","mess":""}}
_dataWriteAudioPlay = {"source":"APIGetPost","func":"play","data":""}
_dataWriteGPIO = {"source":"APIGetPost","func":"blinkLed","data":0}


print "start"
ImageBase64 = ""
IDCardNumber = ""
while True:
    _waitData = Mqtt.getData()
    if _waitData != None:
        waitData = json.loads(_waitData)
        #if waitData["source"] == "KeyBoard":
        #    IDCardNumber = waitData["data"]
        #    #print "KeyBoard: ", IDCardNumber
	#    flag_1 = True
        if waitData["source"] == "MainApp":
            _ImageBase64 = waitData["data"]["base64image"]
            IDCardNumber = waitData["data"]["ID"]
            with open(_ImageBase64) as image_file:
		ImageBase64 = base64.b64encode(image_file.read())
	    #print "MainApp: ", ImageBase64
	    #flag_2 = True
	    #flag_1 = True

        #if (flag_1 == True) & (flag_2 == True):
            #flag_1 = False
            #flag_2 = False
	    print "start"
            __respont =  verifyFace(ImageBase64,IDCardNumber)
	    print "stop"

            if __respont["message"] == "SUCCESS":
                if __respont["data"]["message"] == "Matched":
#		    print IDCardNumber
                    _dataWriteGPIO["data"] = 5
                    _dataWriteMainApp["data"]["mess"] = "Moi Ban Vao!"
                    _dataWriteMainApp["data"]["name"] = __respont["data"]["user_data"]["user_name"]
                    _dataWriteMainApp["data"]["company"] = userData["username"]
		    _dataWriteMainApp["data"]["ID"] = IDCardNumber
                    _dataWriteAudioPlay["data"] = "moibanvao"
                if __respont["data"]["message"] == "Not matched":
                    _dataWriteGPIO["data"] = 2
                    _dataWriteMainApp["data"]["mess"] = "Ban Cam Nham The Roi!"
                    _dataWriteMainApp["data"]["name"] = ""
                    _dataWriteMainApp["data"]["company"] = ""
		    _dataWriteMainApp["data"]["ID"] = IDCardNumber
                    _dataWriteAudioPlay["data"] = "bancamnhamtheroi"
                if __respont["data"]["message"] == "there is no user presented verify id":
                    _dataWriteGPIO["data"] = 3
                    _dataWriteMainApp["data"]["mess"] = "The Khong Hop Le!"
                    _dataWriteMainApp["data"]["name"] = ""
                    _dataWriteMainApp["data"]["company"] = ""
		    _dataWriteMainApp["data"]["ID"] = IDCardNumber
                    _dataWriteAudioPlay["data"] = "thekhonghople"
                if __respont["data"]["message"] == "There is not any face in the image":
                    _dataWriteGPIO["data"] = 1
                    _dataWriteMainApp["data"]["mess"] = "Camera Chua Thay Mat Ban!"
                    _dataWriteMainApp["data"]["name"] = ""
                    _dataWriteMainApp["data"]["company"] = ""
		    _dataWriteMainApp["data"]["ID"] = IDCardNumber
                    _dataWriteAudioPlay["data"] = "camerachuathaymatban"

                Mqtt.MqttPathPublish = "MainApp"
                Mqtt.mqttPublish(json.dumps(_dataWriteMainApp))
                Mqtt.MqttPathPublish = "GPIO"
                Mqtt.mqttPublish(json.dumps(_dataWriteGPIO))
                Mqtt.MqttPathPublish = "AudioPlay"
                Mqtt.mqttPublish(json.dumps(_dataWriteAudioPlay))
		print "done"

