import sys
import os

feat_prefix = 'feat-'

def featless_branch(git_output):
    sha, remote = git_output.split()
    branch_name = os.path.basename(remote)
    return branch_name.replace('feat-', '', 1)

if __name__ == '__main__':
    for line in sys.stdin:
        sys.stdout.write('{branch}\n'.format(branch=featless_branch(line)))
