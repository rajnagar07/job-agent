from jobs.remoteok import get_jobs as remote_jobs
from jobs.wellfound import get_jobs as wellfound_jobs


def collect_jobs():
    jobs = []

    # Collect jobs from RemoteOK
    jobs.extend(remote_jobs())

    # Collect jobs from Wellfound
    jobs.extend(wellfound_jobs())

    return jobs