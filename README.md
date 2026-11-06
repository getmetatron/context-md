# Generic worker onboarding v2

This branch contains an authored Git join/recovery smoke test only. It makes no
model calls and reads no benchmark tasks or Claude credentials. Python3.10+ and
Git are required. Authenticate Git locally with your own repository write access;
do not copy credentials between people.

Run from a new directory on the second worker:

```sh
git clone --single-branch --branch research/worker-join-v2 https://github.com/getmetatron/context-md.git context-worker-join-v2
cd context-worker-join-v2
python3 repository_worker_join_smoke_v2.py --client ../context-worker-12-smoke-v2 --queue https://github.com/getmetatron/context-md.git --artifacts https://github.com/getmetatron/context-md.git --worker worker-12
```

The smoke deliberately interrupts one authored command, checks its cleanup, then
executes its single registered recovery attempt. It should finish in about a
minute; every phase is bounded. Study model draws never inherit this retry rule.
The coordinator must receive and verify all three attempt archives afterward.
This does not authenticate Claude or enable any research task. Subscription-only
authentication and disabled paid extra usage must be verified locally later.
This Mac remains the study's native-runtime coordinator; GitHub carries the queue.
