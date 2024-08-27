from collections import defaultdict

class WorkItem:
    
    def __init__(self, data):
        data = defaultdict(lambda: defaultdict(dict), data)
        self.id = data["id"]
        self.title = data["fields"].get("System.Title", "")
        self.description = data["fields"].get("System.Description", "")
        self.acceptance_criteria = data["fields"].get("Microsoft.VSTS.Common.AcceptanceCriteria", "")
        self.status = data["fields"].get("System.State", "")
        self.iteration_path = data["fields"].get("System.IterationPath", "")
        self.area_path = data["fields"].get("System.AreaPath", "")
        self.created_by = data["fields"]["System.CreatedBy"].get('displayName', "")

        # Handling tags and specific flags more cleanly
        self.dd_required = self._parse_tags(data["fields"].get("System.Tags", ""))

    def __repr__(self):
        return f"WorkItem(id={self.id}, title='{self.title}', description='{self.description}', status='{self.status}')"

    def _parse_tags(self, tags):
        """ Parse tags to determine if 'dd-required' is present. """
        return 'dd-required' in tags
    