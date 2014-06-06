#============================================================
# Taekyung Kim
#============================================================

from Queue import Queue

#------------------------------------------------------------
def queue_2_list(queue_input):
    """
From queue to list
    """
    output_list = []
    while True:
        try:
            output_list.append(queue_input.get_nowait())
        except:
            break
    return output_list
#------------------------------------------------------------
def list_2_queue(list_input):
    """
From list to queue
    """
    output_queue = Queue()
    while True:
        try:
            output_queue.put_nowait(list_input.pop(0))
        except:
            break
    return output_queue

