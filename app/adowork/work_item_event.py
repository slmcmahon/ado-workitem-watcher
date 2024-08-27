from collections import defaultdict

class WorkItemEvent:
    def __init__(self, data):
        data = defaultdict(lambda: defaultdict(dict), data)
        
        self.event_type = data['eventType']
        resource = data['resource']
        fields = {}
        if self.event_type == 'workitem.created':
            self.id = resource['id']
            fields = resource['fields']
            self.work_item_type = fields['System.WorkItemType']
            self.tags = fields['System.Tags'] if 'System.Tags' in fields else None
        elif self.event_type == 'workitem.updated':
            fields = resource['revision']['fields']
            self.id = resource['workItemId']
            self.work_item_type = fields['System.WorkItemType']
            self.tags = fields['System.Tags'] if 'System.Tags' in fields else None
        else:
            self.id = -1
            self.work_item_type = 'unrecognized'
            self.tags = None 
            
            
            
        
        
        