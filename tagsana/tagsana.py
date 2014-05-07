from asana import AsanaException, AsanaAPI
from creds import APIKEY

from collections import defaultdict

class Tagsana(object):
    def __init__(self):
        self.api = AsanaAPI(APIKEY)

    def currate_tasks(self, task_list):
        currated_tasks = []
        task_ids = []
        for task in task_list:
            if not any([task['id']==tid for tid in task_ids]):
                currated_tasks.append(task)
                task_ids.append(task['id'])
        return currated_tasks

    def get_count(self, wss=None, users=None, projs=None):
        """
        Counts the tags based on the following params:
        - wss: workspace to look for tasks
        - users: all tasks attributed to a user (req: ws)
        - projs: all tasks under a list of projects (req: ws)
        All params are expected to be Asana 'id'(s).
        """
        if wss:
            if not isinstance(wss, list):
                wss = [wss]
        else:
            wss = self.api.list_workspaces()
        tasks = []
        for ws in wss:
            if users and not projs:
                #Get all tasks for a user under wss
                if not isinstance(users, list):
                    users = [users]
                for user in users:
                    tasks += self.api.list_tasks(ws['id'], user)
            elif users and projs:
                #TODO: Case where want to know user activity across spec projs
                pass
            else:
                #No user defined, find projs
                if projs is not None and not isinstance(projs, list):
                    projs = [projs]
                else:
                    projs = self.api.list_projects(ws['id'])
                for proj in projs:
                    tasks += self.api.get_project_tasks(proj['id'])

        tasks = self.currate_tasks(tasks)

        count = defaultdict(int)
        for task in tasks:
            try:
                for tag in self.api.get_task_tags(task['id']):
                    count[tag['name']] += 1
            except:
                pass
        return count

