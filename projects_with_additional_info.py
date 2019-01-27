import pandas as pd
import numpy as np
import matplotlib.pyplot as plt   #Data visualisation libraries
import csv
import datetime
import math


commits_dataframe = pd.read_csv("githubCommits.csv", sep=";")
participants_dataframe = pd.read_csv("participants.csv", sep=";")

projects = []
project_rows = []

work_more_after = 0

def common_elements(list1, list2):
	return list(set(list1) & set(list2))


def isProjectDormantMonthly(commits_rows, hackathon_end_date):
	hackathonEndDateParts = hackathon_end_date.split("-")
	hackathonEndDate = datetime.date(int(hackathonEndDateParts[0]), int(hackathonEndDateParts[1]),
									 int(hackathonEndDateParts[2]))
	isTwoMonthsActive = False
	isTwoToFourMonthsActive = False
	isFourToSixMonthsActive = False
	isSixToEightMonthsActive = False


	for i in range(1, 61):
		hackathonEndDate += datetime.timedelta(days=1)
		for commit in commits_rows.values:
			commit_date = convertDate(commit[3])
			if hackathonEndDate == commit_date:
				isTwoMonthsActive = True


	for i in range(1, 61):
		hackathonEndDate += datetime.timedelta(days=1)

		for commit in commits_rows.values:
			commit_date = convertDate(commit[3])
			if hackathonEndDate == commit_date:
				isTwoToFourMonthsActive = True


	for i in range(1, 61):
		hackathonEndDate += datetime.timedelta(days=1)

		for commit in commits_rows.values:
			commit_date = convertDate(commit[3])
			if hackathonEndDate == commit_date:
				isFourToSixMonthsActive = True

	for i in range(1, 61):
		hackathonEndDate += datetime.timedelta(days=1)

		for commit in commits_rows.values:
			commit_date = convertDate(commit[3])
			if hackathonEndDate == commit_date:
				isSixToEightMonthsActive = True

	if (isTwoMonthsActive and isTwoToFourMonthsActive and isFourToSixMonthsActive and isSixToEightMonthsActive):
		return 0
	else:
		return 1


# One commit on average in 9 months
def isProjectDormantInAverage(commits_rows, hackathon_end_date):
	hackathonEndDateParts = hackathon_end_date.split("-")
	hackathonEndDate = datetime.date(int(hackathonEndDateParts[0]), int(hackathonEndDateParts[1]),
									 int(hackathonEndDateParts[2]))


	average = len(commits_rows) / 9

	if average >= 1.0:
		return 0
	else:
		return 1







def skillDiversity(participants, technologies):
	participants = participants.split('#')
	technologies = technologies.split('#')

	participantsAmount = len(participants)
	technologyWeight = 1 / len(technologies)

	techs = {}
	skillDiversity = 0


	for tech in technologies:
		techs[tech] = 0


	for participant in participants:
		participant_row = participants_dataframe.loc[participants_dataframe['id'] == participant]
		if (not participant_row['skills'].isnull().bool()):
			participant_technologies = participant_row['skills'].tolist()[0].split('#')  # From dataframe to series to list -> taking first element and splitting it by #.
			for tech in techs:
				if tech in participant_technologies:
					techs[tech] += 1

	for x in techs.values():
		if (x / participantsAmount) >= 0.75:
			skillDiversity += technologyWeight
		else:
			skillDiversity += (technologyWeight * x) / participantsAmount


	return skillDiversity


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

with open('githubProjects.csv', encoding="utf8") as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=';')
	line_count = 0

	for row in csv_reader:
		if line_count > 0:
			work_after = str(row[19])
			github_url = str(row[14]).strip()
			technologies = str(row[2])
			participants = str(row[4])
			hackathon_end_date = str(row[11]).strip()
			if work_after == "1":
				try:
					devpost_id = str(row[0])
					hackathon_end_date = str(row[11]).strip()

					print("ROW NR: " + str(line_count) + " " + devpost_id)
					commits_rows = commits_dataframe.loc[commits_dataframe['commit_id'] == devpost_id]
					committers = []
					commit_dates = [] # ONLY UNIQUE VALUES?
					for commit_row in commits_rows.values:
						committer = commit_row[4]
						committers.append(committer)
						commit_dates.append(commit_row[3])


					# Unique commit days
					commit_dates_unique = unique(list(set(commit_dates)))

					# Unique commiters
					committers = unique(list(set(committers)))


					# Commits amount
					commits_amount = len(commits_rows)

					# Last day the project was active
					days_after_hackathon = commits_rows.values[-1][2]

					# Commits/days active
					commits_slash_days = commits_amount / days_after_hackathon

					# Skills diversity
					skillPercentage = roundup(skillDiversity(participants, technologies), 1)

					# Commits / 270 days -> commits frequency
					commits_slash_all_days = commits_amount / 270


					# Project dormancy
					#commits_frequency_dormant = isProjectDormantMonthly(commits_rows, hackathon_end_date)
					commits_frequency_dormant = isProjectDormantInAverage(commits_rows, hackathon_end_date)


					row = row + [str(skillPercentage) , str(commits_amount), str(days_after_hackathon), len(committers), commits_slash_days, str(len(commit_dates_unique)),str(commits_frequency_dormant), str(commits_slash_all_days)]

					projects.append(row)
				except Exception as e:
					print("error")
					print(e)
					work_more_after += 1
					print(row)
			else:
				if github_url:
					projects.append(row + ["0", "0", "0", "0", "0", "0", "1", "0"])


		else:
			project_rows = row + ["skillsCovered", "commits", "days_after_hackathon_for_last_commit", "contributors_amount", "commits_slash_last_active_day", "days_which_has_commits", "commits_frequency_dormant", "commits_slash_all_days"]
		#if (line_count == 50):
		#	break
		line_count += 1


	projectsFile = pd.DataFrame(projects, columns=project_rows)
	projectsFile.to_csv('githubProjects_with_extra_info.csv', index=False, sep=';')



print("WORK MORE AFTER: " + str(work_more_after))
