import os
from git import Repo
class Clone_Repo:
    def __init__(self,username,usertoken):
        self.username = username
        self.usertoken = usertoken
    def clone(self,github_url,local_dir):
        try:
            print(f"Cloning repository from {github_url} into {local_dir}...")
            repo_url = github_url.replace("https://", f"https://{self.username}:{self.usertoken}@")
            Repo.clone_from(repo_url,local_dir)
            print(f"Repository cloned successfully into {local_dir}")
        except Exception as e:
            print(f"Error cloning repository: {e}")


if __name__ == "__main__":
    user_name = "your_username"
    user_token = "your_token"
    CL = Clone_Repo(user_name,user_token)
    CL.clone("https://github.com/FFmpeg/FFmpeg.git","your_path")
