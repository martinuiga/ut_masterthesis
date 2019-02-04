import pandas as pd
import csv
import datetime
import math
from itertools import combinations

commits_dataframe = pd.read_csv("githubCommitsTogether.csv", sep=";")
participants_dataframe = pd.read_csv("participants.csv", sep=";")

participant_headers = []
participant_rows = []


def common_elements(list1, list2):
	return list(set(list1) & set(list2))


def unique(list1):
	# intilize a null list
	unique_list = []

	# traverse for all elements
	for x in list1:
		# check if exists in unique_list or not
		if x not in unique_list:
			unique_list.append(x)
	return unique_list

def convertDate(date):
	dateParts = date.split("T")[0]
	latestCommitParts = dateParts.split("-")
	return datetime.date(int(latestCommitParts[0]), int(latestCommitParts[1]), int(latestCommitParts[2]))

def roundup(a, digits=0):
    n = 10**-digits
    return round(math.ceil(a / n) * n, digits)

participant_project_count = {}

with open('githubProjectsTogether.csv', encoding="utf8") as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=';')
	line_count = 0


	for row in csv_reader:
		if line_count > 0:
			work_after = str(row[19])
			github_url = str(row[14]).strip()
			technologies = str(row[2])
			participants = str(row[4])
			hackathon_end_date = str(row[11]).strip()
			try:
				participants_separated = participants.split("#")

				for participant in participants_separated:
					if(participant_project_count.keys().__contains__(participant)):
						participant_project_count[participant] += 1
					else:
						participant_project_count[participant] = 1


			except Exception as e:
				print("error")
				print(e)
				print(row)

		else:
			project_rows = row
		#if (line_count == 2000):
		#	break
		line_count += 1

print(participant_project_count)


githubProjectsDataFrame = pd.read_csv("githubProjects_with_extra_info.csv", sep=";")
participant_pair_count = {}

# Filter the project count list, include only the ones with 2 or more -> make all the possible combination of them and
# start to search the combinations in project rows.
# If a combination is twice then put into pairs library

participants_with_more_than_two_projects = []

for (key, value) in participant_project_count.items():
	if value > 1:
		participants_with_more_than_two_projects.append(key)

participants_with_more_than_two_projects_combinations = (list(combinations(participants_with_more_than_two_projects, 2)))


#############################


participant_worked_together_count = {}

with open('githubProjectsTogether.csv', encoding="utf8") as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=';')
	line_count = 0


	for row in csv_reader:
		if line_count > 0:
			participants = str(row[4])
			try:
				participants = participants.split("#")

				for (pair1, pair2) in participants_with_more_than_two_projects_combinations:
					if (pair1 in participants) and (pair2 in participants):
						pairTogether = pair1 + "#" + pair2

						if (participant_worked_together_count.keys().__contains__(pairTogether)):
							participant_worked_together_count[pairTogether] += 1
						else:
							participant_worked_together_count[pairTogether] = 1


			except Exception as e:
				print("error")
				print(e)
				print(row)

		else:
			project_rows = row
		#if (line_count == 1500):
		#	break
		line_count += 1


print(participant_worked_together_count)

## FILTER OUT THE WORKED TOGETHER COUNT OUT OF 1's

filtered_participant_worked_together_count = {}

for (key, value) in participant_worked_together_count.items():
	if value > 1:
		filtered_participant_worked_together_count[key] = value

print(filtered_participant_worked_together_count)




