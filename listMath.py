import math

# turn list into list of natural logs
def listLn(myList : list):
    lnList = []
    for num in myList:
        lnList.append(math.log(num))
    return lnList

# turn list into list of reciprocals
def listRcp(myList : list):
    rcpList = []
    for num in myList:
        rcpList.append(1/num)
    return rcpList