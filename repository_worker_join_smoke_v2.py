"""Portable Git worker join/recovery smoke; authored data only, zero model calls.

Coordinator creates local remotes; distinct ref prefixes also permit one shared remote. Client remotes are supplied using
existing authenticated Git transport; this module installs no service/access.
Local rehearsal never establishes that a second physical host participated.
"""
import argparse,gzip,hashlib,io,json,os,re,signal,subprocess,sys,time
from pathlib import Path
from durable_json_v2 import write_new
from git_queue import GitQueue
from git_artifacts import GitArtifacts
from process_guard import process_identity
from source_only_stdio_guard_v1 import live_members

HERE=Path(__file__).resolve().parent
RELEASE=['worker.py','git_queue.py','git_artifacts.py','process_guard.py','artifact_bundle.py',
         'grade_cached.py','durable_json_v2.py','source_only_stdio_guard_v1.py','repository_worker_join_smoke_v2.py']
BRANCH='join-smoke-v2'
ARTIFACT_PREFIX='join-smoke-artifacts-v2'


def smoke_manifest(state):
    manifest=state['manifest'];worker=manifest['worker']
    if (manifest.get('schema')!=1 or manifest.get('scope')!='authored two-host join/recovery smoke only; no models or benchmark tasks'
            or not re.fullmatch(r'worker-[0-9]{2,}',worker) or set(state['jobs'])!={'join-fast','join-recover'}
            or set(manifest['release_sha256'])!=set(RELEASE)
            or any(not re.fullmatch('[a-f0-9]{64}',v) for v in manifest['release_sha256'].values())):raise ValueError('exact authored smoke inventory required')
    expected=[{'job_id':name,'capabilities':['join-smoke-v2'],'depends_on':deps,'assigned_worker':worker,
        'max_attempts':attempts,'max_availability_attempts':1,
        'spec':{'kind':'supervised_command','profile':profile}}
        for name,deps,attempts,profile in [('join-fast',[],1,'authored-fast'),('join-recover',['join-fast'],2,'authored-recover')]]
    if manifest['jobs']!=expected:raise ValueError('authored smoke job definitions differ')
    return manifest


