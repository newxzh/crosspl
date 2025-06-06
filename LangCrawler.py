import os
from Crawler import Crawler
from Repository_Info import Repository_Info
class LangCrawler(Crawler):
    def __init__(self, FileName="RepositoryList.csv"):
        super(LangCrawler, self).__init__(FileName)

        #if os.path.exists (self.FileName):
            #os.rename (self.FileName, self.FileName+"-back.csv")

    def GrabProject (self):
        PageNum = 10
        Star    = self.MaxStar
        Delta   = self.Delta
        while Star > self.MinStar:
            if self.MaxGrabNum != -1 and len(self.RepoList) >= self.MaxGrabNum:
                break

            Bstar = Star - Delta
            Estar = Star
            if Bstar <= self.MinStar:
                Bstar = self.MinStar

            Star  = Star - Delta

            StarRange = str(Bstar) + ".." + str(Estar)
            for PageNo in range (1, PageNum+1):
                if self.MaxGrabNum != -1 and len(self.RepoList) >= self.MaxGrabNum:
                    break
                        
                print ("===>[Star]: ", StarRange, ", [Page] ", PageNo, end=", ")
                Result = self.GetRepoByStar (StarRange, PageNo)
                if 'items' not in Result:
                    break

                RepoList = Result['items']
                RepoSize = len (RepoList)       
                if RepoSize == 0:
                    print ("RepoList is Null")
                    break

                print ("RepoSize: %u" %RepoSize)
                
                for Repo in RepoList:
                    LangsDict = self.GetRepoLangs (Repo['languages_url'])
                    MainLang  = self.GetMainLang (LangsDict)
                    
                    LangsDict = self.LangValidate (LangsDict)
                    if LangsDict == None:
                        continue
                    
                    Langs = list(LangsDict.keys ())
                    # if len (Langs) == 0:

                    len_Langs = len(Langs)
                    if len_Langs< self.MinLangs or len_Langs > self.MaxLangs:
                        continue

                    print ("\t[%u][%u] --> %s" %(len(self.RepoList), Repo['id'], Repo['clone_url']))
                    RepoData = Repository_Info (Repo['id'], Repo['stargazers_count'], Langs, Repo['url'], Repo['clone_url'], Repo['topics'],
                                           Repo['description'], Repo['created_at'], Repo['pushed_at'])
                    RepoData.SetMainLang(MainLang)
                    RepoData.SetName(Repo['name'])
                    
                    self.RepoList[Repo['id']] = RepoData
                    self.AppendSave (RepoData)
                    
                    if self.MaxGrabNum != -1 and len(self.RepoList) >= self.MaxGrabNum:
                        break
