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


data = pd.read_csv('githubProjects_with_extra_info_part.csv', header=0, sep=";")

data = data.drop(columns=['id', 'timestamp', 'technologies', 'participant-ids',
		   'hackathon-id', 'hackathon-prize-money', 'hackathon-end-date',
		   'location', 'github-url', 'github_owner_name', 'github_project_id', 'github_forked_from', 'commits_amount_dormant'])


onlyWorkAfter = data.drop(columns=['work_after', 'commits_slash_all_days', 'commits', 'days_which_has_commits',
								   'commits_slash_last_active_day', 'days_after_hackathon_for_last_commit'])


## TURN AROUND DORMANCY VALUE
onlyWorkAfter.commits_frequency_dormant[onlyWorkAfter.commits_frequency_dormant == 1] = 2
onlyWorkAfter.commits_frequency_dormant[onlyWorkAfter.commits_frequency_dormant == 0] = 1
onlyWorkAfter.commits_frequency_dormant[onlyWorkAfter.commits_frequency_dormant == 2] = 0

print(list(onlyWorkAfter.columns))
print(onlyWorkAfter['commits_frequency_dormant'].value_counts())


##### WORK AFTER DATA #####

count_no_sub = len(onlyWorkAfter[onlyWorkAfter['commits_frequency_dormant']==0])
count_sub = len(onlyWorkAfter[onlyWorkAfter['commits_frequency_dormant']==1])
pct_of_no_sub = count_no_sub/(count_no_sub+count_sub)
print("percentage of no work is", pct_of_no_sub*100)
pct_of_sub = count_sub/(count_no_sub+count_sub)
print("percentage of work is", pct_of_sub*100)


### WINNER

table=pd.crosstab(onlyWorkAfter.winner,onlyWorkAfter.commits_frequency_dormant)
table.div(table.sum(1).astype(float), axis=0).plot(kind='bar', stacked=True)
plt.title('Winner proportion between non- and dormant projects')
plt.xlabel('Winner')
plt.ylabel('Proportion')



## HACKATHON PRIZES
table=pd.crosstab(onlyWorkAfter['hackathon-number-of-prizes'],onlyWorkAfter.commits_frequency_dormant)
table.div(table.sum(1).astype(float), axis=0).plot(kind='bar', stacked=True)
plt.title('Stacked Bar Chart of Number of prizes vs commits_frequency_dormant')

plt.xlabel('Number of prizes')
plt.ylabel('Proportion')


## HACKATHON SKILL COVERAGE

table=pd.crosstab(onlyWorkAfter.skillsCovered,onlyWorkAfter.commits_frequency_dormant)
table.div(table.sum(1).astype(float), axis=0).plot(kind='bar', stacked=True)
plt.title('Stacked Bar Chart of skills covered vs commits_frequency_dormant')
plt.xlabel('Skills covered %')
plt.ylabel('Proportion of Customers')



X = onlyWorkAfter.loc[:, onlyWorkAfter.columns != 'commits_frequency_dormant']
y = onlyWorkAfter.loc[:, onlyWorkAfter.columns == 'commits_frequency_dormant']


from imblearn.over_sampling import SMOTE
os = SMOTE(random_state=0)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)

columns = X_train.columns
os_data_X,os_data_y=os.fit_sample(X_train, y_train)

os_data_X = pd.DataFrame(data=os_data_X,columns=columns )
os_data_y= pd.DataFrame(data=os_data_y,columns=['commits_frequency_dormant'])

# we can Check the numbers of our data
print("length of oversampled data is ",len(os_data_X))
print("Number of no subscription in oversampled data",len(os_data_y[os_data_y['commits_frequency_dormant']==0]))
print("Number of subscription",len(os_data_y[os_data_y['commits_frequency_dormant']==1]))
print("Proportion of work after hackathon in oversampled data is ",len(os_data_y[os_data_y['commits_frequency_dormant']==1])/len(os_data_X))
print("Proportion of no work after hackathon in oversampled data is ",len(os_data_y[os_data_y['commits_frequency_dormant']==0])/len(os_data_X))


data_final_vars = onlyWorkAfter.columns.values.tolist()
print(data_final_vars)

from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression

logreg = LogisticRegression()

rfe = RFE(logreg, 20)
rfe = rfe.fit(os_data_X, os_data_y.values.ravel())

print(rfe.support_)
print(rfe.ranking_)



cols = ['winner', 'number-of-technologies', 'number-of-participants', 'likes', 'comments',
		'hackathon-number-of-prizes', 'hackathon-is-colocated', 'skillsCovered', 'worked_together_before']



X = os_data_X[cols]
y = os_data_y['commits_frequency_dormant']


import statsmodels.api as sm

logit_model = sm.Logit(y,X)
result = logit_model.fit()

print(result.summary2())



# CHOOSING THE REMAINING COLS
cols = ['worked_together_before', 'skillsCovered']

from sklearn.linear_model import LogisticRegression

X = os_data_X[cols]
y = os_data_y['commits_frequency_dormant']


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)

logreg = LogisticRegression()
logreg.fit(X_train, y_train)

y_pred = logreg.predict(X_test)
print('Accuracy of logistic regression classifier on test set: {:.2f}'.format(logreg.score(X_test, y_test)))



from sklearn.metrics import confusion_matrix
confusion_matrix = confusion_matrix(y_test, y_pred)
print(confusion_matrix)

from sklearn.metrics import classification_report
print(classification_report(y_test, y_pred))



from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
logit_roc_auc = roc_auc_score(y_test, logreg.predict(X_test))
fpr, tpr, thresholds = roc_curve(y_test, logreg.predict_proba(X_test)[:,1])
plt.figure()
plt.plot(fpr, tpr, label='Logistic Regression (area = %0.2f)' % logit_roc_auc)
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic')
plt.legend(loc="lower right")
plt.savefig('Log_ROC')
plt.show()
