casualProjectsBig = read.csv("C:\\Users\\Karl-Martin\\Dropbox\\masterthesis\\githubProjects_with_extra_info.csv", sep=';', na.strings=c(""))


library(survival)
library(survminer)
projects_filtered <- subset(casualProjectsBig, select=c(6,21,22,24,26,31,33,34, 35))

projects_filtered$commits_frequency_dormant[projects_filtered$commits_frequency_dormant == 1] <- 2
projects_filtered$commits_frequency_dormant[projects_filtered$commits_frequency_dormant == 0] <- 1
projects_filtered$commits_frequency_dormant[projects_filtered$commits_frequency_dormant == 2] <- 0


projects_filtered[1] <- lapply(projects_filtered[1], as.numeric)
projects_filtered[4:5] <- lapply(projects_filtered[4:5], as.numeric)
projects_filtered[9] <- lapply(projects_filtered[9], as.numeric)
sapply(projects_filtered, class)



res.cox <- coxph(Surv(days_after_hackathon_for_last_commit, commits_frequency_dormant) ~ hackathon_location + number.of.participants + winner_weight, data = projects_filtered)
res.cox


summary(res.cox)
str(summary(res.cox))


table(projects_filtered$hackathon_location)


# Plot the baseline survival function
ggsurvplot(survfit(res.cox), color = "#2E9FDF",
           ggtheme = theme_minimal(), data = projects_filtered)





## Laptop


casualProjects = read.csv("C:\\Users\\Martin\\Dropbox\\masterthesis\\githubProjects_with_extra_info.csv", sep=';', na.strings=c(""))

library(survival)
library(survminer)
projects_filtered <- subset(casualProjects, select=c(6,21,22,24,26,31,33,34, 35))

projects_filtered$commits_frequency_dormant[projects_filtered$commits_frequency_dormant == 1] <- 2
projects_filtered$commits_frequency_dormant[projects_filtered$commits_frequency_dormant == 0] <- 1
projects_filtered$commits_frequency_dormant[projects_filtered$commits_frequency_dormant == 2] <- 0


projects_filtered[1] <- lapply(projects_filtered[1], as.numeric)
projects_filtered[4:5] <- lapply(projects_filtered[4:5], as.numeric)
projects_filtered[9] <- lapply(projects_filtered[9], as.numeric)
sapply(projects_filtered, class)



res.cox <- coxph(Surv(days_after_hackathon_for_last_commit, commits_frequency_dormant) ~ 
                     winner_weight + number.of.participants + skillsCovered, 
                 data = projects_filtered)
res.cox


summary(res.cox)
str(summary(res.cox))


table(projects_filtered$number.of.participants)


# Plot the baseline survival function
ggsurvplot(survfit(res.cox), color = "#2E9FDF", conf.int = TRUE,
           ggtheme = theme_minimal(), data = projects_filtered, xlim=c(0, 180))


####### PLOTS ###########


# Hackathon location
location_df <- with(projects_filtered,
               data.frame(number.of.participants = rep(mean(number.of.participants, na.rm = TRUE), 2), 
                          winner_weight = rep(mean(winner_weight, na.rm = TRUE), 2),
                          skillsCovered = rep(mean(skillsCovered, na.rm = TRUE), 2),
                          hackathon_location = c(0, 1)
               )
)


fit <- survfit(res.cox, newdata = location_df)
ggsurvplot(fit, conf.int = TRUE, data= location_df, legend.labs=c("Remote", "Co-located"),
           ggtheme = theme_minimal(), xlim=c(0, 180))



# Winner weight
winners_df <- with(projects_filtered,
                        data.frame(number.of.participants = rep(mean(number.of.participants, na.rm = TRUE), 11), 
                                   winner_weight = c(0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1),
                                   skillsCovered = rep(mean(skillsCovered, na.rm = TRUE), 11),
                                   hackathon_location = c(0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1)
                        )
)


fit <- survfit(res.cox, newdata = winners_df)
ggsurvplot(fit, conf.int = TRUE, data= winners_df, legend.labs=c("Weight=0", "Weight=0.1", "Weight=0.2", "Weight=0.3", "Weight=0.4", "Weight=0.5", "Weight=0.6", "Weight=0.7", "Weight=0.8", "Weight=0.9", "Weight=1"),
           ggtheme = theme_minimal())


# Number of participants
participants_df <- with(projects_filtered,
                   data.frame(number.of.participants = c(2, 3, 4, 5, 6, 7, 8, 9, 10), 
                              winner_weight = rep(mean(number.of.participants, na.rm = TRUE), 9),
                              skillsCovered = rep(mean(skillsCovered, na.rm = TRUE), 9),
                              hackathon_location = c(0, 0, 0, 0, 1, 1, 1, 1, 1)
                   )
)


fit <- survfit(res.cox, newdata = participants_df)
ggsurvplot(fit, conf.int = TRUE, data= participants_df,
           ggtheme = theme_minimal())


###############################

ggforest(res.cox, data = projects_filtered)


sum(projects_filtered$days_after_hackathon_for_last_commit > 50)