import pandas as pd
import numpy as np
import matplotlib.pyplot as plt   #Data visualisation libraries
import csv
import datetime
import math
from itertools import combinations




wholeDataSet = pd.read_csv("projects-incl-hackathon.csv", sep=";")
commits_dataframe = pd.read_csv("githubCommitsTogetherCleaned.csv", sep=";")
gitHubProjectsTogether = pd.read_csv("githubProjectsTogetherCleaned.csv", sep=";")
participants_dataframe = pd.read_csv("participants.csv", sep=";")

projects = []
project_rows = []

work_more_after = 0

### UTILS ###

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

#############

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
def isProjectDormantInAverage(commits_rows):
	average = len(commits_rows) / 6

	if average >= 1.0:
		return 1
	else:
		return 0


def calculateWinnerWeight(hackathons):

	howManyProjects = len(hackathons)
	howManyWinners = 0

	for hackathon in hackathons.values:
		isWinner = str(hackathon[15])

		if isWinner == "1":
			howManyWinners += 1

	coefficent = 1 / howManyProjects

	return (coefficent * howManyProjects) / howManyWinners



def calculateWinnerWeightPercentage(hackathons):

	howManyProjects = len(hackathons)
	howManyWinners = 0

	for hackathon in hackathons.values:
		isWinner = str(hackathon[15])

		if isWinner == "1":
			howManyWinners += 1

	if howManyWinners == 1:
		return 1
	elif howManyWinners == 0:
		return 0
	elif howManyProjects == howManyWinners:
		return 1 / howManyWinners
	else:
		return 1 - ((1.0 * howManyWinners) / howManyProjects)


# Project's skill diversity
def skillDiversity(participants, technologies):
	participants = participants.split('#')
	technologies = technologies.split('#')

	participantsAmount = len(participants)
	technologyWeight = 1 / len(technologies)

	techs = {}
	skillDiversity = 0
	no_skills = []

	for tech in technologies:
		techs[tech] = 0


	for participant in participants:
		participant_row = participants_dataframe.loc[participants_dataframe['id'] == participant]
		try:
			if participant_row['skills'].isnull().bool() == False:
				participant_technologies = participant_row['skills'].tolist()[0].split('#')  # From dataframe to series to list -> taking first element and splitting it by #.
				for tech in techs:
					if tech in participant_technologies:
						techs[tech] += 1
			else:
				no_skills.append(participant)
		except Exception as e:
			if not participant_row['skills'].empty:
				participant_technologies = participant_row['skills'].tolist()[0].split('#')  # From dataframe to series to list -> taking first element and splitting it by #.
				for tech in techs:
					if tech in participant_technologies:
						techs[tech] += 1
			else:
				no_skills.append(participant)

	participantsAmount = abs(participantsAmount - len(no_skills))

	if participantsAmount > 1:
		for x in techs.values():
			if (x / participantsAmount) >= 0.75:
				skillDiversity += technologyWeight
			else:
				skillDiversity += (technologyWeight * x) / participantsAmount

		return skillDiversity
	elif participantsAmount == 1:
		return 1
	else:
		return 0


# Team's skill diversity
def teamSkillDiversity(participants):
	participants = participants.split('#')
	participantsAmount = len(participants)
	techs = {}
	skillDiversity = 0
	participants_with_no_skills = 0
	technologies = []

	for participant in participants:
		participant_row = participants_dataframe.loc[participants_dataframe['id'] == participant]
		try:
			if participant_row['skills'].isnull().bool() == False:
				participant_technologies = participant_row['skills'].tolist()[0].split('#')  # From dataframe to series to list ->
				# taking first element and splitting it by #.
				for tech in participant_technologies:
					technologies.append(tech)

		except Exception as e:
			if not participant_row['skills'].empty:
				participant_technologies = participant_row['skills'].tolist()[0].split('#')  # From dataframe to series to list ->
				# taking first element and splitting it by #.
				for tech in participant_technologies:
					technologies.append(tech)


	technologies = unique(technologies)

	for tech in technologies:
		techs[tech] = 0

	for participant in participants:
		participant_row = participants_dataframe.loc[participants_dataframe['id'] == participant]
		try:
			if participant_row['skills'].isnull().bool() == False:
				participant_technologies = participant_row['skills'].tolist()[0].split('#')  # From dataframe to series to list ->
				# taking first element and splitting it by #.
				for tech in techs:
					if tech in participant_technologies:
						techs[tech] += 1
			else:
				participants_with_no_skills += 1

		except Exception as e:
			if not participant_row['skills'].empty:
				participant_technologies = participant_row['skills'].tolist()[0].split('#')

				for tech in techs:
					if tech in participant_technologies:
						techs[tech] += 1
			else:
				participants_with_no_skills += 1


	technologyWeight = 1 / len(technologies)
	participantsAmount = abs(participantsAmount - participants_with_no_skills)

	if participantsAmount > 1:
		for x in techs.values():
			if (x / participantsAmount) >= 0.75:
				skillDiversity += technologyWeight
			else:
				skillDiversity += (technologyWeight * x) / participantsAmount
		return skillDiversity
	elif participantsAmount == 1:
		return 1
	else:
		return 0


