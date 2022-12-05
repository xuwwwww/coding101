import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json


class Firebase():  # 物件
    # 記得要先初始化，也就是這個函式
    def Init(self, keyPath):
        try:
            global db
            cred = credentials.Certificate(keyPath)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            return 0
        except:
            return -1

    # 包含了update， post，get，delete
    class Function():

        global update

        # root是第一層，member是第二層，sunmember是第三層的東西，而submember的值實際上要存成一個dictionary(也就是json)方便之後使用
        def post(self, root, member, submember, string):
            doc_ref = db.collection(root).document(member)
            try:
                dic = doc_ref.get().to_dict()
            except:
                pass
            if dic != None:
                if submember in dic.keys():
                    print("already exists  -- from post")
                    return -1
                else:
                    dic[submember] = str(string)
                    doc_ref.delete()
                    doc_ref.set(dic)
            else:
                dic = {submember: string}
                doc_ref.set(dic)
            return 0

        # root和member使用同post，ppl是post的submember(一樣的東西)，item為json中的key，value圍其值(item和value都是以string化的json存)
        def update(self, root, member, ppl, item, value):
            doc_ref = db.collection(root).document(member)
            try:
                dic = doc_ref.get().to_dict()
            except:
                return 0
            dic2 = dic[ppl]
            dic3 = json.loads(dic2)
            dic3[item] = value
            dic[ppl] = str(dic3).replace("'", "\"")
            doc_ref.delete()
            doc_ref.set(dic)
            return 1

        # get和get某人在那些房間裡
        class get():

            # 如果ppl沒有輸入的話會預設輸出該member裡的所有submember，若有輸入則會回傳該submember包含的json資料的key以list回傳
            # 若showvalue是true的話就會顯示完整的json檔  以dictionary回傳
            def get(self, root, member, ppl="0", showValue=False):
                try:
                    doc_ref = db.collection(root).document(member)
                    try:
                        dic = doc_ref.get().to_dict()
                    except:
                        return 1
                    if ppl == "0":
                        if showValue != True:
                            return list(dic.keys())  # return <list>
                        else:
                            return dic  # return dictinoary
                    else:
                        dic2 = json.loads(dic[ppl])
                        if showValue != True:
                            return list(dic2.keys())  # return <list>
                        else:
                            return dic2  # return dictinoary
                except:
                    print("connot be empty!")
                    return 1

            # 回傳某人在那些房間裡 回傳值為list
            def getPplRoom(self, ppl):
                doc_ref = db.collection("RoomInfo").document("people")
                try:
                    dic = doc_ref.get().to_dict()
                except:
                    return 1
                dic = json.loads(dic[ppl].replace("\"[", "").replace("]\"", "").replace(" ", ""))["inRoom"]

                dic2 = list(dic.split(","))  # room 的格式為 "inRoom":"roomA,roomB"
                if dic2[0] == 'None' or dic2[0] == "None":
                    return None
                else:
                    return dic2

            # 之後會補上取得這個房間有誰
            def getRoomPpl(self, room):
                doc_ref = db.collection(room).document("init")
                try:
                    dic = doc_ref.get().to_dict()
                    dic = json.loads(dic["ppl"].replace("\"[", "").replace("]\"", "").replace(" ", ""))["ppl"]
                except:
                    print("error from get people in room")
                    return 1

                dic2 = list(dic.split(","))
                if dic2[0] == 'None' or dic2[0] == "None":
                    return None
                else:
                    return dic2

        # 刪除用
        class delete(get):
            # 刪除submember(若要刪除某人記得去他所在的房間將他移除)-->我晚點寫quit room，就不需要再多一步了
            def deleteSubmember(self, root, member, ppl):
                doc_ref = db.collection(root).document(member)
                try:
                    dic = doc_ref.get().to_dict()
                except:
                    return 1
                dic.pop(ppl)
                doc_ref.delete()
                doc_ref.set(dic)
                return 0

            # 刪除member(不要刪掉roominfo裡的rooms和people!!)
            def deleteDoc(self, root, collection):
                try:
                    db.collection(root).document(collection).get()
                except:
                    return 1
                doc_del = db.collection(root).document(collection)
                doc_del.delete()
                return 0

            # 刪除room(不要刪掉roominfo!!)  連同roominfo 裡的 rooms 裡的total rooms所記錄的一起移除
            def deleteRoom(self, root):  # 記得在刪除房間時也要把該使用者所在的房間移除(之後我會加個check去確認)

                def __findId(key, List):
                    j = 0
                    for i in List:
                        if i == key:
                            return int(j)
                        j = j + 1

                def __delSub(sub):
                    doc_ref = db.collection("RoomInfo").document("Rooms")
                    try:
                        dic = doc_ref.get().to_dict()
                    except:
                        return 1
                    dic.pop(sub)
                    doc_ref.delete()
                    doc_ref.set(dic)
                    return 0

                if root == "RoomInfo":
                    return 1

                # quit room for every one in that room//////////////////////////////////////////////////////////////////
                if str(super().getRoomPpl(root)) != "['']":
                    for j in super().getRoomPpl(root):
                        # delete doc
                        try:
                            db.collection(root).document(j).get()
                        except:
                            print("error from getting ppl's rooms in delete room")
                            return 1
                        doc_del = db.collection(root).document(j)
                        doc_del.delete()
                        # delete doc

                        r = super().getPplRoom(j)
                        r.pop(__findId(root, r))
                        r = str(r).replace("[", "").replace("]", "").replace("\'", "").replace("\'", "").replace(" ",
                                                                                                                 "")
                        update(self, "RoomInfo", "people", j, "inRoom", str(r))

                        rp = super().getRoomPpl(root)
                        rp.pop(int(__findId(j, rp)))
                        rp = str(rp).replace("[", "").replace("]", "").replace("\'", "").replace("\'", "").replace(" ",
                                                                                                                   "")
                        update(self, root, "init", "ppl", "ppl", str(rp))
                # /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

                doc_ref = db.collection(root)
                try:
                    dic = doc_ref.get()
                except:
                    return 1
                for delete_list in dic:  # 刪除room裡所有的資料，room就會自動刪除了
                    doc_del = db.collection(root).document(delete_list.id)
                    doc_del.delete()
                try:
                    __delSub(root)  # 刪除room from rooms
                except:
                    pass

                doc_ref = db.collection("RoomInfo").document("Rooms")
                try:
                    dic = doc_ref.get().to_dict()
                except:
                    return 1
                dic = json.loads(dic["tot"].replace("\"[", "").replace("]\"", "").replace(" ", ""))["rooms"]
                rp = list(dic.split(","))
                try:
                    rp.pop(int(__findId(root, rp)))
                    rp = str(rp).replace("[", "").replace("]", "").replace("\"", "").replace("\'", "").replace(" ", "")
                    update(self, "RoomInfo", "Rooms", "tot", "rooms", str(rp))
                except:
                    return 1

    # create，join，getroom
    class Room(Function):

        # 創建房間，並將房間名稱輸入至房間總紀錄中(roominfo->rooms->tot->rooms->中)
        def CreateRoom(self, root, key):
            t = list(str(super().get().get("RoomInfo", "Rooms", "tot", 1)["rooms"]).split(","))
            if root in t:
                print("already exists same room!\nPlease try another name")
                return -1
            else:
                # print("create room")
                super().post(root, "init", "ppl", "{\"ppl\":\"\"}")
                t = str(t).replace("[", "").replace("]", "").replace("\'", "").replace("\"", "").replace(" ", "")
                if t == '':
                    t = str(root)
                else:
                    t = t + ',' + root
                update(self, "RoomInfo", "Rooms", "tot", "rooms", str(t))
            te = "{\"key\":\"" + key + "\"}"
            super().post("RoomInfo", "Rooms", root, te)
            return 0

        # 某人加入房間，將房間名存入該人的json資料當中，並將其加入房間
        def JoinRoom(self, room, key, ppl):
            if key == super().get().get("RoomInfo", "Rooms", room, 1)["key"]:
                Rlist = super().get().getPplRoom(ppl)
                if room in Rlist:
                    print("you have joined the same room!")
                else:
                    Rlist = str(Rlist).replace("[", "").replace("]", "").replace("\'", "").replace("\"", "")
                    if Rlist == "" or Rlist == "None" or Rlist == '':
                        # print("its none inside")
                        Rlist = room
                        print(Rlist)
                        roomp = super().get().get(room, "init", "ppl", 1)["ppl"]
                        if roomp == "" or roomp == '' or roomp == " " or roomp == ' ':
                            roomp = ppl
                        else:
                            roomp = roomp + "," + ppl
                        update(self, room, "init", "ppl", "ppl", roomp)

                    else:
                        # print("exists other room, append one")
                        Rlist = str(Rlist) + "," + room
                        # print(Rlist)
                        roomp = super().get().get(room, "init", "ppl", 1)["ppl"]
                        if roomp == "" or roomp == '' or roomp == " " or roomp == ' ':
                            roomp = ppl
                        else:
                            roomp = roomp + "," + ppl
                        update(self, room, "init", "ppl", "ppl", roomp)
                    # print("nothing repeat in list of rooms, starting upload")
                    Rlist = str(Rlist).replace("[", "").replace("]", "").replace(" ", "")
                    update(self, "RoomInfo", "people", ppl, "inRoom", Rlist)  # join new room into room list
                    super().post(room, ppl, " ", " ")  # create new room by using post()
                    super().delete().deleteSubmember(room, ppl, " ")
                return 1
            else:
                print("wrong key!")
                return -1

        # 回傳現在有哪先房間(list)
        def GetRooms(self):
            return super().get().get("RoomInfo", "Rooms", "tot", 1)["rooms"]

        # 若是要刪掉某個人之前記得先QUIT
        def QuitRoom(self, ppl, room="0"):

            def __findId(key, List):
                j = 0
                for i in List:
                    if i == key:
                        return int(j)
                    j = j + 1

            if room == "0":
                for i in super().get().getPplRoom(ppl):
                    super().delete().deleteDoc(i, ppl)
                    r = super().get().getPplRoom(ppl)
                    try:
                        r.pop(int(__findId(i, r)))

                    except:
                        print("already clear")
                    r = str(r).replace("[", "").replace("]", "").replace("\"", "").replace("\'", "").replace(" ", "")
                    update(self, "RoomInfo", "people", ppl, "inRoom", str(r))

                    rp = super().get().getRoomPpl(room)
                    try:
                        rp.pop(int(__findId(ppl, rp)))
                        rp = str(rp).replace("[", "").replace("]", "").replace("\"", "").replace("\'", "").replace(" ",
                                                                                                                   "")
                        update(self, room, "init", "ppl", "ppl", str(rp))
                    except:
                        return 1

            else:
                super().delete().deleteDoc(room, ppl)
                r = super().get().getPplRoom(ppl)
                r.pop(__findId(room, r))
                r = str(r).replace("[", "").replace("]", "").replace("\'", "").replace("\'", "").replace(" ", "")
                update(self, "RoomInfo", "people", ppl, "inRoom", str(r))
                try:
                    rp = super().get().getRoomPpl(room)
                    rp.pop(int(__findId(ppl, rp)))
                    rp = str(rp).replace("[", "").replace("]", "").replace("\'", "").replace("\'", "").replace(" ", "")
                    print("rp == " + rp)
                    update(self, room, "init", "ppl", "ppl", str(rp))
                except:
                    return 1

            return 0

        def findKey(self, name):
            try:
                b = super().get().get("RoomInfo", "Rooms", name, 1)["key"]
            except:
                print("can't find")
                return -1
            return str(b)

    # account
    class Account(Room):

        # 編輯人物資料(更改json)
        def Edit(self, ppl, keyword, value):
            try:
                update(self, "RoomInfo", "people", ppl, keyword, value)
                return 1
            except:
                return 0

        # 上傳人，需輸入名子，mail，密碼
        def Register(self, name, mail, pwd):
            if name in super().get().get("RoomInfo", "people"):
                print("already registered with the name : " + name + ", please try anothor name !")
                return 1
            else:
                stri = "{\"name\": \"" + name + "\",\"mail\": \"" + mail + "\",\"pwd\": \"" + pwd + "\",\"inRoom\": \"\"}"
                super().post("RoomInfo", "people", name, stri)
            return 0

        def Login(self, name, pwd):
            try:
                if super().get().get("RoomInfo", "people", name, 1)["pwd"] == pwd:
                    return 0
                else:
                    return 1
            except:
                return 1

        def getInfo(self, name):
            return super().get().get("RoomInfo", "people", name, 1)

        # 輸入房間名，我的名稱，實際上付了多少，原本應該只要付多少
        def MoneyUpload(self, room, me, payed, infact):
            t = "{\"payed\":\"" + str(payed) + "\"}"
            t2 = "{\"infact\":\"" + str(infact) + "\"}"
            super().post(room, me, "payed", t)
            super().post(room, me, "infact", t2)

        # 更改錢的東西，option只能輸入"payed"->實際上付多少，"infact"->原本只要付多少，value為新的值
        def MoneyUpdate(self, room, me, option, value):
            update(self, room, me, option, option, str(value))

        def DeleteMe(self, name):
            try:
                for i in super().get().getPplRoom(name):
                    super().QuitRoom(name, i)
            except:
                pass
            fb.Function().delete().deleteSubmember("RoomInfo", "people", name)

            return 0

    class settleMent(Room):

        def settleMent(self, room, name):
            self.paid = 0
            self.actuallyNeed = 0
            self.people = 0
            self.dict = {}
            self.checkdict = {}
            if str(super().get().getRoomPpl(room)) != "['']":
                for j in super().get().getRoomPpl(room):
                    p = int(super().get().get(room, j, "payed", 1)["payed"])
                    i = int(super().get().get(room, j, "infact", 1)["infact"])
                    self.paid += p
                    self.actuallyNeed += i
                    self.dict[j] = int(p - i)
                    self.checkdict[j] = -1  # 1是找的錢可以還他了，2是還欠別人錢，3是找的錢不夠還他，要讓2去還他們，-1是還沒偵測
                    self.people += 1
                    self.me = {}
                self.remain = self.paid - self.actuallyNeed
                if self.remain < 0:
                    print("先把錢付齊!")
                    return 1
                # print(self.remain)
                # print(self.dict)
                for ppl in self.dict.keys():
                    if self.remain > 0:
                        if self.dict[ppl] >= 0 and self.remain - self.dict[ppl] >= 0:
                            # print(str(self.remain) + " 還 " + str(ppl) + "  " + str(self.dict[ppl]) + "  元， 剩 " + str(self.remain - self.dict[ppl]))
                            if ppl == name:
                                self.me["tot"] = self.dict[ppl]
                            self.remain -= self.dict[ppl]
                            self.checkdict[ppl] = 1
                            self.dict[ppl] = 0

                        elif self.dict[ppl] < 0:
                            self.checkdict[ppl] = 2
                            # print(ppl + "  還欠錢")
                        elif self.remain - self.dict[ppl] < 0:

                            self.checkdict[ppl] = 3
                            # print(ppl + "  錢不夠還他")

                for ppl in self.dict.keys():
                    if self.checkdict[ppl] == 3:
                        if ppl == name:
                            self.me["tot"] = self.remain
                        # print("剩下的錢全部還  " + ppl)
                        self.dict[ppl] -= self.remain
                        self.remain = 0
                        self.stillRemain = ppl

                for ppl in self.dict.keys():
                    if self.dict[ppl] < 0:
                        if ppl == name:
                            self.me[self.stillRemain] = self.dict[ppl]
                        if name == self.stillRemain:
                            self.me[ppl] = self.dict[ppl] * -1
                        # print(ppl + " 要還 " + self.stillRemain + "  " + str(-1*self.dict[ppl]))
                # print(self.me)
                return self.me

        def printSettleMent(self, dict):
            for i in dict.keys():
                if i == 'tot':
                    print("這次找的錢要還我  " + str(dict['tot']) + "  元")
                elif dict[i] < 0:
                    print("我欠 " + i + "  " + str(dict[i] * -1) + "  元")
                else:
                    print(i + "  欠我  " + str(dict[i]) + "  元")


