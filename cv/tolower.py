with open('dictionary.txt', 'r') as fileinput:
    with open('words3.txt',"w") as fileout:
        for line in fileinput:
            fileout.write(line.lower())
    


       