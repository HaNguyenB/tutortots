import subprocess
from datetime import datetime
import re
import sys



#assuming tutors is a list of dictionaries of the form {id : int, courses : list of string or int, preferred : list of IDs, blacklist : list of IDs, maxTutees : int}
#assuming tutees is a list of dictionaries of the form {id : int, courses : list of string or int, preferred : list of IDs, blacklist : list of IDs}

def readdata(filename):
  tutor_department = list()
  file = open(filename, "r")
  lines = file.readlines()
  file.close()
  tutors = list()
  
  for line in lines[1:]:
    #get the list of all the classes one tutor is tutoring for
    res = re.findall(r'\[.*?\]', line)
    res[0] = ((res[0].replace('"', '')).replace('[', '')).replace(']', '')
    res[0] = res[0].split(',')
    #read the csv file and put data of each tutor in a list. index 0 = date of the input, index 1 = full name of the tutor, index 2 = t number, index 3 = deparment, index 4 = the email of the person they want to work with, index 5 = the email of the person they don't want to work with, index 6 = the tutor's email
    line = line.strip()
    line = line.split(",")
    tutor = list()
    for i in range (7):
      tutor.append(line[i].strip('\"'))
    tutor.append(res[0])
    tutor.append(line[-1])
    tutor_department.append(tutor[3]) #get a list of the departments which have tutors
    tutors.append(tutor)
  return tutors, tutor_department
  
#create a big dictionary that stores the department as keys
def createdataTutor(filename):
  tutors, tutor_department = readdata(filename)
  dict_department = {}
  #create and a dictionary of all the deparments that have tutors/tutees (no duplicate keys)
  for element in tutor_department:
    if element not in dict_department:
      dict_department[element] = list()
  #loop through all the departments and check the tutor list to see who belongs to which deparment
  for k in dict_department:
    n = 0
    for i in tutors:
      if i[3] == k:
        tutor_dict = {}
        tutor_dict["id"] = n
        tutor_dict["tnumber"] = int(i[2])
        tutor_dict["name"] = i[1]
        tutor_dict["courses"] = i[7]
        #if preferred or blacklist is empty then insert an empty list:
        if i[4] == '':
          tutor_dict["preferred"] = list()
        else:
          tutor_dict["preferred"] = i[4].split(",")
        if i[5] == '':
          tutor_dict["blacklist"] = list()
        else:
          tutor_dict["blacklist"] = i[5].split(",")
        tutor_dict["max"] = int(i[-1])
        if tutor_dict not in dict_department[k]:
          dict_department[k].append(tutor_dict)
        n+=1  
  return dict_department        

def readdata_tutee(filename):
  tutee_department = list()
  file = open(filename, "r")
  lines = file.readlines()
  file.close()
  tutees = list()
  
  for line in lines[1:]:
    line = line.strip()
    line = line.split(",")
    tutee = list()
    for i in range (10):
      if line[i] == '' and i >= 7:
        continue
      else:
        tutee.append(line[i].strip('\"'))
    tutee_department.append(tutee[4])
    tutees.append(tutee)
  return tutees, tutee_department

def createdataTutee(filename):
  tutees, tutee_department = readdata_tutee(filename)
  #print(tutees)
  dict = {}
  #add all the deparments that have tutee (no duplication)
  for element in tutee_department:
    if element not in dict:
      dict[element] = list()
  
  for element in dict:
    n = 0
    for i in tutees:
      if i[4] == element:
        tutee_dict = {}
        tutee_dict["id"] = n
        tutee_dict["tnumber"] = int(i[3])
        tutee_dict["name"] = i[1]
        tutee_dict["courses"] = i[-1]
        #if preferred or blacklist is empty then insert an empty list:
        if i[5] == '':
          tutee_dict["preferred"] = list()
        else:
          tutee_dict["preferred"] = i[5].split(",")
        if i[6] == '':
          tutee_dict["blacklist"] = list()
        else:
          tutee_dict["blacklist"] = i[6].split(",")
        
        if tutee_dict not in dict[element]:
          dict[element].append(tutee_dict)
        n+=1
  return dict

