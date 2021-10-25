import queryhandler

queryhandler.init()
query = input("Enter your query or enter /STOP to exit: ")
while query != '/STOP':
    queryhandler.processQuery(query)
    query = input("Enter your query or enter /STOP to exit: ")
