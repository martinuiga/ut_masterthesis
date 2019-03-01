# split X and y into training and testing sets
from sklearn.model_selection import train_test_split

###############################################

import pandas as pd
import numpy as np
from sklearn import preprocessing
import matplotlib.pyplot as plt
plt.rc("font", size=14)
from sklearn.linear_model import LogisticRegression
import seaborn as sns
sns.set(style="white")
sns.set(style="whitegrid", color_codes=True)


data = pd.read_csv('githubProjects_with_extra_info.csv', header=0, sep=";")

onlyWorkAfter = data.drop(columns=['id', 'timestamp', 'technologies', 'participant-ids',
		   'hackathon-id', 'hackathon-prize-money', 'hackathon-end-date',
		   'location', 'github-url', 'github_owner_name', 'github_project_id',
			'github_forked_from', 'work_after', 'commits_slash_all_days',
			'commits', 'days_which_has_commits',
			'commits_slash_last_active_day', 'days_after_hackathon_for_last_commit',
			'projectsInHackathon', 'number-of-technologies', 'winner', 'contributors_amount'])


## TURN AROUND DORMANCY VALUE
#onlyWorkAfter.commits_frequency_dormant[onlyWorkAfter.commits_frequency_dormant == 1] = 2
#onlyWorkAfter.commits_frequency_dormant[onlyWorkAfter.commits_frequency_dormant == 0] = 1
#onlyWorkAfter.commits_frequency_dormant[onlyWorkAfter.commits_frequency_dormant == 2] = 0

print(list(onlyWorkAfter.columns))
print(onlyWorkAfter['commits_frequency_dormant'].value_counts())


##### WORK AFTER DATA #####

count_no_sub = len(onlyWorkAfter[onlyWorkAfter['commits_frequency_dormant']==0])
count_sub = len(onlyWorkAfter[onlyWorkAfter['commits_frequency_dormant']==1])
pct_of_no_sub = count_no_sub/(count_no_sub+count_sub)
print("percentage of no work is", pct_of_no_sub*100)
pct_of_sub = count_sub/(count_no_sub+count_sub)
print("percentage of work is", pct_of_sub*100)




X = onlyWorkAfter.loc[:, onlyWorkAfter.columns != 'commits_frequency_dormant']
y = onlyWorkAfter.loc[:, onlyWorkAfter.columns == 'commits_frequency_dormant']


from imblearn.over_sampling import SMOTE
os = SMOTE(random_state=0)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

columns = X_train.columns
os_data_X, os_data_y = os.fit_sample(X_train, y_train)

os_data_X = pd.DataFrame(data=os_data_X, columns=columns)
os_data_y = pd.DataFrame(data=os_data_y, columns=['commits_frequency_dormant'])

# we can Check the numbers of our data
print("Length of oversampled data is ",len(os_data_X))
print("Number of dormant",len(os_data_y[os_data_y['commits_frequency_dormant']==0]))
print("Number of not dormant",len(os_data_y[os_data_y['commits_frequency_dormant']==1]))
print("Proportion of not dormant after hackathon in oversampled data is ",len(os_data_y[os_data_y['commits_frequency_dormant']==1])/len(os_data_X))
print("Proportion of dormant after hackathon in oversampled data is ",len(os_data_y[os_data_y['commits_frequency_dormant']==0])/len(os_data_X))


data_final_vars = onlyWorkAfter.columns.values.tolist()
print(data_final_vars)



from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression


logreg = LogisticRegression()

rfe = RFE(logreg, 20)
rfe = rfe.fit(os_data_X, os_data_y.values.ravel())

print(rfe.support_)
print(rfe.ranking_)



cols = ['number-of-participants', 'hackathon_location',
		'skillsCovered', 'teamSkillsDiversity',
		'worked_together_weight', 'winner_weight']



X = os_data_X[cols]
y = os_data_y['commits_frequency_dormant']


import statsmodels.api as sm

logit_model = sm.Logit(y,X)
result = logit_model.fit()

print(result.summary2())


# number.of.participants                   comments hackathon.is.colocatedTrue      hackathonSizeCategory               outside_help              winner_weight
# CHOOSING THE REMAINING COLS
cols = ['winner_weight', 'hackathon_location']
from sklearn.linear_model import LogisticRegression

X = os_data_X[cols]
y = os_data_y['commits_frequency_dormant']
X_test = X_test[cols]



logreg = LogisticRegression()
logreg.fit(X, y)

y_pred = logreg.predict(X_test)
print('Accuracy of logistic regression classifier on test set: {:.2f}'.format(logreg.score(X_test, y_test)))