fb = Firebase()
fb.Init({
    "type": "service_account",
    "project_id": "test-4b666",
    "private_key_id": "5e668d6e6439ae58252b02bbb99c5aaaa7c66274",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCq13wSYuPsJWOK\n6/NoJtL7fSE2NmY5PBmqiDZRU9Bza0V5OHQ5gjvx/m/tz7VPSpVGU3jmwRmBDqeB\nGHOh4IRj7HnEjzXCQY7N7BkIP6o6KKqXQyXRSiml7e/K/F1SCiP20vHtaPON+y7V\nrP8jFX2eQgL1pozGl4yJXcMb6ECsWx7QP8RYX2H76rh9+XErL7N73YfeLszSLz/7\n5hrblX5Vbqjt78+pXKexJVWBSKY27KBFp3/oXo+EXDjrgcaHp0pml7CvDRgQp+jY\neSY/eWdiZDsQJfn2FTFn0PIb48KfVoPvOBlLbCejk9Q/BAOfdK12+4uFzdAyfWiO\n4YmaNOSXAgMBAAECggEALk/3/Gv+aXfBQlmwRF2x+Cb1p+KbV4ypUIdYYjecXI2J\n6dCaATUC1xkocolKF1KaoNPkBHn4VfoJAoAEaK+adBQY9mX0JtLqyXvlVU0c8mMv\ny42SZOf73lVgGeDL03+YPEL2/mrjC2w6SAZ7q6EZypsOflVF+FgA6wQV7izJy279\nvuyiEQrScjAZbVWhpGRJbW7hNK33lQ/q66N7JC0I2zECG5Ons+CWCjtpoQ1zxiXg\nlYAoPWGvhB8iDjIMVPDIb32ENQoim7vesVX4lK4gf/0ivy9wm7hBx1XeBfqq2Vj9\nupRhgjHsvqw5C7ICskkvb9s+mm7A9l9nyS440Li/oQKBgQDviWALtimndOsyedBJ\n66TbFq6+v2PDZw04ldK11TAFNfJzX1m0CDjunps1Rnhfrga6HyZ/CH9sabRlF9lM\nDhPkyYDltJM/U2roCgk2kAClO18lrRIaxV+FgCZue5sGdSwIwKGajkmoNp8yAWaJ\nr0kPGiCIn36dqYrAadWIbhE5nwKBgQC2lW3mfU8CpZ/+ZtnUP7dflvLrTltFx5d+\n6vvPMxA9fjcrM9ak7is3k5INmxyE2O8GLWjqFdJxnDAjovPNzjONudKGWiaBw9wb\nclnGjRvxpQWtmtcCRnSiUGZWYeF+O3Wu+eBMq/d8ctl9f112pgVDrs6kLQpqOdzs\nyImZJpViCQKBgDwVknD9nY8ypbiAk72nDTAjjWutaGHgXJGgCz2vHx9/e7Ry63Zc\nRaOdR0NizNj7NxbCr45X3FaeYTCmfcw1D8povRthYzoUO5G+yrbUAkVwEhrKQetT\nLPW4wmseODGzfHspjp/NJy65nM8XSNgqjsHqBNUgZMs5duNy6KwTJ+DzAoGBAJAp\nmGbfFh1+7L8QMno1/PHK2+8TJVoJaALcQwqsxOvo1mKUQaxkKVdue2mmyXPTXZdB\nD4+Uv17Y9eGNbndXkrkaubE/SRw4q3g4Z84v6Jp5s+wJUC8JtlnapZMbIdJr3FXW\nElY3ieeHP1ap1AA0wf9Y7OwQbCLHoTqMdKiqIFURAoGBAKQNirjMY4A56+Y4ufT+\nVeTwbisT3y40kvyi2tHPCr+q5Pnp1/qwGMqJ+p5dJStYmdxoj7+8qTYwXGF0w+hS\n5sl/Z8TN3Ps99pnYxI8zLwUfdwCYvF4aU9m4FZgQvMcgUrZddHCujKQdZSiVucoJ\nLT3Bj4KKj871b1vR3KLOZ7lG\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-v23fm@test-4b666.iam.gserviceaccount.com",
    "client_id": "116912810274541106819",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-v23fm%40test-4b666.iam.gserviceaccount.com"
})

