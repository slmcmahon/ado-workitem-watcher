import json
import requests
import re
from requests.auth import HTTPBasicAuth
from adowork.work_item import WorkItem

class AdoContext:
    def __init__(self, org, project, pat):
        self.org = org
        self.project = project
        self.pat = pat

    def get_work_item(self, id):
        url = f"{self._get_base_url()}wit/workItems/{id}?api-version=7.1-preview.3"
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers, auth=self._get_credentials())
        return WorkItem(response.json())
    
    def add_design_doc_task(self, work_item, wiki_page_path):
        task_data = [
            {
                "op": "add",
                "path": "/fields/System.AreaPath",
                "value": work_item.area_path
            },
            {
                "op": "add",
                "path": "/fields/System.IterationPath",
                "value": work_item.iteration_path
            },
            {
                "op": "add",
                "path": "/fields/System.State",
                "value": "To Do"
            },
            {
                "op": "add",
                "path": "/fields/System.Description",
                "value": f"Complete the <a href=\"{wiki_page_path}\">design document</a> in the project wiki."
            },
            {
                "op": "add",
                "path": "/fields/System.Title",
                "value": "Complete the Design Document"
            },
            {
                "op": "add",
                "path": "/relations/-",
                "value": {
                "rel": "System.LinkTypes.Hierarchy-Reverse",
                "url": f"{self._get_base_url()}/wit/workItems/{work_item.id}",
                "attributes": {
                    "comment": "Linking task to PBI"
                    }
                }
            }
        ]
        
        task_url = f"{self._get_base_url()}wit/workItems/$Task?api-version=7.1-preview.3"
        headers = {"Content-Type": "application/json-patch+json"}
        response = requests.post(task_url, headers=headers, auth=self._get_credentials(), data=json.dumps(task_data))
        response_data = response.json()

        backlink = [
            {
                "op": "add",
                "path": "/relations/-",
                "value": {
                "rel": "System.LinkTypes.Hierarchy-Forward",
                "url": f"{self._get_base_url()}/wit/workItems/{response_data['id']}",
                "attributes": {
                    "comment": "Linking PBI to task"
                    }
                }
            }
        ]
        
        backlink_url = f"{self._get_base_url()}wit/workItems/{work_item.id}?api-version=7.1-preview.3"
        requests.patch(backlink_url, headers=headers, auth=self._get_credentials(), data=json.dumps(backlink))
        
    def create_wiki_page(self, work_item):
        page_content = f"#{work_item.id}"
        paths = self._get_wiki_doc_paths(work_item)
        wiki_page_path = ""
        for i, path in enumerate(paths):
            content = page_content if i == len(paths) - 1 else ""
            wiki_page_path = self._create_wiki_path(path, content)
            
        return wiki_page_path
    
    def _create_wiki_path(self, path, contents=""):
        data = {
            "content": contents,
        }
        
        sanitized_path = path.replace(' ', '%20')
        url = f"{self._get_base_url()}/wiki/wikis/{self.project}.wiki/pages?api-version=7.1-preview.1&path={sanitized_path}"
        headers = {"Content-Type": "application/json"}
        response = requests.put(url, headers=headers, auth=self._get_credentials(), data=json.dumps(data))
        
        if response.status_code >= 200 and response.status_code < 300:
            return response.json()['remoteUrl']
        else:
            return ""
            
        
    
    def _get_base_url(self):
        return f"https://dev.azure.com/{self.org}/{self.project}/_apis/"
    
    def _get_credentials(self):
        return HTTPBasicAuth("", self.pat)
    
    def _sanitize_title(self, title):
        return (title.replace('/', '-')
                     .replace('\\', '-')
                     .replace(':', '-')
                     .replace('*', '-')
                     .replace('?', '-')
                     .replace('"', '-')
                     .replace('<', '-')
                     .replace('>', '-')
                     .replace('|', '-'))
    
    def _get_wiki_doc_paths(self, work_item):
        paths = ["Technical Design Discussion"]
        area_path = work_item.area_path
        iteration_path = work_item.iteration_path
        
        # Build paths from iteration path
        for path in iteration_path.split('\\')[2:]:
            if paths:
                path = f"{paths[-1]}/{path}"
            paths.append(path)
        
        # Add area path to the paths
        last = paths[-1]
        area_leaf = re.sub(r"^EAR-AA-\d+-", "", area_path.split('\\')[-1])
        paths.append(f"{last}/{area_leaf}")
        
        # Add sanitized title to the final path
        sanitized_title = self._sanitize_title(work_item.title)
        paths.append(f"{paths[-1]}/{work_item.id} - {sanitized_title}")
        
        return paths