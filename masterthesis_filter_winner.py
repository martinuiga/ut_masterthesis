import _mysql as db
import csv
import datetime
from datetime import date


db.connect()

db = db.connect(host="127.0.0.1",user="ght",
                  db="ghtorrent")


### Projects with activity afterwards splitted: winners/not winners ###
# 1. Import CSV file of hackathons
# 2. For every hackathon query the database with ID [0] from hackathons csv file.
# 3. Take hackathon endDate from csv file [11].
# 4. Compare IF latest commit is after hackathon end date.
# 5. See if it is winner or not.

WORK_AFTER_HACKATHON_GITHUB = 0 # WORK AFTER HACKATHON WITH GITHUB URL
NO_WORK_AFTER_HACKATHON_GITHUB = 0 # NO WORK AFTER HACKATHON WITH GITHUB URL
NO_COMMITS_FOUND_WITH_GITHUB = 0 # NO COMMITS FOUND WITH GITHUB URL (url is bad probably)
GITHUB_RANDOM_COUNTER = 0 # all other cases

WINNERS = 0
NOT_WINNERS = 0

WORK_AFTER_HACKATHON_PROJECTID = 0 # WORK AFTER HACKATHON WITHOUT GITHUB URL
NO_WORK_AFTER_HACKATHON_PROJECTID = 0 # NO WORK AFTER HACKATHON WITHOUT GITHUB URL
NO_COMMITS_FOUND_WITH_PROJECTID = 0
GITHUB_IO_URL = 0


def isAfterHackathon(commits, hackathonEndDate):

	latestCommit = commits[len(commits)-1][0].split(" ")[0]
	latestCommitParts = latestCommit.split("-")
	latestCommitDate = datetime.date(int(latestCommitParts[0]), int(latestCommitParts[1]), int(latestCommitParts[2]))

	hackathonEndDateParts = hackathonEndDate.split("-")
	hackathonEndDate = datetime.date(int(hackathonEndDateParts[0]), int(hackathonEndDateParts[1]), int(hackathonEndDateParts[2]))

	return latestCommitDate > hackathonEndDate

def projectNameFromGithubURL(url):
	github_url1 = url.replace("https://", "").replace("www.", "").replace("github.com/", "").replace("http://", "")
	github_url_parts = github_url1.split("/")
	return (github_url_parts[0], github_url_parts[1])


# take github url, then take the username, put github.com/username/username.github.io
def fixGithubIoLink(url):
	url = url.split("/")[2].replace(".github.io", "").strip()
	returnURL = "http://github.com/" + str(url) + "/" + str(url) + ".github.io"
	return returnURL

with open('projects-incl-hackathon.csv', encoding="utf8") as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=';')
	line_count = 0
	for row in csv_reader:
		if line_count > 0:
			try:
				project_name = ""
				hackathon_end_date = str(row[11]).strip()
				github_url = str(row[14]).strip()
				winner = int(row[15])
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
							print("FOUND USER: " + str(userName) + " " + "PROJECT NAME: " + str(project_name) + " ROW NR: " + str(line_count))

					query = 'select c.created_at from projects p, commits c where p.id = "' + project_id + '" and c.project_id = p.id;'

					db.query(query)
					r = db.store_result()
					commits = r.fetch_row(maxrows=0)

					if len(commits) > 0:
						if isAfterHackathon(commits, hackathon_end_date):
							WORK_AFTER_HACKATHON_GITHUB += 1
							if winner == 1:
								WINNERS += 1
							else:
								NOT_WINNERS += 1
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


		if (line_count == 20000):
			break
		line_count += 1



print("WORK AFTER GITHUB URL: " + str(WORK_AFTER_HACKATHON_GITHUB))

print("NO WORK AFTER GITHUB URL: " + str(NO_WORK_AFTER_HACKATHON_GITHUB))

print("NO COMMITS FOUND GITHUB URL: " + str(NO_COMMITS_FOUND_WITH_GITHUB))
print("GITHUB IO ROWS: " + str(GITHUB_IO_URL))
print("TOTAL LINES: " + str(line_count))
print(" ")

print("WINNER: " + str(WINNERS))
print("NO WINNERS: " + str(NOT_WINNERS))
