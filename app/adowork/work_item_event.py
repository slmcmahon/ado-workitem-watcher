from collections import defaultdict

class WorkItemEvent:
    def __init__(self, data):
        data = defaultdict(lambda: defaultdict(dict), data)
        
        event_type = data['eventType']
        self.event_type = event_type.replace('workitem.', '')
        resource = data['resource']
        fields = {}
        if event_type == 'workitem.created':
            self.id = resource['id']
            fields = resource['fields']
            self.work_item_type = fields['System.WorkItemType']
            self.tags = fields['System.Tags'] if 'System.Tags' in fields else None
        elif event_type == 'workitem.updated':
            fields = resource['revision']['fields']
            self.id = resource['workItemId']
            self.work_item_type = fields['System.WorkItemType']
            self.tags = fields['System.Tags'] if 'System.Tags' in fields else None
        else:
            self.id = -1
            self.work_item_type = 'unrecognized'
            self.tags = None 
            
            
            
        
        
        