def bounded_archive(path):
    import tarfile
    maximum=8*1024**2;raw=bytearray()
    with gzip.open(path,'rb') as source:
        while True:
            part=source.read(min(65536,maximum+1-len(raw)))
            if not part:break
            raw.extend(part)
            if len(raw)>maximum:raise ValueError('smoke decompressed archive limit')
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:') as archive:
        members=archive.getmembers()
        if (not 2<=len(members)<=32 or len({m.name for m in members})!=len(members)
                or any(not m.isfile() or not 0<=m.size<=2*1024**2 or len(m.name)>512
                    or Path(m.name).is_absolute() or any(p in ('','.','..') for p in m.name.split('/')) for m in members)
                or sum(m.size for m in members)>maximum):raise ValueError('smoke archive member bound/inventory')
        indexes=[m for m in members if m.name=='artifact-index.json']
        if len(indexes)!=1 or indexes[0].size>65536:raise ValueError('bounded unique smoke index required')
        value=json.loads(archive.extractfile(indexes[0]).read(65537));index=value['files']
        if not isinstance(index,list) or not 1<=len(index)<=31:raise ValueError('smoke index count limit')
        if any(not isinstance(item,dict) or set(item)!={'member','bytes','sha256'} for item in index):raise ValueError('smoke index fields')
        if len({item['member'] for item in index})!=len(index) or {m.name for m in members}!={item['member'] for item in index}|{'artifact-index.json'}:raise ValueError('smoke index/member identity differs')
        data={}
        for item in index:
            member=archive.getmember(item['member'])
            if type(item['bytes']) is not int or member.size!=item['bytes'] or not re.fullmatch('[a-f0-9]{64}',item['sha256']):raise ValueError('smoke index size/hash schema')
            content=archive.extractfile(member).read(member.size+1)
            if len(content)!=item['bytes'] or hashlib.sha256(content).hexdigest()!=item['sha256']:raise ValueError('received full index differs')
            data[item['member']]=content
    return data


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def initialize(root,worker):
    root=Path(root).resolve()
    if root.exists() or not re.fullmatch(r'worker-[0-9]{2,}',worker):raise ValueError('new private smoke root and generic worker required')
    root.mkdir(mode=0o700,parents=True);release=root/'release';release.mkdir(mode=0o700)
    hashes={name:sha(HERE/name) for name in RELEASE}
    for name in RELEASE:(release/name).write_bytes((HERE/name).read_bytes())
    for name in ('queue.git','artifacts.git'):
        subprocess.run(['git','init','--quiet','--bare',str(root/name)],check=True,timeout=20)
        (root/name).chmod(0o700)
    manifest={'schema':1,'scope':'authored two-host join/recovery smoke only; no models or benchmark tasks',
        'release_sha256':hashes,'worker':worker,'jobs':[
          {'job_id':'join-fast','capabilities':['join-smoke-v2'],'depends_on':[],'assigned_worker':worker,
           'max_attempts':1,'max_availability_attempts':1,'spec':{'kind':'supervised_command','profile':'authored-fast'}},
          {'job_id':'join-recover','capabilities':['join-smoke-v2'],'depends_on':['join-fast'],'assigned_worker':worker,
           'max_attempts':2,'max_availability_attempts':1,'spec':{'kind':'supervised_command','profile':'authored-recover'}}]}
    GitQueue(str(root/'queue.git'),branch=BRANCH).initialize(manifest)
    write_new(root/'manifest.json',manifest)
    result={'schema':1,'status':'join_smoke_prepared_not_remote_validated','worker':worker,
        'local_queue_remote':str(root/'queue.git'),'local_artifact_remote':str(root/'artifacts.git'),
        'branch':BRANCH,'release_sha256':hashes,'manifest_sha256':sha(root/'manifest.json'),
        'models_invoked':0,'benchmark_tasks':0,'second_host_verified':False,
        'client_command_template':'python3 repository_worker_join_smoke_v2.py --client <new-private-runtime> --queue <existing-SSH-Git-URL> --artifacts <existing-SSH-Git-URL> --worker '+worker}
    write_new(root/'preparation.json',result);return result


def worker_once(root,config,*,interrupt=False):
    # Three bounded invocations after the initial fast job: interrupted work,
    # recovery/publication, and the declared second authored attempt.
    name='interrupted' if interrupt else 'worker-'+str(len(list(root.glob('worker-*.log')))+1)
    path=root/(name+'.log')
    with path.open('xb') as log:
        process=subprocess.Popen([sys.executable,str(HERE/'worker.py'),'--config',str(config),'--once'],stdout=log,stderr=log)
        try:
            if interrupt:
                deadline=time.monotonic()+90
                while time.monotonic()<deadline:
                    counter=root/'executions.jsonl'
                    if counter.exists() and any(json.loads(line)['phase']=='recover' for line in counter.read_text().splitlines()):break
                    if process.poll() is not None:raise ValueError('recovery fixture exited before interruption')
                    time.sleep(.05)
                else:raise TimeoutError('authored recovery work did not start')
                identity=process_identity(process.pid)
                if not identity:raise ValueError('worker identity absent before interruption')
                write_new(root/'interrupted-worker.json',{'pid':process.pid,'identity':identity,'signal':'SIGKILL','models':0})
                process.kill();process.wait(timeout=2)
                active=json.loads((root/'state/active.json').read_bytes());attempt=Path(active['directory'])
                deadline=time.monotonic()+10
                while not (attempt/'report.json').exists():
                    if time.monotonic()>deadline:raise TimeoutError('orphan guardian did not settle promptly')
                    time.sleep(.05)
                running=json.loads((attempt/'running.json').read_bytes())
                if live_members(running['pid']):raise ValueError('interrupted owned command group remains live')
            else:process.wait(timeout=150)
        finally:
            if process.poll() is None:process.kill();process.wait(timeout=2)