def tutor_tutee(tutor_list, tutee_list,fp):
  main_dict = {}
  for key in tutor_list:
    if key not in main_dict:
      main_dict[key] = {}
      main_dict[key]["tutors"] = tutor_list[key]
    else:
      main_dict[key]["tutors"] = tutor_list[key]
  for key in tutee_list:
    if key not in main_dict:
      main_dict[key] = {}
      main_dict[key]["tutees"] = tutee_list[key]
    else:
      main_dict[key]["tutees"] = tutee_list[key]
  fp.write(f"{main_dict}\n")
  return main_dict




#populates weightArr with appropriate weights given data from tutors and tutees
def calculateWeights(tutors, tutees, weightArr):
    n=len(weightArr)
    m=len(weightArr[0])

    for tutor in tutors:            #loop across all tutors and tutees
        for tutee in tutees:
            weight=0                #each tutor-tutee pair will have a weight assigned to them - goal is to minimize total weight
            
            #course constraints
            for course in tutee["courses"]:
                if course not in tutor["courses"]:  #check class constraints
                    weight+=0xffffffff          #2^32-1 will represent infty for us - this assumes the number of tutors/tutees is relatively small
            
            #preferred pairs 
            if tutor["id"] in tutee["preferred"]: #check if tutee wanted this tutor
                weight-=1.5*n
                if tutee["id"] in tutor["preferred"]:     #check if both wanted eachother
                    weight-=8.5*n
            elif tutee["id"] in tutee["preferred"]: #check if tutor wanted this tutee
                weight-=1.5*n

            #incompatible pairs
            if tutor["id"] in tutee["blacklist"]:
                weight+=0xffffffff
            elif tutee["id"] in tutee["blacklist"]:
                weight+=0xffffffff

            weightArr[tutor["id"]][tutee["id"]]=weight
            
#gurobi doesn't like very big numbers and may lose accuracy/efficiency
    for i in range(n):
        for j in range(m):
            if weightArr[i][j]>0x1fffff:
                weightArr[i][j]=0x1fffff
    return weightArr

#creates program.lp based on data in weightArr
def createLP(tutors, weightArr):
    n=len(weightArr)
    m=len(weightArr[0])
    
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
            f.write(f"Zero <= {tutors[i]['max']} \n")
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

#runs Gurobi solver on program.lp and creates output file assignment.sol
def runGurobi():
    subprocess.run(["gurobi_cl", "ResultFile=assignment.sol", "program.lp"])

def read_data(filename):
#   """
#   This function reads a file and returns a list of the lines.
#   """
  
  file = open(filename, "r")
  lines = file.readlines()
  formatted = []
  
  for line in lines:

    #get all the lines that start with x
    if 'x' in line:
      formatted.append(line.strip().replace(' ', '.').split('.'))
 
    #get the objective value line
    elif '=' in line:
      first_line = line
      
      first_line = first_line.strip().split('=')

      objective_value = int(first_line[1])
      formatted.append([objective_value])

  #convert the list of string to integers
  for list in formatted:
    for index in range(len(list)):
      if list[index] != 'x':
        list[index] = int(list[index])
  
  file.close()

  return formatted


def check_unassigned(filename):
  file = open(filename, "r")
  lines = file.readlines()
  
  unassigned = []

  for line in lines:

    #get all the lines that start with g (ghost as in unassigned tutee)
    if 'g' in line:
      unassigned.append(line.strip().replace(' ', '.').split('.'))

  #convert the list of string to integers
  for line in unassigned:
    for index in range(len(line)):
      if line[index] != 'g':
        line[index] = int(line[index])
  
  file.close()

  tutees_unassigned = {}

  # check if this is going to work
  for assignment in unassigned:
    if assignment[0] == 'g':
      if assignment[2] == 1: #check last digit
  
        tutee_name = get_tutee_name(assignment[1])
        
        if assignment[1] not in tutees_unassigned.keys():
          
          tutees_unassigned[assignment[1]] = [tutee_name]
      
  return tutees_unassigned

