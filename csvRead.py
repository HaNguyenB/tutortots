#by Dan-ha and Ha


import re

tutor_department = list()
def readdata():
  file = open("Tutor Application.csv", "r")
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
  return tutors
  
#create a big dictionary that stores the department as keys
def createdataTutor():
  tutors = readdata()
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

def readdata_tutee():
  tutee_department = list()
  file = open("Tutee Forms.csv", "r")
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

def createdataTutee():
  tutees, tutee_department = readdata_tutee()
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

def tutor_tutee(tutor_list, tutee_list):
  main_dict = {}
  for key in tutor_list:
    if key not in main_dict:
      main_dict[key] = {}
      main_dict[key]["tutors"] = tutor_list[key]
  for key in tutee_list:
    if key not in main_dict:
      main_dict[key] = {}
    else:
      main_dict[key]["tutees"] = tutee_list[key]
  return main_dict

def main():
  tutee = createdataTutee()
  tutor = createdataTutor()
  main_dict = tutor_tutee(tutor,tutee)
  for key in main_dict:
      print(key)
      print(main_dict[key])
      print()
if __name__ == "__main__":
   main()