def client(root,queue_remote,artifact_remote,worker):
    root=Path(root).resolve()
    if root.exists():raise ValueError('new client smoke root required')
    queue=GitQueue(queue_remote,branch=BRANCH);snapshot=queue.snapshot();manifest=smoke_manifest(snapshot)
    if manifest['worker']!=worker:raise ValueError('assigned smoke worker differs')
    for name,digest in manifest['release_sha256'].items():
        if name not in RELEASE or sha(HERE/name)!=digest:raise ValueError('client frozen release differs')
    if set(manifest['release_sha256'])!=set(RELEASE):raise ValueError('complete portable release bindings required')
    root.mkdir(mode=0o700,parents=True)
    config={'worker':worker,'remote':queue_remote,'branch':BRANCH,'state_dir':str(root/'state'),
        'artifact_store':{'remote':artifact_remote,'prefix':ARTIFACT_PREFIX,'wall_seconds':60,'max_bytes':1024**2},
        'capabilities':['join-smoke-v2'],'heartbeat_seconds':5,'poll_seconds':1,
        'policy':{'startup_seconds':20,'idle_seconds':20,'wall_seconds':30,'lease_seconds':300,
                  'lease_safety_seconds':20,'terminal_grace_seconds':.2,'kill_grace_seconds':.3},
        'profiles':{phase:{'argv':[sys.executable,str(HERE/'repository_worker_join_smoke_v2.py'),
            '--payload','{attempt_dir}','--counter',str(root/'executions.jsonl'),'--phase',name],
            'cwd':str(root)} for phase,name in [('authored-fast','fast'),('authored-recover','recover')]}}
    path=root/'worker-config.json';write_new(path,config)
    worker_once(root,path)
    if queue.snapshot()['jobs']['join-fast']['state']!='completed':raise ValueError('fast Git publication failed')
    worker_once(root,path,interrupt=True)
    worker_once(root,path) # Reconcile the interrupted attempt; never rerun it.
    # Recovery deliberately applies the worker's bounded environment backoff.
    # Respect it rather than mistaking a healthy paused worker for a lost job.
    deadline=time.monotonic()+30
    while True:
        paused=queue.snapshot().get('workers',{}).get(worker,{})
        retry=paused.get('retry_at')
        if not paused.get('paused') or isinstance(retry,(int,float)) and retry<=time.time():break
        if retry is None or time.monotonic()>=deadline:raise TimeoutError('authored recovery needs action or exceeded30second backoff bound')
        time.sleep(.5)
    worker_once(root,path) # Declared second authored attempt, no LLM session.
    state=queue.snapshot();jobs=state['jobs']
    if any(v['state']!='completed' for v in jobs.values()):raise ValueError('smoke jobs not completed')
    if len(jobs['join-fast']['attempts'])!=1 or len(jobs['join-recover']['attempts'])!=2:raise ValueError('authored attempt count differs')
    rows=[json.loads(line) for line in (root/'executions.jsonl').read_bytes().splitlines()]
    if [row['phase'] for row in rows]!=['fast','recover','recover']:raise ValueError('unexpected command replay')
    value={'schema':1,'status':'client_git_join_and_parent_loss_recovery_passed','worker':worker,
        'command_executions':3,'model_calls':0,'benchmark_tasks':0,'completed_jobs':2,
        'receiver_verification_pending':True,'second_physical_host_verified':False,
        'auth_or_subscription_tested':False,'note':'Actual distinct-host participation requires coordinator transport evidence; no hostnames are published.'}
    write_new(root/'result.json',value);return value


