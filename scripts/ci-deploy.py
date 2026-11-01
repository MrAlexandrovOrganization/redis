import os,re,subprocess,tempfile
from pathlib import Path

def main():
 sha=os.environ['DEPLOY_SHA']
 if not re.fullmatch('[0-9a-f]{40}',sha):raise ValueError('Invalid revision')
 os.umask(0o077)
 with tempfile.TemporaryDirectory() as temporary:
  t=Path(temporary)
  (t/'key').write_text(os.environ['DEPLOY_SSH_KEY'].rstrip()+'\n')
  (t/'known').write_text(os.environ['DEPLOY_KNOWN_HOSTS'].rstrip()+'\n')
  config=f"Host infra-*\n IdentityFile {t/'key'}\n UserKnownHostsFile {t/'known'}\n StrictHostKeyChecking yes\n HostKeyAlgorithms ssh-ed25519\n IdentitiesOnly yes\n BatchMode yes\n ConnectTimeout 20\n ServerAliveInterval 15\n ForwardAgent no\nHost infra-gateway\n HostName 193.187.93.245\n User observability-deploy\n HostKeyAlias infra-gateway\nHost infra-target\n HostName 193.84.2.141\n User maxim\n HostKeyAlias infra-target\n"
  (t/'config').write_text(config)
  script=f"set -eu\ncd /home/maxim/projects/infra/redis\ntest ! -e .retired\ntest \"$(git rev-parse --show-toplevel)\" = \"$(pwd -P)\"\ntest \"$(git branch --show-current)\" = main\ntest -z \"$(git status --porcelain)\"\ngit fetch --quiet origin refs/heads/main\ntest \"$(git rev-parse FETCH_HEAD)\" = {sha}\ngit merge --ff-only {sha}\nsudo -n make deploy\n"
  subprocess.run(['ssh','-F',str(t/'config'),'infra-target','sh','-s'],input=script,text=True,check=True,timeout=600)
if __name__=='__main__':main()