def isHackathonAfter(observableDate, otherHackathonDate):
	observableDateParts = observableDate.split("-")
	otherHackathonDateParts = otherHackathonDate.split("-")

	observableDate = datetime.date(int(observableDateParts[0]), int(observableDateParts[1]), int(observableDateParts[2]))
	otherHackathonDate = datetime.date(int(otherHackathonDateParts[0]), int(otherHackathonDateParts[1]), int(otherHackathonDateParts[2]))

	return observableDate > otherHackathonDate


def teamFamiliarity(participants, hackathon_end_date):
	participants_separated = participants.split("#")
	participant_combinations = (list(combinations(participants_separated, 2)))

	familiarity = {}

	for (p1, p2) in participant_combinations:
		# jack.*james|james.*jack
		participantString = str(p1) + ".*" + str(p2) + "|" + str(p2) + ".*" + str(p1)
		hackathons = wholeDataSet.loc[wholeDataSet['participant-ids'].str.contains(participantString)]

		participantString = p1 + "#" + p2
		familiarity[participantString] = 0

		for hackathon in hackathons.values:
			end_date = hackathon[11]

			if isHackathonAfter(hackathon_end_date, end_date):
				familiarity[participantString] += 1


	#participantWeight = 1 / len(participants_separated)
	#amountOfParticipants = len(participants_separated)
	participantWeight = 1 / len(participant_combinations)
	amountOfParticipants = len(participant_combinations)


	teamFamiliarityCalculation = 0

	for (key, value) in familiarity.items():
		teamFamiliarityCalculation += ((participantWeight * value) / amountOfParticipants)

	if teamFamiliarityCalculation > 1.0:
		return 2.0
	else:
		return teamFamiliarityCalculation


def getHackathonSizeCategory(numberofHackathons):

	if numberofHackathons > 3 and numberofHackathons < 16:
		return 1
	elif numberofHackathons > 15 and numberofHackathons < 51:
		return 2
	elif numberofHackathons > 50 and numberofHackathons < 101:
		return 3
	else:
		return 4