def get_tutor_name(id, tutors):
#   """
#   This function gets an id and returns the name of the tutor.
#   """
  name = ''
  for dict in tutors:
    if dict["id"] == id:
      name = dict["name"]
  return name
  
def get_tutee_name(id, tutees):
#   """
#   This function gets an id and returns the name of the tutee.
#   """
  name = ''
  for dict in tutees:
    if dict["id"] == id:
      name = dict["name"]
  return name

def makeDict(assignment_list, tutors, tutees):
  #"""
  #This function gets an assignment_list and returns a dictionary.
  #Key is the tutor and the value is a list of the names of the tutees of that respect tutor.
  #{tutor: [tutee], tutor: [tutee], tutor: [tutee, tutee], tutor: [tutee]}
  #"""
  tutors_assignments = {} #tutors are keys
 
  for assignment in assignment_list:
    if assignment[0] == 'x':
      if assignment[3] == 1: #check last digit
  
        tutor_name = get_tutor_name(assignment[1], tutors)
        tutee_name = get_tutee_name(assignment[2], tutees)
        
        if tutor_name not in tutors_assignments.keys():
          
          tutors_assignments[tutor_name] = [tutee_name]
          
        else:
          tutors_assignments[tutor_name].extend([tutee_name])
    
  return tutors_assignments

def find_tnumber(name, tutors, tutees):
  #"This function accepts a name and find the tnumber that matches the name"
  tnumber = 0
  for dict in tutors:
    if dict["name"] == name:
      tnumber = dict["tnumber"]

  for dict2 in tutees:
    if dict2["name"] == name:
      tnumber = dict2["tnumber"]

  return tnumber

def create_txt(tutors_list, ghost, tutors, tutees,subject):
  timestamp = datetime.now()
  colon=':'
  d4 = timestamp.strftime(f"%Y-%m-%d_%H-%M")
  filename = f"assignments/{subject}assignment{d4}" 

  with open(filename, 'w') as f:
    for tutor in tutors_list.keys():
      f.write(f"{tutor} - T-Number: {find_tnumber(tutor, tutors, tutees)}\n")
      for tutee in tutors_list[tutor]:
        f.write(f"\t {tutee} - T-Number: {find_tnumber(tutee, tutors, tutees)}\n")
      f.write(f"\n")
    f.write("\nUnassigned\n")
    for tutee in ghost:
        f.write(f"\t {get_tutee_name(tutee, tutees)} - T-Number: {find_tnumber(get_tutee_name(tutee, tutees))}\n")
  

def main():
  tutorFilename=sys.argv[1]
  tuteeFilename=sys.argv[2]
  log=open("log.txt",'w')
  log.write(f"{tuteeFilename}\n")
  log.write(f"{tutorFilename}\n")

  tuteeData = createdataTutee(tuteeFilename)
  tutorData = createdataTutor(tutorFilename)

  log.write(f"{tuteeData}\n")
  log.write(f"{tutorData}\n")

  data = tutor_tutee(tutorData,tuteeData,log)
  f=open("data.txt",'w')
  f.write(f"{data}\n")
  f.close()

  log.write(f"{data.keys()}\n")
  

  for subject in data.keys():
    log.write(f"writing key {subject}\n")
    tutors=data[subject]["tutors"]
    tutees=data[subject]["tutees"]

    log.write(f"extracted tutors: {tutors}\n")
    log.write(f"extracted tutees: {tutees}\n")

    weightArr=[None]*len(tutors)
    for i in range(len(tutors)):
      weightArr[i]=[None]*len(tutees)

    log.write(f"initialized weightArray: {weightArr}\n")

    weightArr=calculateWeights(tutors, tutees, weightArr)

    log.write(f"populated weightArray: {weightArr}\n")

    createLP(tutors, weightArr)

    log.write(f"created .lp file\n")

    runGurobi()

    filename = "assignment.sol"
    assignment_list = read_data(filename)
    log.write(f"read data of assignment sol\n")
    #print(assignment_list)
    tutors_list = makeDict(assignment_list, tutors, tutees)
    #print()
    #print(tutors_list)
    ghost = check_unassigned(filename)
    create_txt(tutors_list,ghost,tutors,tutees,subject)


main()