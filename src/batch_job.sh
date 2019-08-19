#!/bin/sh
# sbatch --array=0-7 --job=fireopal batch_job.sh
~/anaconda3/envs/fireopal/bin/python batch_job.py
