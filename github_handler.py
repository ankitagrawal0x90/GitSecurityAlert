import requests

class GithubHandler:

    def __init__(self, github_config, query):
        self.git_url = github_config['URL']
        self.org = github_config['Organization']
        self.git_headers = {
         'Accept': 'application/json',
         'Authorization': 'Bearer %s' % (github_config['AuthToken']),
        }
        self.query = query
        self.repos_all = list()
        self.repos_with_alerts = dict()

    def run_query(self, page_cursor):
        query = self.query % (page_cursor, self.org)
        response = requests.post(self.git_url, json={'query': query}, headers=self.git_headers)
        if response.status_code == 200:
            self.parse_and_store_response(response.json())
            return response.json()
        else:
            raise Exception("Query failed to run by returning code of {}. {}".format(response.status_code, self.query))

    def parse_and_store_response(self, response):
        nodes = response['data']['organization']['repositories']['nodes']
        for node in nodes:
            self.repos_all.append(node['name'])
            vuln_nodes = node['vulnerabilityAlerts']['nodes']
            if vuln_nodes:
                self.repos_with_alerts[node['name']] = vuln_nodes

    def parse_all_alerts(self):
        for repo, alerts in self.repos_with_alerts.items():
            self.get_repo_alerts(repo, alerts)


    def query_all_repos(self):
        print "Initializing....\n"
        print "Quering alerts for first 100 repos....."
        result = self.run_query("null")
        pagination = result['data']['organization']['repositories']['pageInfo']
        #print pagination
        while pagination['hasNextPage']:
            print "Quering alerts for next 100 repos....."
            result = self.run_query('"%s"' % pagination['endCursor'])
            # print result
            pagination = result['data']['organization']['repositories']['pageInfo']
            #print pagination
        print "Initialization Complete.\n"

    def get_all_alerts(self):
        return self.repos_with_alerts

    def get_all_repos(self):
        return self.repos_all
