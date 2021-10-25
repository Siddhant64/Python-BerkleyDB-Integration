import re
import functions

briefMode = True
validQueryPattern = "^(?:date *(?:<|>) *[0-9]{4}\/[0-9]{2}\/[0-9]{2}|(?:(?" \
                    + ":pterm|rterm) *:)? *[0-9a-zA-Z_]+%?|(?:score|price)" \
                    + " *(?:<|>) *[0-9]+)(?:( )+(?:date *(?:<|>) *[0-9]{4}\/[" \
                    + "0-9]{2}\/[0-9]{2}|(?:(?:pterm|rterm) *:)? *[0-9a-zA" \
                    + "-Z_]+%?|(?:score|price) *(?:<|>) *[0-9]+))*$"


class Query:
    def __init__(self):
        self.terms = []
        self.pterms = []
        self.rterms = []
        # (StartPrice, EndPrice)
        self.price = (None, None)
        self.score = (None, None)
        self.date = (None, None)

    def addTerm(self, term):
        if term not in self.terms:
            self.terms.append(term)

    def addPTerm(self, pterm):
        if pterm not in self.pterms:
            self.pterms.append(pterm)

    def addRTerm(self, rterm):
        if rterm not in self.rterms:
            self.rterms.append(rterm)
    
    def addPrice(self, value, operator):
        newprice = value
        if (operator == "<"):
            if self.price[1]:
                newprice = value if value < self.price[1] else self.price[1]
            self.price = (self.price[0], newprice)
        else:
            if self.price[0]:
                newprice = value if value < self.price[0] else self.price[0]
            self.price = (newprice, self.price[1])
    
    def addScore(self, value, operator):
        newscore = value
        if (operator == "<"):
            if self.score[1]:
                newscore = value if value < self.score[1] else self.score[1]
            self.score = (self.score[0], newscore)
        else:
            if self.score[0]:
                newscore = value if value < self.score[0] else self.score[0]
            self.score = (newscore, self.score[1])
    
    def addDate(self, value, operator):
        newdate = value
        if (operator == "<"):
            if self.date[1]:
                newdate = value if value < self.date[1] else self.date[1]
            self.date = (self.date[0], newdate)
        else:
            if self.date[0]:
                newdate = value if value < self.date[0] else self.date[0]
            self.date = (newdate, self.date[1])
    
    def runQuery(self):
        rids = set()
        isSet = False
        if self.pterms:
            for term in self.pterms:
                if isSet:
                    rids = rids.intersection(functions.pterm_search(term))
                else:
                    rids = set(functions.pterm_search(term))
                    isSet = True
        if self.rterms:
            for term in self.rterms:
                if isSet:
                    rids = rids.intersection(functions.rterm_search(term))
                else:
                    rids = set(functions.rterm_search(term))
                    isSet = True
        if self.terms:
            for term in self.terms:
                if isSet:
                    rids = rids.intersection(functions.term_search(term))
                else:
                    rids = set(functions.term_search(term))
                    isSet = True
        if self.score[0] != None or self.score[1] != None:
            if isSet:
                rids = rids.intersection(functions.score_search(self.score))
            else:
                rids = set(functions.score_search(self.score))
                isSet = True
        records = functions.get_records(list(rids))
        filteredrecords = functions.filterPriceDate(records, self.price, self.date)
        printData(filteredrecords)
        

def printData(records):
    if briefMode:
        print("Review ID | Product Title | Score")
        print("--------------------------------------------------")
        for record in records:
            print(record[0], end=" | ")
            print(record[2], end=" | ")
            print(record[7])
    else:
        print("Review ID | Product ID | Product Title | Product Price | User ID | Profile Name | Helpfulness | Score | Timestamp | Summary | Full Review")
        print("--------------------------------------------------------------")
        for record in records:
            for i in range(len(record) - 1):
                print(record[i], end=" | ")
            print(record[-1])

