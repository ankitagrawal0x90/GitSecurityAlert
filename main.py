from github_handler import GithubHandler
from jira_handler import JiraHandler
from vuln_query import query

import configparser

class Options:

    def __init__(self, alerts_dict):
        self.alerts_dict = alerts_dict

    def get_repo_option_from_user(self):
        self.print_repo_names()
        print("Enter repository name to see alert options (0 to exit): "),
        option = raw_input()
        if option == "0":
            return option
        else:
            if option in self.alerts_dict:
                return option
            else:
                print "\nInvalid Input!!\n"
                return self.get_repo_option_from_user()

    def get_alert_option_from_user(self):
        print "*****Alert Options******"
        print "v : View all alerts"
        print "c : Create ticket for all alerts"
        print "m : Create ticket for multiple alerts"
        print "i : Create ticket for individual alerts"
        print "b : Back to repos"
        print "Enter option: ",
        option = raw_input()
        if option in ['v', 'c', 'm', 'i', 'b']:
            return option
        else:
            print "Invalid Option!!"
            return self.get_alert_option_from_user()

    def print_repo_names(self):
        print "**Alerts found for following repos"
        for repo in self.alerts_dict.keys():
            print repo

    def create_issues_for_alerts(self, repo, jiraHandler):
        alert_option = self.get_alert_option_from_user()
        alert_list_all = self.alerts_dict[repo]
        if alert_option == 'v':
            repo_alerts_text = ""
            for alert in alert_list_all:
                repo_alerts_text += jiraHandler.get_alert_text(alert)
            print repo_alerts_text
        elif alert_option == 'c':
            jiraHandler.create_issues_by_option(repo, alert_list_all)
        elif alert_option == 'm':
            alert_list_user = self.get_alert_list_from_user(alert_list_all, jiraHandler)
            jiraHandler.create_issues_by_option(repo, alert_list_user)
        elif alert_option == 'i':
            alert_list_user = self.get_alert_list_from_user(alert_list_all, jiraHandler)
            jiraHandler.create_issues_by_option(repo, alert_list_user, False)
        if alert_option != 'b':
            self.create_issues_for_alerts(repo, jiraHandler)

    def get_alert_list_from_user(self, alerts, jiraHandler):
        alert_list = list()
        for alert in alerts:
            print jiraHandler.get_alert_text(alert)
            print "Include this alert for Jira ticket (Y/y for Yes)? ",
            option = raw_input()
            if option in ['y', 'Y', 'Yes']:
                alert_list.append(alert)
        return alert_list


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    github_config = config['Github']
    jira_config = config['Jira']
    githubHandler = GithubHandler(github_config, query)
    githubHandler.query_all_repos()
    alerts_dict = githubHandler.get_all_alerts()
    options = Options(alerts_dict)
    jiraHandler = JiraHandler(jira_config)
    repo_option = options.get_repo_option_from_user()
    while repo_option != "0":
        options.create_issues_for_alerts(repo_option, jiraHandler)
        repo_option = options.get_repo_option_from_user()
