import os
from fire_opal_settings import *
from fire_opal_v2 import process_list

if 'SLURM_ARRAY_TASK_COUNT' in os.environ:
    task_count = int(os.environ['SLURM_ARRAY_TASK_COUNT'])
    task_min   = int(os.environ['SLURM_ARRAY_TASK_MIN'])
    task_id    = int(os.environ['SLURM_ARRAY_TASK_ID'])
else:
    task_count = 1
    task_min   = 0
    task_id    = 0


filelist = os.listdir(datadirectory)
myfilelist = filelist[task_id-task_min : : task_count]
print('processor %d of %d has %d files' % (task_id-task_min, task_count, len(myfilelist)))
process_list(myfilelist)

