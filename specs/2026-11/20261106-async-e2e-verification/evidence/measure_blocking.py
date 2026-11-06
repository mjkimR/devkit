from pathlib import Path
import json
import os
import subprocess
import sys
import time
from unittest.mock import patch
from devkit_agt.features.isolated_execution.repositories.runs import Runs
from devkit_agt.features.isolated_execution.services.lifecycle import wait

root=Path.cwd()/f'scratch/blocking-consumer-{time.time_ns()}';root.mkdir(parents=True)
env={k:v for k,v in os.environ.items() if not k.startswith('GIT_')}
def git(*args):
 return subprocess.check_output(['git','-C',str(root),'-c','user.name=fixture','-c','user.email=fixture@example.com',*args],env=env,text=True).strip()
git('init','-q','-b','main');(root/'fixture').write_text('same-revision')
git('add','.');git('commit','-qm','controlled timing fixture');sha=git('rev-parse','HEAD')
python=str(Path(getattr(sys,'_base_executable',sys.executable)).resolve())
argv=(python,'-c',"import time; from pathlib import Path; assert Path('fixture').read_text()=='same-revision'; time.sleep(.8); print(sum(range(100000)))")
original=subprocess.Popen
rows=[]
for disabled in (True,False):
 for repetition in range(4):
  def launch(*args,**kwargs):
   process=original(*args,**kwargs)
   if disabled and len(args[0])>2 and str(args[0][2]).endswith('/runtime.py'):
    process.wait()
   return process
  runs=Runs(root)
  start=time.perf_counter()
  with patch('subprocess.Popen',launch):
   pending=runs.launch(sha,argv,None)
  submitted=time.perf_counter()
  # Same independent work in each arm. This may overlap only the asynchronous arm.
  assert (root/'fixture').read_text()=='same-revision'
  time.sleep(.9)
  collect=time.perf_counter()
  done=wait(runs,pending['run_id'],10,True)
  end=time.perf_counter()
  assert done['outcome']=='passed' and done['cleanup']['outcome'] in {'cleaned','already_clean'},done
  row={'mode':'synchronous-disabled-async' if disabled else 'asynchronous','warmup':repetition==0,'sha':sha,'run_id':done['run_id'],'launch_return_seconds':submitted-start,'collection_blocked_seconds':end-collect,'host_blocked_seconds':submitted-start+end-collect,'preparation_seconds':done['command_started_at']-done['started_at'],'command_and_observation_seconds':done['completed_at']-done['command_started_at'],'total_wall_seconds':end-start,'resources':done['resources']}
  rows.append(row)
Path('specs/2026-11/20261106-async-e2e-verification/blocking-measurements.json').write_text(json.dumps({'method':'Same fixture commit, argv, setup, isolated environment, machine and resource limits. Async disabled by waiting for the exact same supervisor process inside its launch Popen wrapper; one warmup then three samples per arm. 0.9s independent-work fixture follows launch in each arm. Timing includes process observation; not whole-suite speedup evidence.','platform':sys.platform,'rows':rows},indent=2)+'\n')
print(json.dumps(rows))
