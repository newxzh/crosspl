import os
class Config ():
    OriginCollect= "OriginData"
    OriginStat   = "StatData"
    BaseDir      = os.getcwd()
    CollectDir   = OriginCollect
    StatisticDir = OriginStat
    Version      = "None"
    CFG_Type = ['int', 'str', 'list']
    def __init__(self, CfgFile='config.ini'):
        self.CfgFile = CfgFile
        self.CFG = {}
        self.CFG['UserName']   = 'str'
        self.CFG['Token']      = 'str'
        self.CFG['TaskNum']    = 'int'
        self.CFG['Languages']  = 'list'
        self.CFG['Domains']    = 'list'
        self.CFG['MaxGrabNum'] = 'int'
        self.CFG['LangConsistCheck'] = 'int'
        self.CFG['MinStar'] = 'int'
        self.CFG['MinLangs'] = 'int'
        self.CFG['MaxLangs'] = 'int'
    def Get (self, Key):
        return self.CFG[Key]
    def LoadCfg (self):
        CfgPath = Config.BaseDir +"\\"+ self.CfgFile
        with open (CfgPath, "r") as CF:
            AllLines = CF.readlines ()
            for Line in AllLines:
                Line = Line.replace ('\n', '')
                if Line.find (':') == -1 or Line.find ('#') != -1:
                    continue
                Key, Content = Line.split (':')
                Type = self.CFG.get (Key)
                if Type == 'int':
                    self.CFG[Key] = int (Content)
                elif Type == 'str':
                    self.CFG[Key] = Content
                elif Type == 'list':
                    CList = list (Content.split (' '))
                    self.CFG[Key] = [item for item in CList if item != '']
                else:
                    continue
    @staticmethod
    def IsExist (file):
        isExists = os.path.exists(file)
        if (not isExists):
            return False
        fsize = os.path.getsize(file)/1024
        if (fsize == 0):
            return False
        return True
    @staticmethod
    def MakeDir (path):
        path=path.strip()
        path=path.rstrip("\\")
        isExists=os.path.exists(path)
        if not isExists:
            os.makedirs(path)