with open('githubProjectsTogetherCleaned.csv', encoding="utf8") as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=';')
	line_count = 0

	for row in csv_reader:
		if line_count > 0:
			work_after = str(row[19])
			github_url = str(row[14]).strip()
			technologies = str(row[2])
			participants = str(row[4])
			hackathon_end_date = str(row[11]).strip()
			hackathon_id = str(row[8])
			winner = str(row[15])
			devpost_id = str(row[0])
			hackathon_end_date = str(row[11]).strip()
			numberOfParticipants = str(row[5])
			likes = str(row[6])
			comments = str(row[7])
			hackathon_is_located = str(row[12])


			print("ROW NR: " + str(line_count) + " " + devpost_id)
			if work_after == "1":
				try:
					commits_rows = commits_dataframe.loc[commits_dataframe['commit_id'] == devpost_id]
					committers = []
					commit_dates = []
					for commit_row in commits_rows.values:
						committer = commit_row[4]
						committers.append(committer)
						commit_dates.append(commit_row[3])


					# Unique commit days
					commit_dates_unique = unique(list(set(commit_dates)))

					# Unique commiters
					committers = unique(list(set(committers)))

					# Contributors amount
					contributors = len(committers)

					# Outside help
					outsideHelp = 0

					if contributors > int(numberOfParticipants):
						outsideHelp = 1

					# Commits amount
					commits_amount = len(commits_rows)

					if commits_amount == 0:
						work_more_after += 1
						days_after_hackathon = 0
						commits_slash_days = 0
						commits_slash_all_days = 0
					else:
						# Last day the project was active
						days_after_hackathon = commits_rows.values[-1][2]
						# Commits/days active division by zero problem.
						commits_slash_days = commits_amount / days_after_hackathon
						# Commits / 270 days -> commits frequency
						commits_slash_all_days = commits_amount / 270

					# Skills diversity
					skillPercentage = roundup(skillDiversity(participants, technologies), 1)

					# Team skill diversity
					teamSkillPercentage = roundup(teamSkillDiversity(participants), 1)

					# Project dormancy
					commits_frequency_dormant = isProjectDormantInAverage(commits_rows)

					# Project winning weight
					hackathons = wholeDataSet.loc[wholeDataSet['hackathon-id'] == hackathon_id]

					if winner == "1":
						winner_weight = roundup(calculateWinnerWeightPercentage(hackathons), 1)
					else:
						winner_weight = 0


					# Convert hackathon location to numeric
					hackathonLoc = 0
					if hackathon_is_located == "True":
						hackathonLoc = 1

					# Number of teams in the hackathon
					numberOfProjectsInHackathon = len(hackathons)

					#Hackathon size category
					hackathonSizeCategory = getHackathonSizeCategory(numberOfProjectsInHackathon)

					# Project's team working together weight
					worked_together_weight = roundup(teamFamiliarity(participants, hackathon_end_date), 1)


					row = row + [str(skillPercentage), str(teamSkillPercentage),
								 str(numberOfProjectsInHackathon), str(hackathonSizeCategory), str(commits_amount),
								 str(days_after_hackathon), str(contributors), str(outsideHelp), commits_slash_days,
								 str(len(commit_dates_unique)), str(commits_frequency_dormant),
								 str(commits_slash_all_days), str(worked_together_weight), str(winner_weight), str(hackathonLoc)]

					projects.append(row)
				except Exception as e:
					print("error")
					print(e)
					work_more_after += 1
					print(row)
			else:

				# Skills diversity
				skillPercentage = roundup(skillDiversity(participants, technologies), 1)

				# Team skill diversity
				teamSkillPercentage = roundup(teamSkillDiversity(participants), 1)

				# Project winning weight
				hackathons = wholeDataSet.loc[wholeDataSet['hackathon-id'] == hackathon_id]

				if winner == "1":
					winner_weight = roundup(calculateWinnerWeightPercentage(hackathons), 1)
				else:
					winner_weight = 0

				# Number of teams in the hackathon
				numberOfProjectsInHackathon = len(hackathons)

				# Convert hackathon location to numeric
				hackathonLoc = 0
				if hackathon_is_located == "True":
					hackathonLoc = 1

				# Hackathon size category
				hackathonSizeCategory = getHackathonSizeCategory(numberOfProjectsInHackathon)

				# Project's team working together weight
				worked_together_weight = roundup(teamFamiliarity(participants, hackathon_end_date), 1)


				projects.append(row + [str(skillPercentage), str(teamSkillPercentage), str(numberOfProjectsInHackathon), str(hackathonSizeCategory),
									   "0", "0", "0", "0", "0", "0", "0", "0", str(worked_together_weight), str(winner_weight), str(hackathonLoc)])


		else:
			project_rows = row + ["skillsCovered", "teamSkillsDiversity", "projectsInHackathon", "hackathonSizeCategory", "commits",
								  "days_after_hackathon_for_last_commit", "contributors_amount", "outside_help", "commits_slash_last_active_day",
								  "days_which_has_commits", "commits_frequency_dormant",
								  "commits_slash_all_days", "worked_together_weight", "winner_weight", "hackathon_location"]

		#if (line_count == 100):
		#	break
		line_count += 1


	projectsFile = pd.DataFrame(projects, columns=project_rows)
	projectsFile.to_csv('githubProjects_with_extra_info.csv', index=False, sep=';')



print("WORK MORE AFTER: " + str(work_more_after))
