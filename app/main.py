from adowork import ado_context
from adowork.work_item_event import WorkItemEvent
from azure.servicebus import ServiceBusClient
import time
import json
import os

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
                messages = receiver.receive_messages(max_message_count=30, max_wait_time=5)
                for msg in messages:
                    print('-' * 120)

                    body = b''.join(msg.body).decode('utf-8')
                    msg_content = json.loads(body)
                    
                    event = WorkItemEvent(msg_content)
                    try:
                        if event.id > 0:
                            queuetime =  msg.enqueued_time_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
                            wi = adoctx.get_work_item(event.id)
                            print(f'{queuetime} - Work item {event.event_type}: {event.id} - {wi.title}')
                            dd_required = wi.dd_required
                            
                            if dd_required:
                                url = adoctx.create_wiki_page(wi)
                                if url != '':
                                    print(f'Wiki page created: {url}')
                                    task_id = adoctx.add_design_doc_task(wi, url)
                                    print(f'Design doc task created: {task_id}')
                        else:
                            print("Event was either not a PBI or not tagged as dd-required.")

                    except KeyError as e:
                        print(f'Error: {e}')
                    
                    receiver.complete_message(msg)
                time.sleep(int(os.environ["ASB_POLL_INTERVAL_SECONDS"], 10))

if __name__ == "__main__":
    receive_messages_continuously()