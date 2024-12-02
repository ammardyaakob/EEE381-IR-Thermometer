
def simpleAvg(xArr: list, yArr : list, holdParameter):

    hold = 0
    total = 0
    currAvg = yArr[0]
    avg = []

    for i in range(len(xArr)):

        # Find current average (sample size set by to holdParameter)
        if hold < holdParameter:
            hold = hold + 1
            total = total + yArr[i] # add values to total
        else: # Once hold = holdParameter e.g. sample size reached
            currAvg = total/holdParameter # calculate average
            hold = 0 # reset sample parameters
            total = 0

        avg.append(currAvg) # add current average to list
    return avg