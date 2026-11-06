"""Durably gated, parent-death-aware process group for source-only MCP stdio."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import time
from durable_json_v2 import write_new
from process_guard import process_identity


def live_members(group):
    p=subprocess.Popen(['ps','-axo','pid=,pgid=,stat='],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    try:output,_=p.communicate(timeout=2)
    except subprocess.TimeoutExpired:p.kill();p.communicate();raise
    if p.returncode:raise RuntimeError('cannot verify transport group')
    # The observer itself briefly inherits the group when run by its leader.
    return [int(a[0]) for line in output.splitlines() if len(a:=line.split())==3 and int(a[0])!=p.pid and int(a[1])==group and not a[2].startswith('Z')]



def run_guard(argv,directory,deadline):
    directory=Path(directory);pid=os.getpid();parent=os.getppid();identity=process_identity(pid);parent_identity=process_identity(parent)
    if os.getpgrp()!=pid or not identity or not parent_identity:raise ValueError('stdio guardian requires a new owned group and live parent')
    write_new(directory/'transport-process.json',{'pid':pid,'identity':identity,'parent_pid':parent,'parent_identity':parent_identity,'deadline_monotonic':deadline})
    stop=threading.Event();errors=[]
    signal.signal(signal.SIGTERM,lambda *_:stop.set());signal.signal(signal.SIGINT,lambda *_:stop.set())
    child=None;reason='held_guard_startup'
    try:
        child=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=None,start_new_session=False)
        # The actual server consumes one raw gate byte before tool dispatch.
        # Its complete process group identity is already fsynced above.
        child.stdin.write(b'G');child.stdin.flush()
        def forward(source,destination,maximum,eof_stops):
            total=0
            try:
                while not stop.is_set():
                    raw=os.read(source,65536)
                    if not raw:
                        if eof_stops:stop.set()
                        break
                    total+=len(raw)
                    if total>maximum:raise ValueError('stdio transport byte allowance')
                    view=memoryview(raw)
                    while view:view=view[os.write(destination,view):]
            except Exception as e:errors.append(type(e).__name__);stop.set()
        threading.Thread(target=forward,args=(0,child.stdin.fileno(),256*1024,True),daemon=True).start()
        threading.Thread(target=forward,args=(child.stdout.fileno(),1,32*1024**2,False),daemon=True).start()
        while not stop.wait(.1):
            if child.poll() is not None:reason='server_exit';break
            if time.monotonic()>=deadline:reason='absolute_deadline';break
            if process_identity(parent)!=parent_identity:reason='client_identity_gone';break
        else:reason='client_eof_or_termination'
    finally:
        # Keep this group leader alive during TERM and verification. If a child
        # resists TERM, KILL the entire owned group; outer recovery must then
        # verify disappearance and retain the missing/held guardian receipt.
        if process_identity(pid)!=identity:raise RuntimeError('transport guardian identity changed')
        os.killpg(pid,signal.SIGTERM)
        end=time.monotonic()+.8
        while time.monotonic()<end:
            if child is not None:child.poll()
            if not [p for p in live_members(pid) if p!=pid]:break
            time.sleep(.05)
        remaining=[p for p in live_members(pid) if p!=pid]
        if remaining:os.killpg(pid,signal.SIGKILL)
        if child is not None:
            child.wait(timeout=1);child.stdin.close();child.stdout.close()
        write_new(directory/'transport-guardian.json',{'reason':reason,'errors':errors,'server_descendants_quiescent':True,'group':pid,'identity':identity})


def settle_transport(directory):
    directory=Path(directory);record=directory/'transport-process.json';proof=directory/'transport-cleanup.json'
    if not record.exists():
        if (directory/'transport-launch.json').exists():raise RuntimeError('transport launch declared but identity absent; no continuation')
        return False
    value=json.loads(record.read_text());pid=value['pid'];identity=value['identity']
    members=live_members(pid)
    if members:
        if process_identity(pid)!=identity:raise RuntimeError('transport group identity ambiguous; no continuation')
        os.killpg(pid,signal.SIGTERM);end=time.monotonic()+5
        while time.monotonic()<end and live_members(pid):time.sleep(.1)
        if live_members(pid):
            if process_identity(pid)!=identity:raise RuntimeError('transport group owner lost; hold')
            os.killpg(pid,signal.SIGKILL);end=time.monotonic()+3
            while time.monotonic()<end and live_members(pid):time.sleep(.1)
    if live_members(pid):raise RuntimeError('transport still live; no continuation')
    result={'group':pid,'identity':identity,'live_group_members':[],'quiescent':True}
    if proof.exists():
        if json.loads(proof.read_text())!=result:raise ValueError('transport cleanup evidence differs')
    else:write_new(proof,result)
    return True

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',required=True,type=Path);a=p.parse_args()
    from source_only_mcp_v1 import validate_packet
    packet=validate_packet(json.loads(a.config.read_text()))
    run_guard([sys.executable,str(Path(__file__).with_name('source_only_mcp_v1.py')),'--config',str(a.config),'--gated'],Path(packet['log']).parent,packet['guard_deadline_monotonic'])