# fb.Room().CreateRoom("launch", "456")#創立房間，給與名稱和密碼

# fb.Room().CreateRoom("123", "123")
# fb.Room().CreateRoom("234", "234")
# fb.Room().CreateRoom("345", "345")

# fb.Account().Register("sam", "sam@gmail.com", "abcd1234") #創立人
# fb.Account().Register("bob", "bob@gmail.com", "bob123")
# fb.Account().Register("abc", "abc@gmail.com", "abc")
# fb.Account().Register("efg", "efg@gmail.com", "efg")
# fb.Account().Register("dfg", "dfg@gmail.com", "dfg")
# fb.Account().Register("fgh", "fgh@gmail.com", "fgh")
# fb.Room().JoinRoom("launch", "456", "louis") #將人加入房間
# fb.Room().JoinRoom("launch", "456", "louis")
# fb.Room().JoinRoom("123", "123", "efg")
# fb.Room().JoinRoom("123", "123", "bob")
# fb.Room().JoinRoom("123", "123", "abc")


# fb.Room().JoinRoom("123", "123", "dfg")
# fb.Room().JoinRoom("234", "234", "abc")
# fb.Room().JoinRoom("123", "123", "fgh")

# print(fb.Function().get().getRoomPpl("123"))

# fb.Account().MoneyUpload("123", "efg", 200, 200)  #加入錢
# fb.Account().MoneyUpload("123", "bob", 120, 265)
# fb.Account().MoneyUpload("123", "fgh", 1000, 300)
# fb.Room().QuitRoom("bob", "123")
# fb.Room().QuitRoom("louis", "123")


# print(fb.Room().findKey("launch"))
# fb.Room().QuitRoom("123", "abc")
# fb.Room().QuitRoom("123", "123")
# fb.Account().DeleteMe("abc")   #刪除該人
# fb.Function().delete().deleteRoom("234")   #刪除房間

fb.settleMent().printSettleMent(fb.settleMent().settleMent("123", "abc"))