def receive(root,queue_remote,artifact_remote):
    root=Path(root).resolve()
    if root.exists():raise ValueError('new receiver root required')
    state=GitQueue(queue_remote,branch=BRANCH).snapshot();smoke_manifest(state)
    if len(state['jobs']['join-fast']['attempts'])!=1 or len(state['jobs']['join-recover']['attempts'])!=2:raise ValueError('exact smoke attempt count required')
    if ([a['status'] for a in state['jobs']['join-fast']['attempts']]!=['completed']
            or [a['status'] for a in state['jobs']['join-recover']['attempts']]!=['interrupted','completed']
            or state['jobs']['join-recover']['attempts'][0]['reason']!='environment'):raise ValueError('parent-loss smoke dispositions differ')
    root.mkdir(mode=0o700,parents=True)
    count=0
    for name,job in state['jobs'].items():
        if job['state']!='completed':raise ValueError('completed smoke jobs required')
        attempt=job['attempts'][-1];reference=attempt['result']['artifacts'][0];destination=root/(name+'.tar.gz')
        GitArtifacts(artifact_remote,prefix=ARTIFACT_PREFIX,max_bytes=1024**2,wall_seconds=60).fetch(reference,destination)
        data=bounded_archive(destination)
        bindings=[value for key,value in data.items() if key.endswith('/attempt-binding.json')]
        payloads=[value for key,value in data.items() if key.endswith('/authored-result.json')]
        if len(bindings)!=1 or len(payloads)!=1:raise ValueError('unique attempt binding and authored payload required')
        binding=json.loads(bindings[0]);payload=json.loads(payloads[0])
        if (binding['attempt_id']!=attempt['attempt_id'] or binding['worker']!=attempt['worker'] or binding['job_id']!=name
                or binding['generation']!=attempt['generation']):raise ValueError('receiver queue/attempt identity differs')
        if payload!={'phase':'fast' if name=='join-fast' else 'recover','marker':'JOIN_SMOKE_ONLY','model_calls':0}:raise ValueError('authored payload differs')
        count+=len(data)
    interrupted=state['jobs']['join-recover']['attempts'][0]
    reference=interrupted['artifacts'][0];destination=root/'join-interrupted.tar.gz'
    GitArtifacts(artifact_remote,prefix=ARTIFACT_PREFIX,max_bytes=1024**2,wall_seconds=60).fetch(reference,destination)
    data=bounded_archive(destination)
    bindings=[json.loads(value) for key,value in data.items() if key.endswith('/attempt-binding.json')]
    reports=[json.loads(value) for key,value in data.items() if key.endswith('/report.json')]
    if (len(bindings)!=1 or len(reports)!=1 or bindings[0]['job_id']!='join-recover'
            or bindings[0]['worker']!=interrupted['worker'] or bindings[0]['attempt_id']!=interrupted['attempt_id']
            or bindings[0]['generation']!=interrupted['generation'] or reports[0]['reason']!='parent_lost'
            or reports[0]['exit_code']>=0):raise ValueError('interrupted attempt identity/report differs')
    count+=len(data)
    value={'schema':1,'status':'independent_git_receiver_verified_smoke_artifacts','completed_jobs':2,
        'archived_attempts_verified':3,'indexed_files_verified':count,'model_calls':0,'benchmark_tasks':0,'second_physical_host_verified':False}
    write_new(root/'result.json',value);return value


def payload(directory,counter,phase):
    if phase not in ('fast','recover'):raise ValueError('authored phase required')
    directory=Path(directory);counter=Path(counter)
    with counter.open('a') as stream:
        stream.write(json.dumps({'phase':phase,'at':time.time()})+'\n');stream.flush();os.fsync(stream.fileno())
    if phase=='recover':time.sleep(2)
    write_new(directory/'authored-result.json',{'phase':phase,'marker':'JOIN_SMOKE_ONLY','model_calls':0})
    print(json.dumps({'type':'result','subtype':'success','is_error':False}),flush=True)


if __name__=='__main__':
    os.umask(0o077);p=argparse.ArgumentParser(description=__doc__);mode=p.add_mutually_exclusive_group(required=True)
    for name in ('initialize','client','receive','payload'):mode.add_argument('--'+name,type=Path)
    p.add_argument('--worker',default='worker-12');p.add_argument('--queue');p.add_argument('--artifacts');p.add_argument('--counter',type=Path);p.add_argument('--phase')
    args=p.parse_args()
    if args.initialize:print(json.dumps(initialize(args.initialize,args.worker),sort_keys=True))
    elif args.client:print(json.dumps(client(args.client,args.queue,args.artifacts,args.worker),sort_keys=True))
    elif args.receive:print(json.dumps(receive(args.receive,args.queue,args.artifacts),sort_keys=True))
    else:payload(args.payload,args.counter,args.phase)
