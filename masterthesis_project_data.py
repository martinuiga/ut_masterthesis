import _mysql as db
import pandas as pd
import csv
import datetime


db.connect()

db = db.connect(host="127.0.0.1",user="ght",
                  db="ghtorrent")


### is there activity in the github projects afterwards ###
# 1. Import CSV file of hackathons
# 2. For every hackathon query the database with ID [0] from hackathons csv file.
# 3. Take hackathon endDate from csv file [11].
# 4. Compare IF latest commit is after hackathon end date.

WORK_AFTER_HACKATHON_GITHUB = 0 # WORK AFTER HACKATHON WITH GITHUB URL
NO_WORK_AFTER_HACKATHON_GITHUB = 0 # NO WORK AFTER HACKATHON WITH GITHUB URL
NO_COMMITS_FOUND_WITH_GITHUB = 0 # NO COMMITS FOUND WITH GITHUB URL (url is bad probably)
GITHUB_RANDOM_COUNTER = 0 # all other cases

WORK_AFTER_HACKATHON_PROJECTID = 0 # WORK AFTER HACKATHON WITHOUT GITHUB URL
NO_WORK_AFTER_HACKATHON_PROJECTID = 0 # NO WORK AFTER HACKATHON WITHOUT GITHUB URL
NO_COMMITS_FOUND_WITH_PROJECTID = 0
GITHUB_IO_URL = 0

EXCEPTIONS = 0


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
						else:
							NO_WORK_AFTER_HACKATHON_GITHUB += 1
					elif userName:
						print("NO COMMIT FOR USERNAME: " + userName)
						NO_COMMITS_FOUND_WITH_GITHUB += 1
					else:
						GITHUB_RANDOM_COUNTER += 1

				else:
					project_name = str(row[0]).strip()
					query = 'select c.created_at from projects s, commits c where s.name = "' + project_name.strip() + '" and s.id = c.project_id limit 1000'
					print("PROJECT NAME: " + str(project_name) + " WITH END DATE: " + str(hackathon_end_date) + " ROW NR: " + str(line_count))


					db.query(query)
					r = db.store_result()
					commits = r.fetch_row(maxrows=0)

					if len(commits) > 0:
						if isAfterHackathon(commits, hackathon_end_date):
							WORK_AFTER_HACKATHON_PROJECTID += 1
						else:
							NO_WORK_AFTER_HACKATHON_PROJECTID += 1
					elif github_url and "github.io" in github_url:
						GITHUB_IO_URL += 1
					else:
						print("NO COMMITS FOUND FOR PROJECT: " + str(project_name))
						NO_COMMITS_FOUND_WITH_PROJECTID += 1

			except Exception as e:
				print(e)
				print("Something went wrong with row: " + str(row))
				EXCEPTIONS += 1


		#if (line_count == 10):
		#	break
		line_count += 1



print("WORK AFTER GITHUB URL: " + str(WORK_AFTER_HACKATHON_GITHUB))
print("WORK AFTER PROJECT_ID: " + str(WORK_AFTER_HACKATHON_PROJECTID))

print("NO WORK AFTER GITHUB URL: " + str(NO_WORK_AFTER_HACKATHON_GITHUB))
print("NO WORK AFTER PROJECT_ID: " + str(NO_WORK_AFTER_HACKATHON_PROJECTID))

print("NO COMMITS FOUND GITHUB URL: " + str(NO_COMMITS_FOUND_WITH_GITHUB))
print("NO COMMITS FOUND PROJECT_ID: " + str(NO_COMMITS_FOUND_WITH_PROJECTID))

print("GITHUB RANDOM ROWS: " + str(GITHUB_RANDOM_COUNTER))
print("GITHUB IO ROWS: " + str(GITHUB_IO_URL))
print("TOTAL LINES: " + str(line_count))


data = []
cols = [WORK_AFTER_HACKATHON_GITHUB, WORK_AFTER_HACKATHON_PROJECTID, NO_WORK_AFTER_HACKATHON_GITHUB, NO_WORK_AFTER_HACKATHON_PROJECTID,
		NO_COMMITS_FOUND_WITH_GITHUB, NO_COMMITS_FOUND_WITH_PROJECTID, EXCEPTIONS]
fullData = pd.DataFrame(data, columns=cols)
fullData.to_csv('whole_data.csv', index=False, sep=';')
