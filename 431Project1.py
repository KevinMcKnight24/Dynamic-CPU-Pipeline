def main(f):
    #Instantiating varaiables
    committedInsts=0
    icount = 0
    instNum = 0  
    cycleNum = 0
    numOfIssueCalls = 4
    numOfWBCalls = 5
    numOfCommitCalls = 6
    numOfRenameCalls = 2
    #Creating the list with all the instructions
    Lines = f.readlines()
    inst = []
    temp = []
    for line in Lines:
        temp.append(line.strip())
        inst.append(temp[icount].split(","))
        icount += 1
    #Creating the structures I need for the code
    machineWidth = int(inst[0][1])
    physicalRegs = int(inst[0][0])
    inst.pop(0)
    icount -= 1
    #Creating the list that I will add all the numbers to and return
    finalList = []
    for i in range(icount):
        finalList.append([])
    mapTable = []
    freeList = []
    readyTable = []
    rob = []
    for i in range(33):
        mapTable.append(i)
        freeList.append(True)
        readyTable.append(True)
    for i in range(33, physicalRegs + 33):
        freeList.append(False)
        readyTable.append(True)
    instructions = []
    issueQueue = []

    
    for i in range(icount):
        for j in range(4):
            finalList[i].append(j + (i//machineWidth))

    while(committedInsts<icount):
        while (len(issueQueue) < min(machineWidth, icount - committedInsts)):
            instructions.append(fetch(inst, instNum))
            instType, rs, rt, rd = (Decode(instructions[instNum]))
            reRs, reRt, reRd, mapTable, freeList, numOfRenameCalls, finalList = Rename(instType, rs, rt, rd, mapTable, freeList, numOfRenameCalls, finalList, instNum)
            issueQueueAdd, readyTable = Dispatch(instType, reRs, reRt, reRd, readyTable)
            issueQueueAdd.append(instNum)
            issueQueue.append(issueQueueAdd)
            rob.append(issueQueueAdd)
            instNum += 1
        
    
        
        issueQueue, finalList, numOfIssueCalls = Issue(issueQueue, finalList, readyTable, numOfIssueCalls)
        issueQueue, finalList, readyTable, committedInsts, numOfWBCalls, rob = WB(issueQueue, finalList, readyTable, committedInsts, numOfWBCalls, rob)
        #readyTable, rob = Commit(readyTable, rob)

        cycleNum += 1


    for i in range(icount):
        if(i > 0):
            finalList[i].append(max((finalList[i][-1] + 1),finalList[i-1][-1]))
        else:
            finalList[i].append(finalList[i][-1] + 1)

    for i in range(len(finalList)):
        finalList[i] = [str(x) for x in finalList[i]]
        
    newF = open('out.txt', 'w')
    for element in finalList:
        newF.write(",".join(element))
        newF.write("\n")
    newF.close()        
    return(newF)


def fetch(inst, instNum):
    return inst[instNum]

def Decode(instruction):
    instType = instruction[0]
    rs = instruction[1]
    rt = instruction[2]
    rd = instruction[3]
    return instType, int(rs), int(rt), int(rd)

def Rename(instType, rs, rt, rd, mapTable, freeList, numOfRenameCalls, finalList, instNum):
    reRs = 0
    reRt = 0
    reRd = 0
    flag = False
    i = 32
    if(instType == "S"):
        reRs = mapTable[rs]
        reRt = rt
        reRd = mapTable[rd]
    else:
        if instType == "L":
            reRt = rt
        else:
            reRt = mapTable[rt]
    if instType == "I":
        reRd = rd
    else:
        reRd = mapTable[rd]

    if(instType != "S"):
        while flag is False:
            if freeList[i] == False:
                freeList[i] = True
                mapTable[rs] = i
                reRs = i
                flag = True
            else:
                i += 1

    return int(reRs), int(reRt), int(reRd), mapTable, freeList, numOfRenameCalls, finalList

def Dispatch(instType, reRs, reRt, reRd, readyTable):
    goToIQ = []
    goToIQ.append(instType)
    if(instType == "R" or instType == "I"):
        goToIQ.append(reRt)
        goToIQ.append(readyTable[reRt])
        goToIQ.append(reRd)
        goToIQ.append(readyTable[reRd])
        goToIQ.append(reRs) 
        readyTable[reRs] = False
    elif(instType == "L"):
        goToIQ.append("")
        goToIQ.append(True)
        goToIQ.append(reRd)
        goToIQ.append(readyTable[reRd])
        goToIQ.append(reRs)
        readyTable[reRs] = False
    else:
        goToIQ.append(reRs)
        goToIQ.append(readyTable[reRs])
        goToIQ.append(reRd)
        goToIQ.append(readyTable[reRd])
        goToIQ.append(0)

    return goToIQ, readyTable


def Issue(issueQueue, finalList, readyList, numOfIssueCalls):
    sOrNaw, sAge = False, 0
    for i in range(len(issueQueue)):
        if(issueQueue[i][0] != "L"):
            issueQueue[i][2] = readyList[issueQueue[i][1]]
        issueQueue[i][4] = readyList[issueQueue[i][3]]

    for i in issueQueue:
        if i[0] == "S":
            sOrNaw, sAge = True, i[6]

    for i in issueQueue:
        if i[2] == True and i[4] == True:
            if(i[0] == "L" and sOrNaw == True and sAge < i[6]):
                continue
            else:
                finalList[i[6]].append(numOfIssueCalls)
                i.append(True)

    numOfIssueCalls += 1
    return issueQueue, finalList, numOfIssueCalls

def WB(issueQueue, finalList, readyList, committedInst, numOfWBCalls, rob):
    for i in range(len(issueQueue)):
        if len(issueQueue[i]) > 7:
            if(issueQueue[i][0] != "S"):
                readyList[issueQueue[i][5]] = True
            committedInst += 1
            finalList[issueQueue[i][6]].append(numOfWBCalls)
            #rob[issueQueue[i][6]].append("commit")
            issueQueue[i] = ""

    while "" in issueQueue:
        issueQueue.remove("")

    numOfWBCalls += 1
    return issueQueue, finalList, readyList, committedInst, numOfWBCalls, rob

'''
def Commit(readyTable, rob):
    for i in range(len(rob)):
        if rob[i][-1] == "commit":
            readyTable[rob[i][6]] == False

    return readyTable, rob
    '''
f = open("test.in", "r")
main(f)