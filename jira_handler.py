from jira import JIRA

class JiraHandler:

    def __init__(self, jira_config):
        self.jira_proj_id = jira_config['ProjId']
        self.labels = jira_config['Labels'].split(',')
        self.url = jira_config['URL']
        self.basic_auth = (jira_config['Email'], jira_config['AuthToken'])
        self.jira = JIRA(basic_auth=self.basic_auth, server=self.url)

    def create_issue(self, summary, description):
        fields_dict = {
          'project': {'id': self.jira_proj_id},
          'summary': summary,
          'description': description,
          'issuetype': {'name': 'Bug'},
          'priority': {'name': 'P2'}
        }
        new_issue = self.jira.create_issue(fields_dict)
        new_issue.update(fields={"labels": self.labels})

    def get_alert_text(self, alert, jira_format=False):
        h2 = ""
        h3 = ""
        if jira_format:
            h2 = "h2. "
            h3 = "h3. "
        vuln = alert['securityVulnerability']
        advisory = vuln['advisory']
        alert_text = "\n%sPackage: %s\n\
%sSummary:\n%s\n\
%sSeverity: %s\n\
%sDescription:\n%s\n\
%sVulnerable Range: %s\n" % (h2, vuln['package']['name'], h3, advisory['summary'], h3, advisory['severity'],
                             h3, advisory['description'], h3, vuln['vulnerableVersionRange'])
        if vuln["firstPatchedVersion"]:
            alert_text += "%sFirst Patched Version: %s\n" % (h3, vuln["firstPatchedVersion"]["identifier"])
        else:
            alert_text += "%sFirst Patched Version: Not Available\n" % h3
        alert_text += "%sReferences:\n" % h3
        if advisory["references"]:
            for reference in advisory["references"]:
                alert_text += "%s\n" % reference["url"]
            alert_text += "\n\n"
        else:
            alert_text += "Not Available\n\n"
        if jira_format:
            alert_text += "----------------------------\n\n"
        return alert_text

    def create_issues_by_option(self, repo, alert_list, consolidated=True):
        scripting_text = "\n_Note: This ticket was created by an automation tool_\n"
        if not consolidated:
            for alert in alert_list:
                package = alert['securityVulnerability']['package']['name']
                summary = "%s has a vulnerable dependency %s" % (repo, package)
                print "**Creating ticket: %s\n" % summary
                description = self.get_alert_text(alert, True)
                description = scripting_text + description
                self.create_issue(summary, description)
        else:
            description = ""
            for alert in alert_list:
                description += self.get_alert_text(alert, True)
            summary = "%s has one more vulnerable dependencies" % repo
            print "**Creating ticket: %s\n" % summary
            description = scripting_text + description
            self.create_issue(summary, description)
