import _mysql as db
import pandas as pd
import csv
import datetime
from datetime import date


db.connect()

db = db.connect(host="127.0.0.1",user="ght",
                  db="ghtorrent")


WORK_AFTER_HACKATHON_GITHUB = 0 # WORK AFTER HACKATHON WITH GITHUB URL
NO_WORK_AFTER_HACKATHON_GITHUB = 0 # NO WORK AFTER HACKATHON WITH GITHUB URL
NO_COMMITS_FOUND_WITH_GITHUB = 0 # NO COMMITS FOUND WITH GITHUB URL (url is bad probably)
GITHUB_RANDOM_COUNTER = 0 # all other cases
EXCEPTIONS = 0


def isAfterHackathon(commits, hackathonEndDate):

	latestCommit = commits[len(commits)-1][0].split(" ")[0]
	latestCommitParts = latestCommit.split("-")
	latestCommitDate = datetime.date(int(latestCommitParts[0]), int(latestCommitParts[1]), int(latestCommitParts[2]))

	hackathonEndDateParts = hackathonEndDate.split("-")
	hackathonEndDate = datetime.date(int(hackathonEndDateParts[0]), int(hackathonEndDateParts[1]), int(hackathonEndDateParts[2]))

	return latestCommitDate > hackathonEndDate

def projectNameFromGithubURL(url):
	github_url = url.replace("https://", "").replace("www.", "").replace("github.com/", "").replace("http://", "")
	github_url_parts = github_url.split("/")
	return (github_url_parts[0], github_url_parts[1])


def fixGithubIoLink(url):
	url = url.split("/")[2].replace(".github.io", "").strip()
	returnURL = "http://github.com/" + str(url) + "/" + str(url) + ".github.io"
	return returnURL


cols = ['project', 'project_id']

for i in range (1, 271):
	cols.append("day " + str(i))

projectAndCommitsPerDay = []

def commitsPerDays(projectName, p_id, commitsList, endDate):
	projectRow = [projectName, str(p_id)]

	hackathonEndDateParts = endDate.split("-")
	hackathonEndDate = datetime.date(int(hackathonEndDateParts[0]), int(hackathonEndDateParts[1]), int(hackathonEndDateParts[2]))

	parsedCommitDates = []
	for commit in commitsList:
		commitParts = commit[0].split(" ")[0].split("-")
		parsedCommitDates.append(datetime.date(int(commitParts[0]), int(commitParts[1]),
										 int(commitParts[2])))

	for i in range (1, 271):
		hackathonEndDate += datetime.timedelta(days=1)

		commitCounter = 0

		for parsedCommit in parsedCommitDates:
			if hackathonEndDate == parsedCommit:
				commitCounter += 1

		projectRow.append(commitCounter)

	return projectRow


with open('projects-incl-hackathon.csv', encoding="utf8") as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=';')
	line_count = 0
	for row in csv_reader:
		if line_count > 0:
			try:
				project_name = ""
				hackathon_end_date = str(row[11]).strip()
				github_url = str(row[14]).strip()
				userName = ''

				### IF GITHUB URL EXISTS AND USER FOUND ###

				if github_url and ("github.com" in github_url or "github.io" in github_url):
					if "github.io" in github_url:
						github_url = fixGithubIoLink(github_url)

					(userName, project_name) = projectNameFromGithubURL(github_url)
					db.query('select * from projects p where p.name = "' + project_name.strip() + '"')
					r = db.store_result()
					projects = r.fetch_row(maxrows=0)
					project_id = ''

					for project in projects:
						if userName in project[1].decode("utf-8"):
							project_id = str(project[0])
							print("FOUND USER: " + str(userName) + " " + "PROJECT NAME: " + str(
								project_name) + " ROW NR: " + str(line_count))

					query = 'select c.created_at from projects p, commits c where p.id = "' + project_id + '" and c.project_id = p.id;'

					db.query(query)
					r = db.store_result()
					commits = r.fetch_row(maxrows=0)

					if len(commits) > 0:
						if isAfterHackathon(commits, hackathon_end_date):
							WORK_AFTER_HACKATHON_GITHUB += 1
							projectAndCommitsPerDay.append(commitsPerDays(project_name, project_id, commits, hackathon_end_date))
						else:
							NO_WORK_AFTER_HACKATHON_GITHUB += 1
					elif userName:
						print("NO COMMIT FOR USERNAME: " + userName)
						NO_COMMITS_FOUND_WITH_GITHUB += 1
					else:
						GITHUB_RANDOM_COUNTER += 1

			except Exception as e:
				print(e)
				print("Something went wrong with row: " + str(row))
				EXCEPTIONS += 1


		if (line_count == 60000):
			break
		line_count += 1


	projects = pd.DataFrame(projectAndCommitsPerDay, columns=cols)
	projects.to_csv('dailyCommits.csv', index=False, sep=';')

	print(projects)
	print("WORK AFTER HACKATHONS FROM GITHUB: " + str(WORK_AFTER_HACKATHON_GITHUB))
	print("NO WORK AFTER HACKATHOS FROM GITHUB: " + str(NO_WORK_AFTER_HACKATHON_GITHUB))
	print("NO COMMITS FOUND WITH GITHUB: " + str(NO_COMMITS_FOUND_WITH_GITHUB))
	print("EXCEPTIONS: " + str(EXCEPTIONS))
