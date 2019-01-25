import pandas as pd
import csv
import datetime
import base64
import json
import time
import httplib2

participants_dataframe = pd.read_csv("participants.csv", sep=";")

headers = {"Authorization": b'Basic ' +  base64.urlsafe_b64encode(b'martinuiga:2b82357890acbf16897ea8a576722ab5d0ea62f7')}

h = httplib2.Http(".cache")


WORK_AFTER_HACKATHON_GITHUB = 0 # WORK AFTER HACKATHON WITH GITHUB URL
NO_WORK_AFTER_HACKATHON_GITHUB = 0 # NO WORK AFTER HACKATHON WITH GITHUB URL
EXCEPTIONS = 0



#######################
###                 ###
###      Files      ###
###                 ###
#######################



## COMMITS FILE

commits_cols = ['commit_id', 'sha', 'day', 'timestamp', 'ght_author_id', 'ght_committer_id', 'github_comment_ids']

commit_rows = []

## PULL REQUESTS FILE

pr_cols = ['project_to_pr_id', 'ght_pr_id', 'timestamp', 'actor', 'sha']

pr_rows = []


## PARTICIPANT COVERAGE FILE

participant_cols = ['project_to_participant_id', 'coverage', 'participant_name']

participant_rows = []



failed_row_cols = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']

failed_rows = []
status = ""


####

project_csv_cols = []
project_csv_rows = []

####

#######################
###                 ###
###      Utils      ###
###                 ###
#######################

def common_elements(list1, list2):
	return list(set(list1) & set(list2))

def projectNameFromGithubURL(url):
	if (url[-4:] == '.git'):
		url = url[:-4]
	github_url = url.replace("https://", "").replace("www.", "").replace("github.com/", "").replace("http://", "")
	github_url_parts = github_url.split("/")
	return (github_url_parts[0], github_url_parts[1])


def toAPIGithubUrl(userName, project_name):
	return "https://api.github.com/repos/" + str(userName) + "/" + str(project_name)


def fixGithubIoLink(url):
	url = url.split("/")[2].replace(".github.io", "").strip()
	returnURL = "http://github.com/" + str(url) + "/" + str(url) + ".github.io"
	return returnURL

def isAfterHackathon(commits, hackathonEndDate):

	latestCommit = commits[0]['commit']['committer']['date'].split("T")[0]
	latestCommitParts = latestCommit.split("-")
	latestCommitDate = datetime.date(int(latestCommitParts[0]), int(latestCommitParts[1]), int(latestCommitParts[2]))

	hackathonEndDateParts = hackathonEndDate.split("-")
	hackathonEndDate = datetime.date(int(hackathonEndDateParts[0]), int(hackathonEndDateParts[1]), int(hackathonEndDateParts[2]))

	return latestCommitDate > hackathonEndDate


def commitsPerDays(commitsList, hackathonendDate, devPostId):

	hackathonEndDateParts = hackathonendDate.split("-")
	hackathonEndDate = datetime.date(int(hackathonEndDateParts[0]), int(hackathonEndDateParts[1]), int(hackathonEndDateParts[2]))

	parsedCommits = []

	for commit in commitsList:
		commitParts = commit['commit']['committer']['date'].split("T")[0].split("-")
		sha = commit['sha']
		author_id = commit['commit']['author']['name']
		commiter_id = commit['commit']['committer']['name']
		comments_url = commit['comments_url']
		originalDate = commit['commit']['committer']['date']

		formatted_date = datetime.date(int(commitParts[0]), int(commitParts[1]), int(commitParts[2]))

		parsedCommits.append([formatted_date, sha, author_id, commiter_id, comments_url, originalDate])

	for i in range (1, 271):
		hackathonEndDate += datetime.timedelta(days=1)
		commit_id = str(devPostId)

		for parsedCommit in parsedCommits:
			commentIds = ""
			if hackathonEndDate == parsedCommit[0]:


				### GET COMMENTS FOR THIS COMMIT ###
				r, content = h.request(parsedCommit[4], "GET", headers=headers)
				data = json.loads(content.decode("utf-8"))

				for commentId in data:
					print("IN COMMENTS")
					commentIds += str(commentId['id']) + "#"

				commit_rows.append([str(commit_id), parsedCommit[1], i, parsedCommit[5], parsedCommit[2], parsedCommit[3], commentIds])




def pullRequestsPerProject(devpostId, pulls_url):
	pulls_url = pulls_url.replace("{/number}", "")
	r, content = h.request(pulls_url, "GET", headers=headers)
	data = json.loads(content.decode("utf-8"))
	pr_id = str(devpostId)

	for pullrequest in data:
		actor = pullrequest['user']['login']
		timestamp = pullrequest['created_at']
		commits_url = pullrequest['commits_url']

		r, content = h.request(commits_url, "GET", headers=headers)
		pr_commits = json.loads(content.decode("utf-8"))
		for pr_commit in pr_commits:
			sha = pr_commit['sha']
			pr_rows.append([pr_id, pullrequest['id'], timestamp, actor, sha])

