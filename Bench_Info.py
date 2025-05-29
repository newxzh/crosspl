import os
import csv
class Bench_Info():
    def __init__(self,File_path,Classfier,Classfier_ID,Interface_class,Interface_name,Usage_Process,Sava_path):
        self.File_path = File_path
        self.Classfier = Classfier
        self.Classfier_ID = Classfier_ID
        self.Interface_class = Interface_class
        self.Interface_name = Interface_name
        self.Usage_Process = Usage_Process
        self.Save_path = Sava_path


    def Info_Save (self):
        WriteHeader = False
        if os.path.exists (self.Save_path):
            WriteHeader = True
        with open(self.Save_path, 'a+', encoding='utf-8', newline='') as CsvFile:
            writer = csv.writer(CsvFile)
            if WriteHeader == False:
                Header = ["File_path","Classfier","Classfier_ID","Interface_class","Interface_name","Status_description"]
                writer.writerow(Header)
            Row = [self.File_path, self.Classfier,self.Classfier_ID,self.Interface_class, self.Interface_name,self.Usage_Process]
            writer.writerow(Row)
        return


if __name__ == "__main__":
    a = Bench_Info('D:\\CAE/Repository/foundation-sites_2573058\\.husky\\husky-commit-lint.js',"IMI",0,"JavaScript*","child_process",'[a,b,c]',"D:\CAE\Info.csv")
    a.Info_Save()


