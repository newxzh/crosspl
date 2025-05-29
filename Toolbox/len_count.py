import pandas as pd
RepoList_path = "D:\CAE\RepositoryList.csv"
RepoData = pd.read_csv(RepoList_path, encoding='latin-1')
RepoData_name = RepoData["Name"].tolist()

print(len(RepoData_name))