def projectTechnologiesCovered(participants, devpost_id, technologies):

	participants = participants.split('#')
	project_technologies = technologies.split('#')

	for participant in participants:
		participant_row = participants_dataframe.loc[participants_dataframe['id'] == participant]
		if (participant_row['skills'].isnull().bool()):
			print("NONE")
			participant_rows.append([str(devpost_id), None])
		else:
			participant_technologies = participant_row['skills'].tolist()[0].split('#')  # From dataframe to series to list -> taking first element and splitting it by #.

			number_of_common_elements = len(common_elements(project_technologies, participant_technologies))
			percentage = (number_of_common_elements * 100) / len(project_technologies)

			participant_rows.append([str(devpost_id), percentage, participant])




#######################
###                 ###
###      MAIN       ###
###                 ###
#######################

with open('projects-incl-hackathon-filtered-no-url.csv', encoding="utf8") as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=';')
	line_count = 0
	githubProjects = 0

	for row in csv_reader:
		if line_count > 0:
			try:
				project_name = ""
				userName = ''
				hackathon_end_date = str(row[11]).strip()
				github_url = str(row[14]).strip()
				devpost_id = str(row[0])
				project_technologies = str(row[2])
				project_participants = str(row[4])

				print("ROW: " + str(line_count))

				userName = project_participants.split("#")[0]

				github_api_url = toAPIGithubUrl(userName, devpost_id)

				r, content = h.request(github_api_url, "GET", headers=headers)
				data = json.loads(content.decode("utf-8"))
				status = str(r['status'])

				####
				ght_owner_id = data['owner']['id']
				forked_from = data['fork']
				proj_id = data['id']
				contributors_url = data['contributors_url']
				pr_url = data['pulls_url']
				###

				### GET ALL COMMITS ###

				r, content = h.request(github_api_url + "/commits?per_page=100", "GET", headers=headers)
				status = str(r['status'])
				data = json.loads(content.decode("utf-8"))

				commitsList = []
				commitsList += data

				if 'link' in r:
					while 'next' in r['link']:
						r, content = h.request(str(r['link'].split(">")[0].replace("<", "")), "GET",
											   headers=headers)
						data = json.loads(content.decode("utf-8"))
						commitsList += data
				#######################

				if (isAfterHackathon(commitsList, hackathon_end_date)):
					commitsPerDays(commitsList, hackathon_end_date, devpost_id)
					pullRequestsPerProject(devpost_id, pr_url)
					projectTechnologiesCovered(project_participants, devpost_id, project_technologies)
					project_csv_rows.append(row + [userName, proj_id, forked_from, "1"])

					WORK_AFTER_HACKATHON_GITHUB += 1
				else:
					NO_WORK_AFTER_HACKATHON_GITHUB += 1



			except Exception as e:
				print("Exception")
				print(e)
				print(row)
				failed_rows.append(row)
				EXCEPTIONS += 1

		r, content = h.request("https://api.github.com/rate_limit", "GET", headers=headers)
		data = json.loads(content.decode("utf-8"))
		limit = data['rate']['remaining']

		if limit < 300:
			time.sleep(3900)

		#if line_count == 5:
		#	break

		line_count += 1



	project_csv_cols = ['id', 'timestamp', 'technologies', 'number-of-technologies',
						'participant-ids', 'number-of-participants', 'likes', 'comments',
						'hackathon-id', 'hackathon-prize-money', 'hackathon-number-of-prizes',
						'hackathon-end-date', 'hackathon-is-colocated', 'location', 'github-url', 'winner',
						'ght/github_owner_name', 'ght/github_project_id', 'ght/github_forked_from', 'work_after']


	projects = pd.DataFrame(project_csv_rows, columns=project_csv_cols)
	projects.to_csv('githubProjects_no-url.csv', index=False, sep=';')

	commitsDataFrame = pd.DataFrame(commit_rows, columns=commits_cols)
	commitsDataFrame.to_csv('githubCommits_no-url.csv', index=False, sep=';')

	prDataFrame = pd.DataFrame(pr_rows, columns=pr_cols)
	prDataFrame.to_csv('githubPullRequests_no-url.csv', index=False, sep=';')

	particpantsDf = pd.DataFrame(participant_rows, columns=participant_cols)
	particpantsDf.to_csv('githubWorkload_no-url.csv', index=False, sep=';')

	failedRows = pd.DataFrame(failed_rows, columns=failed_row_cols)
	failedRows.to_csv('githubFailedrows_no-url.csv', index=False, sep=';')

	print("WORK AFTER HACKATHONS FROM GITHUB: " + str(WORK_AFTER_HACKATHON_GITHUB))
	print("NO WORK AFTER HACKATHOS FROM GITHUB: " + str(NO_WORK_AFTER_HACKATHON_GITHUB))
	print("EXCEPTIONS: " + str(EXCEPTIONS))
