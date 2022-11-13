

n=4
m=5
weightArr=[[0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff],[0xffffffff,0xffffffff,0,0,0xffffffff],[0,0xffffffff,0xffffffff,-12,0xffffffff],[0xffffffff,0xffffffff,-12,0xffffffff,0]]
maxTutees=[1,2,2,1,4]

for i in range(n):
    for j in range(m):
        if weightArr[i][j]>0x1fffff:
            weightArr[i][j]=0x1fffff





with open("program.lp","w") as f:
    f.write("Minimize\n")
    
    #write pairing weights
    for i in range(n):      
        for j in range(m):
            f.write(f"\t{weightArr[i][j]} x.{i}.{j} + \n")
    
    #write even distribution weights
    for i in range(n-1):
        for j in range(n-i-1):
            f.write(f"\td.{i}.{j+i+1} + \n")

    #write ghost tutor weights
    for j in range(m):
        f.write(f"\t50000 g.{j} + \n")

    f.write("\tZero\n\nSubject To\n")

    # 1 tutor per tutee
    for j in range(m):
        f.write(f"\tSingleTutor.{j}: ")
        for i in range(n):
            f.write(f"x.{i}.{j} + ")
        f.write(f"g.{j} + ")            # ghost tutor counts as a tutor here
        f.write("Zero = 1 \n")
    f.write("\n")

    # no tutor gets more tutees than they requested
    for i in range(n):
        f.write(f"\tXTutees.{i}: ")
        for j in range(m):
            f.write(f"x.{i}.{j} + ")             # ghost tutor can take infinitely many tutees
        f.write(f"Zero <= {maxTutees[i]} \n")
    f.write("\n")

    # save for specific pair requests, try to distribute tutees evenly among tutors - this defines the variables used for that
    for i in range(n-1):
        for j in range(n-i-1):
            f.write(f"\tD.{i}.{j+i+1}.1: ")
            for k in range(m):
                f.write(f"x.{i}.{k} - x.{j+i+1}.{k} + ")
            f.write(f"Zero - d.{i}.{j+i+1} <= 0 \n")
            f.write(f"\tD.{i}.{j+i+1}.2: ")
            for k in range(m):
                f.write(f"x.{j+i+1}.{k} - x.{i}.{k} + ")
            f.write(f"Zero - d.{i}.{j+i+1} <= 0 \n")
    f.write("\n")
    f.write("\tZero = 0\n")

    f.write("\nBinary\n")
    
    for i in range(n):
        for j in range(m):
            f.write(f"\tx.{i}.{j} \n")

    for j in range(m):
        f.write(f"\tg.{j} \n")
    
    f.write("\nInteger\n")

    for i in range(n-1):
        for j in range(n-i-1):
            f.write(f"\td.{i}.{j+i+1} \n")

    f.write("End")

