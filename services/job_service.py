from jobs.remoteok import get_jobs as remote_jobs
from jobs.wellfound import get_jobs as wellfound_jobs
from jobs.greenhouse import get_all_jobs


def collect_jobs():
    jobs = []

    # RemoteOK
    print("Collecting jobs from RemoteOK...")
    jobs.extend(remote_jobs())

    # Wellfound
    print("Collecting jobs from Wellfound...")
    jobs.extend(wellfound_jobs())

    # Greenhouse
    print("Collecting jobs from Greenhouse...")
    jobs.extend(get_all_jobs())

    return jobs