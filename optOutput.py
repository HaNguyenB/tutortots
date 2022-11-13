# by Otavio Paz Nascimen

from datetime import datetime

tutors = [{"id" : 0, "name" : "Bob", "tnumber" : 123151},{"id" : 1, "name" : "Alice", "tnumber" : 223151},{"id" : 2, "name" : "Carrie", "tnumber" : 123100},{"id" : 3, "name" : "Dominic", "tnumber" : 993151}]

tutees = [{"id" : 0, "name" : "Jefferson", "tnumber" : 120051},{"id" : 1, "name" : "Stefany", "tnumber" : 103101},{"id" : 2, "name" : "Octavio", "tnumber" : 100001},{"id" : 3, "name" : "Sonia", "tnumber" : 169151}, {"id" : 4, "name" : "Alexander", "tnumber" : 123000}]

def evaluate_assignment(list):
#   """
#   This function accepts a list of the assingments and returns a boolean based on the evaluation.
#   """
  objective_value = list[0]
  if objective_value < 0:
    is_good = True
  elif objective_value > 1000:
    is_good = False

  return is_good

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

def get_tutor_name(id):
#   """
#   This function gets an id and returns the name of the tutor.
#   """
  name = ''
  for dict in tutors:
    if dict["id"] == id:
      name = dict["name"]
  return name
  
def get_tutee_name(id):
#   """
#   This function gets an id and returns the name of the tutee.
#   """
  name = ''
  for dict in tutees:
    if dict["id"] == id:
      name = dict["name"]
  return name

def dictionary(assignment_list):
  #"""
  #This function gets an assignment_list and returns a dictionary.
  #Key is the tutor and the value is a list of the names of the tutees of that respect tutor.
  #{tutor: [tutee], tutor: [tutee], tutor: [tutee, tutee], tutor: [tutee]}
  #"""
  tutors_assignments = {} #tutors are keys
 
  for assignment in assignment_list:
    if assignment[0] == 'x':
      if assignment[3] == 1: #check last digit
  
        tutor_name = get_tutor_name(assignment[1])
        tutee_name = get_tutee_name(assignment[2])
        
        if tutor_name not in tutors_assignments.keys():
          
          tutors_assignments[tutor_name] = [tutee_name]
          
        else:
          tutors_assignments[tutor_name].extend([tutee_name])
    
  return tutors_assignments

def find_tnumber(name):
  #"This function accepts a name and find the tnumber that matches the name"
  tnumber = 0
  for dict in tutors:
    if dict["name"] == name:
      tnumber = dict["tnumber"]

  for dict2 in tutees:
    if dict2["name"] == name:
      tnumber = dict2["tnumber"]

  return tnumber

def create_txt(tutors_list, ghost):
  timestamp = datetime.now()
  colon=':'
  d4 = timestamp.strftime(f"%Y-%m-%d_%H-%M")
  filename = f"assignments/assignment"+d4 

  with open(filename, 'w') as f:
    for tutor in tutors_list.keys():
      f.write(f"{tutor} - T-Number: {find_tnumber(tutor)}\n")
      for tutee in tutors_list[tutor]:
        f.write(f"\t {tutee} - T-Number: {find_tnumber(tutee)}\n")
      f.write(f"\n")
    f.write("\nUnassigned\n")
    for tutee in ghost:
        f.write(f"\t {get_tutee_name(tutee)} - T-Number: {find_tnumber(get_tutee_name(tutee))}\n")
  

def main():
  filename = "sampleOut.sol"
  assignment_list = read_data(filename)
  #print(assignment_list)
  tutors_list = dictionary(assignment_list)
  #print()
  #print(tutors_list)
  ghost = check_unassigned(filename)
  create_txt(tutors_list,ghost)
  


#if __name__ == '__main__':
main()