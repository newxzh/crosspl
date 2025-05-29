import abc
import csv
import pandas as pd
from Config import Config
from Repository_Info import Repository_Info

csv.field_size_limit(2**31-1)
# The Analyzer is an abstract class that defines the extraction of some common content of the class (defines some abstract methods and some ordinary methods). An abstract class cannot be instantiated.
# If a subclass of an abstract class wants to be instantiated, it must also implement all the abstract methods in its abstract superclass.
class Analyzer(metaclass=abc.ABCMeta):

    Language_Combination_Limit = 20

    def __init__(self, FileName="Analyzer.csv"):
        self.FileName = FileName
        self.FilePath = Config.BaseDir
        self.AnalyzStats = {}
        self.RepoList = []
        #在初始化Analyzer的时候，LoadRepoList()就会被执行
        self.LoadRepoList ()
        
    @abc.abstractmethod
    def SaveData (self, FileName=None):
        print("Save data to csv file")

    def LoadRepoList (self, FileName="RepositoryList.csv"):
        FilePath = self.FilePath + '/' + FileName
        df = pd.read_csv(FilePath, encoding='latin-1')
        for index, row in df.iterrows():
            RepoData = Repository_Info (row['Id'], row['Star'], row['Langs'], row['ApiUrl'], row['CloneUrl'], row['Topics'],
                                   row['Descripe'], row['Created'], row['Pushed'])
            RepoData.SetName(row['Name'])
            # 向self.RepoList中添加Repository的实例化对象RepoData，这样就可以通过实例化对象直接调用对应的值或者函数
            self.RepoList.append (RepoData)

    @abc.abstractmethod
    def Obj2List (self, Value):
        return list(Value.__dict__.values())

    @abc.abstractmethod
    def Obj2Dict (self, Value):
        return Value.__dict__

    @abc.abstractmethod
    def GetHeader (self, Data):
        Headers = list(list(Data.values())[0].__dict__.keys())
        return [header.replace(" ", "_") for header in Headers]

    def AnalyzeData (self, RepoList):
        for Repo in RepoList:
            self.UpdateAnalysis (Repo)
        self.UpdateFinal ()

    @abc.abstractmethod
    def UpdateFinal (self):
        print("Abstract Method that is implemented by inheriting classes")

    @abc.abstractmethod
    def UpdateAnalysis(self, CurRepo):
        print("Abstract Method that is implemented by inheriting classes")

    def StartRun (self):
        self.AnalyzeData (self.RepoList)