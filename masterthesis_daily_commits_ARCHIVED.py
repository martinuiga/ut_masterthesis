import _mysql as db
import pandas as pd
import csv
import datetime


db.connect()

db = db.connect(host="127.0.0.1",user="ght",
                  db="ghtorrent")


participants_dataframe = pd.read_csv("participants.csv", sep=";")



WORK_AFTER_HACKATHON_GITHUB = 0 # WORK AFTER HACKATHON WITH GITHUB URL
NO_WORK_AFTER_HACKATHON_GITHUB = 0 # NO WORK AFTER HACKATHON WITH GITHUB URL
NO_COMMITS_FOUND_WITH_GITHUB = 0 # NO COMMITS FOUND WITH GITHUB URL (url is bad probably)
GITHUB_RANDOM_COUNTER = 0 # all other cases
EXCEPTIONS = 0


### UTILS ###

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


## FAILED PROJCETS FILE

failed_row_cols = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']

failed_rows = []


## COMMITS FILE

commits_cols = ['commit_id', 'sha', 'day', 'timestamp', 'ght_author_id', 'ght_committer_id', 'github_comment_ids']

commit_rows = []


## PULL REQUESTS FILE

pr_cols = ['project_to_pr_id', 'ght_pr_id', 'timestamp', 'actor', 'sha']

pr_rows = []


## PARTICIPANT COVERAGE FILE

participant_cols = ['project_to_participant_id', 'coverage', 'participant_name']

participant_rows = []


####

project_csv_cols = []
project_csv_rows = []

####



def commitsPerDays(commitsList, hackathonendDate, devPostId):
	hackathonEndDateParts = hackathonendDate.split("-")
	hackathonEndDate = datetime.date(int(hackathonEndDateParts[0]), int(hackathonEndDateParts[1]), int(hackathonEndDateParts[2]))

	parsedCommits = []
	for commit in commitsList:
		commitParts = commit[0].split(" ")[0].split("-")

		fullDate = datetime.date(int(commitParts[0]), int(commitParts[1]),
										 int(commitParts[2]))
		originalDate = commit[0]

		parsedCommits.append([fullDate, commit[1], commit[2], commit[3], commit[5], originalDate])


	for i in range (1, 271):
		hackathonEndDate += datetime.timedelta(days=1)
		commit_id = str(devPostId)

		for parsedCommit in parsedCommits:
			commentIds = ""
			if hackathonEndDate == parsedCommit[0]:
				authorID = parsedCommit[2]
				committerID = parsedCommit[3]

				db.query('select cc.comment_id from commit_comments cc where cc.commit_id = ' + parsedCommit[4] + ';')
				r = db.store_result()
				comment_ids = r.fetch_row(maxrows=0)

				db.query('select u.login from users u where u.id = ' + authorID + ';')
				r = db.store_result()
				authorLogin = r.fetch_row(maxrows=0)[0][0].decode("utf-8")

				db.query('select u.login from users u where u.id = ' + committerID + ';')
				r = db.store_result()
				committerLogin = r.fetch_row(maxrows=0)[0][0].decode("utf-8")

				for commentId in comment_ids:
					commentIds += str(commentId[0]) + "&"

				commit_rows.append([str(commit_id), parsedCommit[1].decode("utf-8"), i, parsedCommit[5], authorLogin, committerLogin, commentIds])



def pullRequestsPerProject(project_id, devpostId):

	db.query('select pr.id from pull_requests pr where pr.base_repo_id = ' + project_id + ';')
	r = db.store_result()
	pull_requests = r.fetch_row(maxrows=0)

	for pullrequest in pull_requests:
		pull_request_id = pullrequest[0]

		db.query("select pr.id, ph.created_at, ph.actor_id, pc.commit_id, c.sha " \
		"from pull_requests pr, pull_request_history ph, pull_request_commits pc, commits c " \
		"where pr.id = " + pull_request_id +  " and ph.pull_request_id = pr.id and pc.pull_request_id = pr.id and c.id = pc.commit_id;")

		r = db.store_result()
		print("Pull request id found")
		pr_stuff = r.fetch_row(maxrows=0)


		for pr in pr_stuff:
			db.query('select u.login from users u where u.id = ' + pr[2] + ';')
			r = db.store_result()
			authorLogin = r.fetch_row(maxrows=0)[0][0].decode("utf-8")
			pr_rows.append([devpostId, str(pullrequest[0]), pr[1], authorLogin, pr[4].decode("utf-8")])



def common_elements(list1, list2):
	return list(set(list1) & set(list2))

