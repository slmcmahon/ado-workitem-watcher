from adowork import ado_context
from adowork.work_item_event import WorkItemEvent
from azure.servicebus import ServiceBusClient
import time
import json
import os
import uuid 

def handle_workitem_created(msg_content):
    work_item_type = msg_content['resource']['fields']['System.WorkItemType']
    if work_item_type == 'Product Backlog Item':
        id = msg_content["resource"]["id"]
        current_time = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        print(f'{current_time} - Work item {id} created')
        return id
    return 0

def handle_workitem_updated(msg_content):
    work_item_type = msg_content['resource']['revision']['fields']['System.WorkItemType']
    if work_item_type == 'Product Backlog Item':
        id = msg_content["resource"]["workItemId"]
        current_time = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        print(f'{current_time} - Work item {id} updated')
        return id
    return 0

def handle_unknown_event(event_type):
    print(f'Unknown event type: {event_type}')
    
event_handlers = {
    'workitem.created': handle_workitem_created,
    'workitem.updated': handle_workitem_updated
}


def receive_messages_continuously():
    print("creating service bus client")
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=os.environ["ASB_CONNECTION_STRING"], logging_enable=True)
    print("creating ado context")
    adoctx = ado_context.AdoContext(os.environ["ADO_ORG"], os.environ["ADO_PROJECT"], os.environ["ADO_PAT"])

    # Continuously receive messages from the queue
    with servicebus_client:
        receiver = servicebus_client.get_queue_receiver(queue_name=os.environ["ASB_QUEUE"])
        with receiver:
            while True:  # Infinite loop to keep the application running
                messages = receiver.receive_messages(max_message_count=10, max_wait_time=5)
                for msg in messages:
                    print('-'*40)

                    body = b''.join(msg.body).decode('utf-8')
                    msg_content = json.loads(body)
                    
                    event = WorkItemEvent(msg_content)
                    try:
                        if event.id > 0:
                            wi = adoctx.get_work_item(event.id)
                            dd_required = wi.dd_required
                            
                            if dd_required:
                                url = adoctx.create_wiki_page(wi)
                                if url != '':
                                    print(f'Wiki page created: {url}')
                                    adoctx.add_design_doc_task(wi, url)
                        else:
                            print("Event was either not a PBI or not tagged as dd-required.")

                    except KeyError as e:
                        print(f'Error: {e}')
                    
                    print('-'*40)

                    receiver.complete_message(msg)
                time.sleep(int(os.environ["ASB_POLL_INTERVAL_SECONDS"], 10))

if __name__ == "__main__":
    receive_messages_continuously()