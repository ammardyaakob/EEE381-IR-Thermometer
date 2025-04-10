from queue import Queue

def simpleAvg(yArr : list, holdParameter):

    hold = 0
    total = 0
    currAvg = 0
    avg = []
    queue = Queue(maxsize=holdParameter)

    for i in range(len(yArr)):

        if not queue.full():
            queue.put(yArr[i])
            total = total + yArr[i]
            currAvg = total / (i+1)

        else:
            total = (currAvg * holdParameter) + yArr[i] - queue.get() #  new sum = the current average * the amount of values that made the average + new value - old value
            queue.put(yArr[i])
            currAvg = total / holdParameter

        avg.append(currAvg) # add current average to list
    return avg