def projectTechnologiesCovered(participants, devpost_id, technologies):

	participants = participants.split('#')
	project_technologies = technologies.split('#')

	for participant in participants:
		participant_row = participants_dataframe.loc[participants_dataframe['id'] == participant]
		if (participant_row['skills'].isnull().bool()):
			print("NONE")
			participant_rows.append([devpost_id, None])
		else:
			participant_technologies = participant_row['skills'].tolist()[0].split('#')  # From dataframe to series to list -> taking first element and splitting it by #.

			number_of_common_elements = len(common_elements(project_technologies, participant_technologies))
			percentage = (number_of_common_elements * 100) / len(project_technologies)

			participant_rows.append([devpost_id, percentage, participant])



with open('projects-incl-hackathon.csv', encoding="utf8") as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=';')
	line_count = 0

	for i in range(0, 60004):
		next(csv_reader)
	for row in csv_reader:
		if line_count > 0:
			try:
				project_name = ""
				userName = ''
				hackathon_end_date = str(row[11]).strip()
				github_url = str(row[14]).strip()
				winner = str(row[15])
				devpost_id = str(row[0])
				project_technologies = str(row[2])
				project_participants = str(row[4])
				print("ROW: " + str(line_count))

				if github_url and ("github.com" in github_url or "github.io" in github_url):
					if "github.io" in github_url:
						github_url = fixGithubIoLink(github_url)

					(userName, project_name) = projectNameFromGithubURL(github_url)

					db.query('select u.id from users u where u.login = "' + userName.strip() + '";')
					r = db.store_result()
					userId = r.fetch_row(maxrows=0)
					user_id = userId[0][0] ## GHTORRENT USERS.ID

					query = 'select c.created_at, c.sha, c.author_id, c.committer_id, p.id, c.id, p.forked_from from commits c, projects p where p.owner_id = ' + \
							user_id + ' and p.name = "' + project_name.strip() + '" and c.project_id = p.id;'

					db.query(query)
					r = db.store_result()
					commits = r.fetch_row(maxrows=0)
					if len(commits) > 0:
						if isAfterHackathon(commits, hackathon_end_date):
							WORK_AFTER_HACKATHON_GITHUB += 1
							proj_id = str(commits[0][4])
							forked_from = str(commits[0][6])

							print(project_name + " " + str(userName) + str (proj_id))

							commitsPerDays(commits, hackathon_end_date, devpost_id)
							pullRequestsPerProject(proj_id, devpost_id)
							projectTechnologiesCovered(project_participants, devpost_id, project_technologies)

							project_csv_rows.append(row + [userName, proj_id, forked_from, "1"])
						else:
							project_csv_rows.append(row + [None, None, None, "0"])
							NO_WORK_AFTER_HACKATHON_GITHUB += 1

					elif userName:
						failed_rows.append(row)
						NO_COMMITS_FOUND_WITH_GITHUB += 1
					else:
						GITHUB_RANDOM_COUNTER += 1
						failed_rows.append(row)
				else:
					project_csv_rows.append(row + [None, None, None, "0"])

			except Exception as e:
				failed_rows.append(row)
				print(e)
				print("Something went wrong with row: " + str(row))
				EXCEPTIONS += 1

		else:
			project_csv_cols = row + ['ght/github_owner_id', 'ght/github_project_id', 'ght/github_forked_from', 'work_after']

		#if (line_count == 5):
		#	break
		line_count += 1






	projects = pd.DataFrame(project_csv_rows, columns=project_csv_cols)
	projects.to_csv('PROJECTS_5.csv', index=False, sep=';')

	failedRows = pd.DataFrame(failed_rows, columns=failed_row_cols)
	failedRows.to_csv('FAILEDROWS_5.csv', index=False, sep=';')

	commitsDataFrame = pd.DataFrame(commit_rows, columns=commits_cols)
	commitsDataFrame.to_csv('COMMITS_5.csv', index=False, sep=';')

	prDataFrame = pd.DataFrame(pr_rows, columns=pr_cols)
	prDataFrame.to_csv('PULL_REQ_5.csv', index=False, sep=';')

	particpantsDf = pd.DataFrame(participant_rows, columns=participant_cols)
	particpantsDf.to_csv('WORKLOAD_5.csv', index=False, sep=';')



	print("WORK AFTER HACKATHONS FROM GITHUB: " + str(WORK_AFTER_HACKATHON_GITHUB))
	print("NO WORK AFTER HACKATHOS FROM GITHUB: " + str(NO_WORK_AFTER_HACKATHON_GITHUB))
	print("NO COMMITS FOUND WITH GITHUB: " + str(NO_COMMITS_FOUND_WITH_GITHUB))
	print("EXCEPTIONS: " + str(EXCEPTIONS))