def processQuery(text):
    global briefMode
    text = text.lower()
    if text == "output=brief":
        briefMode = True
        print("output=" + ("brief" if briefMode else "full"))
    elif text == "output=full":
        briefMode = False
        print("output=" + ("brief" if briefMode else "full"))
    else:
        if (not re.match(validQueryPattern, text)):
            print("Invalid query")
            return
        queryObject = Query()
        tokens = []
        for item in text.split(' '):
            if item:
                tokens.append(item)
        
        while len(tokens) > 0:
            token = tokens.pop(0)
            if (re.match("^score(?:(?:<|>)[0-9]*)?$", token)):
                if (token == "score"):
                    if len(tokens) == 0:
                        queryObject.addTerm(token)
                    else:
                        peekNext = tokens[0]
                        if peekNext[0] in ['<', '>']:
                            operator = tokens.pop(0)
                            if len(operator) > 1:
                                queryObject.addScore(operator[1:], operator[0])
                            else:
                                queryObject.addScore(tokens.pop(0), operator)
                elif (token in ["score<", "score>"]):
                    queryObject.addScore(tokens.pop(0), token[5])
                else:
                    queryObject.addScore(token[6:], token[5])
            elif (re.match("^price(?:(?:<|>)[0-9]*)?$", token)):
                if (token == "price"):
                    if len(tokens) == 0:
                        queryObject.addTerm(token)
                    else:
                        peekNext = tokens[0]
                        if peekNext[0] in ['<', '>']:
                            operator = tokens.pop(0)
                            if len(operator) > 1:
                                queryObject.addPrice(operator[1:], operator[0])
                            else:
                                queryObject.addPrice(tokens.pop(0), operator)
                elif (token in ["price<", "price>"]):
                    queryObject.addPrice(tokens.pop(0), token[5])
                else:
                    queryObject.addPrice(token[6:], token[5])
            elif (re.match("^date(?:(?:<|>)(?:[0-9]{4}\/[0-9]{2}\/[0-9]{2})?)?$", token)):
                if (token == "date"):
                    if len(tokens) == 0:
                        queryObject.addTerm(token)
                    else:
                        peekNext = tokens[0]
                        if peekNext[0] in ['<', '>']:
                            operator = tokens.pop(0)
                            if len(operator) > 1:
                                queryObject.addDate(operator[1:], operator[0])
                            else:
                                queryObject.addDate(tokens.pop(0), operator)
                elif (token in ["date<","date>"]):
                    queryObject.addDate(tokens.pop(0), token[4])
                else:
                    queryObject.addDate(token[5:], token[4])
            elif (re.match("^rterm(?::(?:[0-9a-zA-Z_]+%?)?)?$", token)):
                if (token == "rterm"):
                    if len(tokens) == 0:
                        queryObject.addTerm(token)
                    else:
                        peekNext = tokens[0]
                        if peekNext[0] == ":":
                            operator = tokens.pop(0)
                            if len(operator) > 1:
                                queryObject.addRTerm(operator[1:])
                            else:
                                queryObject.addRTerm(tokens.pop(0))
                elif (token == "rterm:"):
                    queryObject.addRTerm(tokens.pop(0))
                else:
                    queryObject.addRTerm(token[6:])
            elif (re.match("^pterm(?::(?:[0-9a-zA-Z_]+%?)?)?$", token)):
                if (token == "pterm"):
                    if len(tokens) == 0:
                        queryObject.addTerm(token)
                    else:
                        peekNext = tokens[0]
                        if peekNext[0] == ":":
                            operator = tokens.pop(0)
                            if len(operator) > 1:
                                queryObject.addPTerm(operator[1:])
                            else:
                                queryObject.addPTerm(tokens.pop(0))
                elif (token == "pterm:"):
                    queryObject.addPTerm(tokens.pop(0))
                else:
                    queryObject.addPTerm(token[6:])
            else:
                queryObject.addTerm(token)
        
        queryObject.runQuery()


def init():
    functions.connect()
