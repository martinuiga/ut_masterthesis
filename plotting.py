import pandas as pd
import numpy as np
import matplotlib.pyplot as plt   #Data visualisation libraries
import csv
import datetime



projs = pd.read_csv("githubProjects_with_extra_info.csv", sep=";")

print(projs.loc[:,"days_which_has_commits"].median())

### Graph: Y axis: commiters amount, X axis: Days after hackathon on last commit ###

plt.scatter(projs.commits, projs.contributors_amount)
plt.xlim(1, 2000)
plt.ylim(1, 30)
plt.ylabel("Contributors amount")
plt.xlabel("Commits amount")
plt.title("Y axis: Commiters amount, X axis: Commits amount")
#plt.show()



### Graph: Y axis: commiters amount, X axis: Days after hackathon on last commit ###

plt.scatter(projs["number-of-participants"], projs.contributors_amount)
plt.xlim(1, 5)
plt.ylim(1, 100)
plt.ylabel("Contributors amount")
plt.xlabel("Commits amount")
plt.title("Y axis: Commiters amount, X axis: Commits amount")
#plt.show()




### Graph: Y axis: commits amoun (in 270 days), X axis: Days active after hackathon ###

plt.scatter(projs.days_after_hackathon_for_last_commit, projs.commits)

median = projs.loc[:,"days_after_hackathon_for_last_commit"].median()
plt.axvline(median, color='k', linestyle='dashed', linewidth=1)

_, max_ = plt.ylim()
plt.text(median + median/10,
         max_ - max_/10,
         'Median: {:.2f}'.format(median))

median = projs.loc[:,"commits"].median()
plt.axhline(median, color='k', linestyle='dashed', linewidth=1)

_, max_ = plt.xlim()
plt.text(median + median/10,
         max_ - max_/10,
         'Median: {:.2f}'.format(median))

plt.ylabel("Commits amount (in 270 days)")
plt.xlabel("Days active")
plt.title("Y axis: commits amount, X axis: days active")
#plt.show()




participants = pd.read_csv("participants.csv", sep=";")

pd.crosstab(participants["number-of-hackathons"], participants.likes).plot(kind='bar')
plt.title('Purchase Frequency for Job Title')
plt.xlabel('Job')
plt.ylabel('Frequency of Purchase')
plt.savefig('purchase_fre_job')
plt.show()
