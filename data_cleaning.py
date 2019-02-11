import pandas as pd
import csv

projects = []
project_rows = []

gitHubProjectsTogether = pd.read_csv("githubProjectsTogether.csv", sep=";")
wholeDataSet = pd.read_csv("projects-incl-hackathon.csv", sep=";")
participants_dataframe = pd.read_csv("participants.csv", sep=";")

NUMBER_WITHOUR_TECHS = 0
NUMBER_WITHOUT_PARTICI = 0
NUMBER_WITHOUT_ENOUGH_PROJECTS = 0
NUMBER_WITHOUT_ANY_SKILLS = 0


def noSkillsInTeam(participants):
	participants_split = participants.split("#")

	skilledAmount = 0

	for participant in participants_split:
		participant_row = participants_dataframe.loc[participants_dataframe['id'] == participant]
		try:
			if participant_row['skills'].isnull().bool() == False:
				skilledAmount += 1

		except Exception as e:
			if not participant_row['skills'].empty:
				skilledAmount += 1

	if skilledAmount > 1:
		return True
	else:
		return False


with open('githubProjectsTogether.csv', encoding="utf8") as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=';')
	line_count = 0

	for row in csv_reader:
		if line_count > 0:
			nr_of_techs = str(row[3])
			nr_of_partic = str(row[5])
			hackathon_id = str(row[8])
			devpost_id = str(row[0])
			participants = str(row[4])

			print("ROW NR: " + str(line_count) + " " + devpost_id)

			if int(nr_of_techs) < 1:
				NUMBER_WITHOUR_TECHS += 1
				continue

			if int(nr_of_partic) < 2:
				NUMBER_WITHOUT_PARTICI += 1
				continue

			if not noSkillsInTeam(participants):
				NUMBER_WITHOUT_ANY_SKILLS += 1
				continue

			hackathonProjects = wholeDataSet.loc[wholeDataSet['hackathon-id'] == hackathon_id]

			if len(hackathonProjects) < 4:
				NUMBER_WITHOUT_ENOUGH_PROJECTS += 1
				continue

			projects.append(row)
		else:
			project_rows = row
		#if (line_count == 426):
		#	break
		line_count += 1


	projectsFile = pd.DataFrame(projects, columns=project_rows)
	projectsFile.to_csv('githubProjectsTogetherCleaned.csv', index=False, sep=';')



print(NUMBER_WITHOUT_ENOUGH_PROJECTS)
print(NUMBER_WITHOUT_PARTICI)
print(NUMBER_WITHOUR_TECHS)
print(NUMBER_WITHOUT_ANY_SKILLS)


commits = []
commits_rows = []


with open('githubCommitsTogether.csv', encoding="utf8") as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=';')
	line_count = 0

	for row in csv_reader:
		if line_count > 0:
			days_after = str(row[2])
			devpost_id = str(row[0])

			if int(days_after) > 180:
				continue

			commits.append(row)
		else:
			commits_rows = row
		#if (line_count == 426):
		#	break
		line_count += 1


	commitsFile = pd.DataFrame(commits, columns=commits_rows)
	commitsFile.to_csv('githubCommitsTogetherCleaned.csv', index=False, sep=';')
