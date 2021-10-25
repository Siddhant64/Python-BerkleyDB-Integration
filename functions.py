from bsddb3 import db
import time
import datetime


reviewsdb = None
scoresdb = None
ptermsdb = None
rtermsdb = None

def connect():
    global reviewsdb, scoresdb, ptermsdb, rtermsdb
    reviewsdb = db.DB()
    reviewsdb.open("resources/indexfiles/rw.idx", None, db.DB_HASH)
    
    scoresdb = db.DB()
    scoresdb.set_flags(db.DB_DUP)
    scoresdb.open("resources/indexfiles/sc.idx", None, db.DB_BTREE)

    ptermsdb = db.DB()
    ptermsdb.set_flags(db.DB_DUP)
    ptermsdb.open("resources/indexfiles/pt.idx", None, db.DB_BTREE)

    rtermsdb = db.DB()
    rtermsdb.set_flags(db.DB_DUP)
    rtermsdb.open("resources/indexfiles/rt.idx", None, db.DB_BTREE)

def parse(string):
    mystring = list(string)
    output = []
    currentItem = ""
    while (mystring):
        currentChar = mystring.pop(0)
        if (currentChar == '"'):
            currentChar = mystring.pop(0)
            while (currentChar != '"'):
                currentItem = currentItem + currentChar
                currentChar = mystring.pop(0)
            if len(mystring) == 0:
                output.append(currentItem)
                break
            else:
                currentChar = mystring.pop(0)
        while (currentChar != ','):
            currentItem = currentItem + currentChar
            if len(mystring) == 0:
                break
            currentChar = mystring.pop(0)
        output.append(currentItem)
        currentItem = ""
    return output


def get_records(rids):
    global reviewsdb
    curs = reviewsdb.cursor()
    
    records = []
    for rid in rids:
        result = curs.set(rid.encode("utf-8"))
        records.append([rid] + parse(result[1].decode("utf-8")))
    return records


def pterm_search(value):
    global ptermsdb
    return search(ptermsdb.cursor(), value)


def rterm_search(value):
    global rtermsdb
    return search(rtermsdb.cursor(), value)


def term_search(value):
    global rtermsdb, ptermsdb
    list1 = search(rtermsdb.cursor(), value)
    list2 = search(ptermsdb.cursor(), value)
    return list(set().union(list1, list2))



def score_search(value):
    global scoresdb
    curs = scoresdb.cursor()
    
    rids = []
    
    if value[0] == None:
        iter = curs.first()
    else:
        start = value[0].encode("utf-8")
        iter = curs.set_range(start)
        key = iter[0].decode("utf-8")
        while (iter != None and float(key) == float(value[0])):
            iter = curs.next()
            key = iter[0].decode("utf-8")
        
    while (iter):
        key = iter[0].decode("utf-8")
        if value[1] != None:
            if key >= value[1]:
                break
        
        rid = iter[1].decode("utf-8")
        if rid not in rids:
            rids.append(rid)
        dup = curs.next_dup()
        while (dup):
            rid = dup[1].decode("utf-8")
            if rid not in rids:
                rids.append(rid)
            dup = curs.next_dup()
        iter = curs.next()
    return rids


def search(cursor, value):
    curs = cursor

    rids = []
    start = value.strip('%')
    isWildCardEnabled = True if value[-1] == "%" else False
    
    iter = curs.set_range(start.encode("utf-8"))
    while (iter):
        key = iter[0].decode("utf-8")
        if isWildCardEnabled:
            if key[0:len(start)] != start:
                break
        else:
            if key != start:
                break

        rid = iter[1].decode("utf-8")
        if rid not in rids:
            rids.append(rid)
        dup = curs.next_dup()
        while (dup):
            rid = dup[1].decode("utf-8")
            if rid not in rids:
                rids.append(rid)
            dup = curs.next_dup()
        iter = curs.next()
    return rids

def filterPriceDate(records, price, date):
    validrecords =  []
    for record in records:
        isValid = True
        try:
            if not (price[0] == None and price[1] == None):
                price1 = int(price[0]) if price[0] else None
                price2 = int(price[1]) if price[1] else None
                price = (price1, price2)
                curPrice = float(record[3])
                if price[0] != None and price[1] != None:
                    if not (curPrice < price[1] and curPrice > price[0]):
                        isValid = False
                elif price[0] == None:
                    if not (curPrice < price[1]):
                        isValid = False
                elif price[1] == None:
                    if not (curPrice > price[0]):
                        isValid = False
            
        except Exception as e:
            isValid = False
            pass
        try:
            
            if not (date[0] == None and date[1] == None):
                curDate = int(record[8])
                time1 = int(time.mktime(datetime.datetime.strptime(date[0], "%Y/%m/%d").timetuple())) if date[0] else None
                time2 = int(time.mktime(datetime.datetime.strptime(date[1], "%Y/%m/%d").timetuple())) if date[1] else None
                newDate = (time1, time2)
                if newDate[0] != None and newDate[1] != None:
                    if not (curDate < newDate[1] and curDate > newDate[0]):
                        isValid = False
                elif newDate[0] == None:
                    if not (curDate < newDate[1]):
                        isValid = False
                elif newDate[1] == None:
                    if not (curDate > newDate[0]):
                        isValid = False
            
        except:
            isValid = False
            pass
        if isValid:
            validrecords.append(record)
    return validrecords

