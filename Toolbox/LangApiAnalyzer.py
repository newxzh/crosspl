import os
import re
import csv
import copy
from Analyzer import Analyzer
from Config import Config
from code_preprocess import skip_note
from Bench_Info import Bench_Info
LANG_API_FFI = "FFI"
LANG_API_IRI = "IMI"  # Indirect remote-invocation
# LANG_API_ID  = "EBD"  #inter-dependence
class State ():
    def __init__(self, id, signature,description = " "):
        self.id = id
        self.signature = signature
        self.next = []
        self.description = description
    def AddNext (self, next):
        self.next.append (next)

    def Match (self, String):
        if len (self.signature) == 0:
            return True,self.signature,self.description
        if re.search(self.signature, String) != None: # If self.signature matches part of a key string in String, return True.
            return True,self.signature,self.description
        else:
            return False,self.signature,self.description

#定义了一系列Api分类器
class ApiClassifier ():
    def __init__(self, name, clstype, fileType, interface_name):
        self.name     = name
        self.clstype  = clstype
        self.filetype = fileType.split()
        self.States = [] # States stores the instantiated states, with properties including id, next , signature , as well as the AddNext method and the Match method.
        self.interface_name = interface_name

    def AddState (self, state):
        self.States.append (state)
    def Match (self, File):
        MatchList_file = []
        state_desc_list = []
        sig_list = []
        flag = 0
        if not os.path.exists (File):
            return False,MatchList_file,sig_list,state_desc_list
        Ext = os.path.splitext(File)[-1].lower()
        if "*" not in self.filetype and Ext not in self.filetype:
            return False,MatchList_file,sig_list,state_desc_list
        StateStack = copy.deepcopy(self.States)
        if len (StateStack) == 0:
            return False,MatchList_file,sig_list,state_desc_list
        with open (File, "r", encoding="utf-8", errors="ignore") as sf:
            for line in sf:
                line = line.strip()
                if len(line) == 0:
                    continue
                if line.startswith("/*") or line.endswith("*/"):
                    flag += 1
                if line.startswith("'''") or line.endswith("'''"):
                    flag += 1
                if line.startswith('"""') or line.endswith('"""'):
                    flag += 1
                if line.startswith("<!--") or line.endswith("-->"):
                    flag += 1
                if skip_note(line, Ext, flag):
                    continue
                for state in StateStack:
                    isMatch,signature,state_description = state.Match(line)
                    if signature not in sig_list:
                        sig_list.append(signature)
                        state_desc_list.append(state_description)
                    if isMatch == False:
                        continue
                    if File not in MatchList_file:
                        MatchList_file.append(File)
                    if len (state.next) == 0: # 确保满足状态转移的要求
                        # MatchList_file => 返回与状态机匹配的文件
                        return True,MatchList_file,sig_list,state_desc_list
                    for next in state.next:
                        if next not in StateStack:
                            StateStack.append (next)
        return False,MatchList_file,sig_list,state_desc_list


class LangApiAnalyzer (Analyzer):
    def __init__(self, FileName='ApiSniffer'):
        super(LangApiAnalyzer, self).__init__(FileName=FileName)
        self.FilePath = Config.BaseDir + '/'
        # self.Index = 0
        self.FFIClfList = []
        self.IRIClfList = []
        self.Langs = {}
        self.TopLanguages = {"c":".c", "c++":".cpp .cc", "c#":".cs", "java":".java", "javascript":".js", "typescript":".ts", 
                             "python":".py", "html":".html", "php":".php", "go":".go", "ruby":".rb", "objective-c":".m .mm", 
                             "css":".css", "assembly":".as", "kotlin":".kt", "swift":".swift","rust":".rs", "perl":".pl", "r":".r", "scala":".scala", "dart":".dart"}
        # Init FFI classifier
        self.InitFfiClass ()
        # Init IRI classifier
        self.InitIriClass ()

        # Default file
        Header = ['id', 'languages', 'classifier', 'clfType', 'fileType']
        SfFile = self.FilePath + 'ApiSniffer.csv'
        with open(SfFile, 'w', encoding='utf-8', newline='') as CsvFile:
            writer = csv.writer(CsvFile)
            writer.writerow(Header)

    def UpdateFinal(self):
        self.SaveData ()
    def UpdateAnalysis(self, Repo):
        ReppId  = Repo.Id
        ReppName = Repo.Name
        RepoDir = "D:\\CAE\\Splited_Repository" + "\\1\\" + f"{ReppName}_{ReppId}"
        if not os.path.exists (RepoDir):
            return
        TopLangs = self.TopLanguages.keys()
        Langs = [lang for lang in Repo.Langs if lang in TopLangs]
        # print ("Scan ", RepoDir, Langs)
        self.Sniffer(ReppId, Langs, RepoDir)

    def SnifferByFFI (self, File):
        Classfier_ID = 0
        for Clf in self.FFIClfList:
            IsMatch,Matched_files,signature,state_description = Clf.Match (File)
            if IsMatch == True:
                bench_info = Bench_Info(Matched_files[0], "Foreign Function Interface(FFI)",Classfier_ID, Clf.name,Clf.interface_name, state_description,"D:\CAE\Repo_Info\Info_FFI_desktop.csv")
                bench_info.Info_Save()
                print("==================================================================")
                print(f"The Matched file path: {Matched_files}")
                print(f"Name of class: {Clf.name}")
                print(f"Class type: {Clf.interface_name}")
                print(f"Class type: {Clf.clstype}")
                print(f"Matched with: {signature}")
                print(" ")
                return Clf
            Classfier_ID += 1
        return None

    def SnifferByIri (self, Langs, File):
        Classfier_ID = 51
        Fext = os.path.splitext(File)[-1].lower()
        IsFiltered = True
        for lang in Langs:
            Ext = self.TopLanguages [lang].split ()
            if Fext in Ext:
                IsFiltered = False
                break
        if IsFiltered == True:
            return None
        for Clf in self.IRIClfList:
            IsMatch,Matched_files,signature,state_description = Clf.Match (File)
            if IsMatch == True:
                print(Matched_files[0])
                bench_info = Bench_Info(Matched_files[0], "Inter-Process Communication (IPC)",Classfier_ID, Clf.name,Clf.interface_name, state_description,"D:\CAE\Repo_Info\Info_IRI_desktop.csv")
                bench_info.Info_Save()
                print("==================================================================")
                print(f"The Matched file path: {Matched_files}")
                print(f"Name of class: {Clf.name}")
                print(f"Class type: {Clf.interface_name}")
                print(f"Class type: {Clf.clstype}")
                print(f"Matched with: {signature}")
                print(" ")
                return Clf
            Classfier_ID += 1
        return None

    def AddScanResult (self, ClfList, Clf):
        for C in ClfList:
            if C.name == Clf.name:
                return
        ClfList.append (Clf)

    def Sniffer (self, ReppId, Langs, Dir):
        if len (Langs) <= 1:
            return None

        ClfList = []
        self.Langs [ReppId] = Langs
        
        # # 1. FFI Scan
        # RepoDirs = os.walk(Dir)
        # for Path, Dirs, Fs in RepoDirs: # Traverse all files under the project directory: Dirs -> all folders in RepoDirs, Fs -> all files under RepoDirs.
        #     for f in Fs:
        #         File = os.path.join(Path, f)
        #         if os.path.exists(File):
        #             Clf = self.SnifferByFFI (File)
        #             if Clf != None:
        #                 self.AddScanResult (ClfList, Clf)
        #         else:
        #             continue
        # if (len (ClfList) >= len(Langs)-1):
        #     self.AnalyzStats [ReppId] = ClfList
        #     return

        # 2. IRI Scan      
        RepoDirs = os.walk(Dir)
        for Path, Dirs, Fs in RepoDirs:
            for f in Fs:
                File = os.path.join(Path, f)
                if os.path.exists(File):
                    Clf = self.SnifferByIri (Langs, File)
                    if Clf != None:
                        self.AddScanResult (ClfList, Clf)
                else:
                    continue
        if (len (ClfList) >= 3 or len (ClfList) >= len(Langs)-1):
            self.AnalyzStats [ReppId] = ClfList
            return
    def FormatTypes (self, TypeList):
        Types = ""
        TypeOrder = [LANG_API_FFI, LANG_API_IRI]
        for type in TypeOrder:
            if type not in TypeList:
                continue
            if Types == "":
                Types = type
            else:
                Types += "_" + type
        return Types
    # 将处理完的结果进行保存
    def SaveData (self,FileName=None):
        if (len(self.AnalyzStats) == 0):
            return
        SfFile = self.FilePath + self.FileName + '.csv' # 数据保存的路径
        with open(SfFile, 'a', encoding='utf-8', newline='') as CsvFile:
            writer = csv.writer(CsvFile)
            # self.AnalyzStats.items() -> 获取self.AnalyzStats的所有key-value对,此处的Id值得是Key，ClfList指的是value
            for Id, ClfList in self.AnalyzStats.items():
                Names = []
                Types = []
                FileTypes = []
                for clf in ClfList:
                    Names.append (clf.name)
                    Types.append (clf.clstype)
                    FileTypes += clf.filetype
                Names = "_".join(list(set (Names)))
                Types = self.FormatTypes(list(set (Types)))
                row = [Id, self.Langs [Id], Names, Types, FileTypes]
                if len(FileTypes) != 0:
                    writer.writerow(row)
        self.AnalyzStats = {}
             
    def Obj2List (self, value):
        return super(LangApiAnalyzer, self).Obj2List (value)

    def Obj2Dict (self, value):
        return super(LangApiAnalyzer, self).Obj2Dict (value)
    
    def GetHeader (self, data):
        return super(LangApiAnalyzer, self).GetHeader (data)

    def InitIriClass (self):
        ############################################################
        # Class: Java*
        ############################################################
        # # FSM 1: Recognizing Java ServerSocket Server-side
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "java.net ServerSocket")
        # S0 = State(0, "import java.net.*|import java.net.ServerSocket|import java.net.Socket","Step 1: Import necessary networking classes for creating a TCP server")
        # S1 = State(1, "new ServerSocket","Step 2: Create a ServerSocket instance to listen for incoming client connections")
        # S2 = State(2, "accept", "Step 3: Accept an incoming connection request")
        # S3 = State(3, "getInputStream|getOutputStream","Step 4: Obtain input and output streams to send and receive data between server and client")
        # S4 = State(4, "close", "Step 5: Close the Socket and release resources after communication is complete")
        # # State transitions for the FSM
        # S0.AddNext(S1)
        # S1.AddNext(S2)
        # S2.AddNext(S3)
        # S3.AddNext(S4)
        # # Add state to the server classifier
        # Class.AddState(S0)
        # self.IRIClfList.append(Class)
        #
        # # FSM 2: Recognizing Java Socket Client-side
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "java.net Socket")
        # S5 = State(5, "import java.net.*|import java.net.Socket","Step 1: Import necessary networking classes for creating a TCP client")
        # S6 = State(6, "new Socket", "Step 2: Create a Socket instance to establish a connection with the server")
        # S7 = State(7, "connect", "Step 3: Initiate a connection request to the server using the Socket instance")
        # S8 = State(8, "getInputStream|getOutputStream","Step 4: Obtain input and output streams to send and receive data between client and servers")
        # S9 = State(9, "close()", "Step 5: Close the Socket and release resources after communication is complete")
        # # State transitions for the FSM
        # S5.AddNext(S6)
        # S6.AddNext(S7)
        # S7.AddNext(S8)
        # S8.AddNext(S9)
        # # Add state to the client classifier
        # Class.AddState(S5)
        # self.IRIClfList.append(Class)
        #
        # # FSM 3: Recognizing Java using java.net UDP Server-side or Client-side
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "java.net UDP Server or Client")
        # S10 = State(10,
        #             "import java.net.*|import java.net.DatagramPacket|import java.net.DatagramSocket|import java.net.InetAddress",
        #             "Step 1: Import Java networking classes required for UDP communication, including DatagramSocket for handling UDP sockets, DatagramPacket for sending/receiving packets, and InetAddress for managing IP addresses.")
        # S11 = State(11, "new DatagramSocket",
        #             "Step 2: Create a DatagramSocket instance. On the server-side, bind it to a specific port to listen for incoming packets. On the client-side, use it to send data.")
        # S12 = State(12, "new DatagramPacket",
        #             "Step 3: Create a DatagramPacket instance. For receiving, allocate a buffer to store incoming data. For sending, specify the target IP address and port.")
        # S13 = State(13, "receive|getData|getLength|getOffset|parseData|processData|send",
        #             "Step 4: Handle UDP packet transmission. The server calls receive() to wait for incoming packets, extracts data using getData(), and processes it. The client sends data using send().")
        # S10.AddNext(S11)
        # S11.AddNext(S12)
        # S12.AddNext(S13)
        # Class.AddState(S10)
        # self.IRIClfList.append(Class)
        #
        # # # FSM 4: Recognizing Java using Netty TCP Client
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Java Netty TCP Client")
        # S14 = State(14,
        #             "import io.netty.bootstrap.Bootstrap|import io.netty.channel.*|import io.netty.channel.nio.NioEventLoopGroup|import io.netty.channel.socket.nio.NioSocketChannel",
        #             "Step 1: Import Netty libraries, including Bootstrap for client initialization, EventLoopGroup for managing event-driven I/O, Channel for network communication, and NioSocketChannel for handling non-blocking TCP connections.")
        # S15 = State(15, "new NioEventLoopGroup()|new Bootstrap()",
        #             "Step 2: Initialize an instance of NioEventLoopGroup to manage client-side I/O threads and create a Bootstrap instance to configure Netty's TCP client behavior.")
        # S16 = State(16, "NioSocketChannel",
        #             "Step 3: Set the Bootstrap's channel type to NioSocketChannel, enabling non-blocking TCP connections and defining a ChannelInitializer to configure the client pipeline.")
        # S17 = State(17, "connect",
        #             "Step 4: Establish a connection to the remote server using Bootstrap.connect(), and configure the client pipeline with encoders, decoders, and custom handlers for message processing.")
        # S18 = State(18, "closeFuture()|shutdownGracefully",
        #             "Step 5: Wait for the client connection to close using closeFuture(), then call shutdownGracefully() on EventLoopGroup to release resources and ensure a graceful shutdown.")
        #
        # # Define state transitions for FSM
        # S14.AddNext(S15)
        # S15.AddNext(S16)
        # S16.AddNext(S17)
        # S17.AddNext(S18)
        # # Add states to the classifier
        # Class.AddState(S14)
        # self.IRIClfList.append(Class)
        #
        # # FSM 5: Java Netty TCP Server-side
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Java Netty TCP Server")
        # S14 = State(14,
        #             "import io.netty.bootstrap.ServerBootstrap|import io.netty.channel.*|import io.netty.channel.nio.NioEventLoopGroup|import io.netty.channel.socket.nio.NioServerSocketChannel",
        #             "Step 1: Import Netty's server-related classes, including ServerBootstrap for server setup, EventLoopGroup for managing I/O threads, Channel for TCP communication, and NioServerSocketChannel for non-blocking server transport.")
        # S15 = State(15, "new NioEventLoopGroup()|new ServerBootstrap()",
        #             "Step 2: Instantiate NioEventLoopGroup to handle server-side event loops and create a ServerBootstrap instance to configure the server’s behavior.")
        # S16 = State(16, "NioServerSocketChannel",
        #             "Step 3: Configure the ServerBootstrap to use NioServerSocketChannel for handling incoming TCP connections and set up the pipeline with appropriate handlers for request processing.")
        # S17 = State(17, "bind",
        #             "Step 4: Bind the server to a specific host and port using ServerBootstrap.bind(), allowing it to listen for and accept incoming client connections.")
        # S18 = State(18, "closeFuture()|shutdownGracefully()",
        #             "Step 5: Keep the server running by synchronizing on closeFuture(), and call shutdownGracefully() on EventLoopGroup during shutdown to release all associated resources.")
        #
        # # Define state transitions
        # S14.AddNext(S15)
        # S15.AddNext(S16)
        # S16.AddNext(S17)
        # S17.AddNext(S18)
        #
        # # Add states to the classifier
        # Class.AddState(S14)
        # self.IRIClfList.append(Class)
        #
        # # FSM 6: Java Netty UDP Client-side or Server-side
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Java Netty UDP Client or Server")
        # S19 = State(19,
        #             "import io.netty.bootstrap.Bootstrap|import io.netty.channel.*|import io.netty.channel.nio.NioEventLoopGroup|import io.netty.channel.socket.nio.NioDatagramChannel",
        #             "Step 1: Import Netty libraries required for UDP communication, including Bootstrap for client/server setup, NioEventLoopGroup for managing event-driven I/O, Channel for UDP data handling, and NioDatagramChannel for non-blocking datagram transport.")
        # S20 = State(20, "NioEventLoopGroup|new Bootstrap()",
        #             "Step 2: Create a NioEventLoopGroup to handle I/O operations asynchronously and initialize a Bootstrap instance to configure the Netty UDP client or server.")
        # S21 = State(21, "NioDatagramChannel",
        #             "Step 3: Configure the Bootstrap with NioDatagramChannel for UDP transport, apply necessary channel options such as SO_BROADCAST, and initialize a ChannelPipeline with relevant handlers like SimpleChannelInboundHandler.")
        # S22 = State(22, "bind",
        #             "Step 4: Bind the DatagramChannel to a local port, enabling the UDP socket to send and receive datagrams from remote hosts.")
        # S23 = State(23, "closeFuture()|shutdownGracefully",
        #             "Step 5: Monitor closeFuture() to detect when the channel is closed, then release resources gracefully using shutdownGracefully() to prevent memory leaks.")
        #
        # # Define state transitions
        # S19.AddNext(S20)
        # S20.AddNext(S21)
        # S21.AddNext(S22)
        # S22.AddNext(S23)
        #
        # # Add states to the classifier
        # Class.AddState(S19)
        # self.IRIClfList.append(Class)
        #
        # # FSM 7: Recognizing the TCP Client-side based on Java.nio
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "TCP Client-side based on java.nio")
        # S24 = State(24, "import java.nio.*|import java.nio.channels.*|import java.net.*",
        #             "Step 1: Import necessary NIO classes, including networking classes")
        # S25 = State(25, "SocketChannel.open|configureBlocking(false)|Selector.open()|register",
        #             "Step 2: Initialize SocketChannel, set non-blocking mode, open Selector, and register the channel")
        # S26 = State(26, "connect", "Step 3: Establish a connection to the server using SocketChannel")
        # S27 = State(27,
        #             "capacity|clear|put|flip|write|read|compact|order|getInt|putInt|getFloat|putFloat|duplicate|slice|asReadOnlyBuffer|position|limit|mark|reset",
        #             "Step 4: Perform buffer operations such as writing, reading, flipping, compacting, and managing memory")
        # S28 = State(28, "close()", "Step 5: Close the SocketChannel and release resources")
        # # Define state transitions
        # S24.AddNext(S25)
        # S25.AddNext(S26)
        # S26.AddNext(S27)
        # S27.AddNext(S28)
        #
        # # Add the state machine to the classifier
        # Class.AddState(S24)
        # self.IRIClfList.append(Class)
        #
        # # FSM 8: Recognizing the TCP Server-side based on Java.nio
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "TCP Server-side based on java.nio")
        # S29 = State(29, "import java.nio.*|import java.nio.channels.*",
        #             "Step 1: Import necessary NIO classes, including channels and buffers for server-side operations")
        # S30 = State(30,
        #             "ServerSocketChannel.open|configureBlocking(false)|serverSocketChannel.socket()|bind|Selector.open()",
        #             "Step 2: Create a ServerSocketChannel, configure it as non-blocking, bind to a port, and initialize a Selector for handling multiple connections")
        # S31 = State(31, "accept", "Step 3: Accept client connections from the ServerSocketChannel")
        # S32 = State(32,
        #             "capacity|clear|put|flip|write|read|compact|order|getInt|putInt|getFloat|putFloat|duplicate|slice|asReadOnlyBuffer|position|limit|mark|reset",
        #             "Step 4: Use ByteBuffer to perform data operations such as writing, reading, flipping, compacting, and managing memory")
        # S33 = State(33, "close()", "Step 5: Close the ServerSocketChannel and release all associated resources")
        # # Define state transitions
        # S29.AddNext(S30)
        # S30.AddNext(S31)
        # S31.AddNext(S32)
        # S32.AddNext(S33)
        # # Add the state machine to the classifier
        # Class.AddState(S29)
        # self.IRIClfList.append(Class)
        #
        # # FSM 9: Recognizing the UDP Client-side based on Java.nio
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "UDP sender based on java.nio")
        #
        # S34 = State(34, "import java.nio.*|import java.nio.channels.*",
        #             "Step 1: Import necessary Java NIO classes for non-blocking UDP communication, including DatagramChannel and ByteBuffer.")
        # S35 = State(35, "DatagramChannel.open|configureBlocking(false)",
        #             "Step 2: Open a DatagramChannel for UDP communication, configure it as non-blocking to allow asynchronous operations.")
        # S36 = State(36, "send",
        #             "Step 3: Create a ByteBuffer to store the outgoing message, set the target address using InetSocketAddress, and use send() to transmit the data.")
        # S37 = State(37, "clear|close()",
        #             "Step 4: Clear the ByteBuffer to prepare for new data and close the DatagramChannel to release resources.")
        #
        # S34.AddNext(S35)
        # S35.AddNext(S36)
        # S36.AddNext(S37)
        #
        # Class.AddState(S34)
        # self.IRIClfList.append(Class)
        #
        # # FSM 10: Recognizing the UDP Server-side based on Java.nio
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "UDP receiver based on java.nio")
        #
        # S38 = State(38, "import java.nio.*|import java.nio.channels.*",
        #             "Step 1: Import necessary Java NIO classes for UDP communication, including DatagramChannel and ByteBuffer.")
        # S39 = State(39, "DatagramChannel.open|configureBlocking(false)",
        #             "Step 2: Open a DatagramChannel, configure it as non-blocking, bind it to a local address, and optionally register it with a Selector for event-driven handling.")
        # S40 = State(40, "bind",
        #             "Step 3: Bind the DatagramChannel to a specific port to start listening for incoming UDP packets.")
        # S41 = State(41, "receive",
        #             "Step 4: Create a ByteBuffer, call receive() to store incoming packets, and process the received data.")
        # S42 = State(42, "close()",
        #             "Step 5: Close the DatagramChannel to free up resources after communication is complete.")
        # S38.AddNext(S39)
        # S39.AddNext(S40)
        # S40.AddNext(S41)
        # S41.AddNext(S42)
        #
        # Class.AddState(S38)
        # self.IRIClfList.append(Class)
        #
        # # FSM 11: Recognizing FileChannel usage in Java.nio
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "FileChannel usage in java.nio")
        # S43 = State(43, "import java.nio.*|import java.nio.channels.*|import java.nio.file.*",
        #             "Step 1: Import necessary Java NIO classes, including FileChannel and Buffer classes such as ByteBuffer and MappedByteBuffer")
        # S44 = State(44, "FileChannel.open|StandardOpenOption",
        #             "Step 2: Open a FileChannel using FileChannel.open() with appropriate StandardOpenOption flags like READ, WRITE, APPEND, etc., for file operations")
        # S45 = State(45, "read|write|position|truncate|size|force|map|transferTo|transferFrom",
        #             "Step 3: Perform file operations such as reading and writing to a file, modifying position, truncating file, transferring data, and mapping files into memory")
        # S46 = State(46,
        #             "clear()|flip()|put()|get()|compact()|duplicate()|slice()|asReadOnlyBuffer()|mark()|reset()|order()|force()|isDirect()|allocateDirect()",
        #             "Step 4: Perform various operations on ByteBuffer, DirectByteBuffer, and MappedByteBuffer. This includes clearing, flipping, putting, getting, and other memory management tasks. For MappedByteBuffer, force writes changes to disk.")
        # S47 = State(47, "close",
        #             "Step 5: Close the FileChannel to release system resources and finalize the file operations")
        # # Define state transitions
        # S43.AddNext(S44)
        # S44.AddNext(S45)
        # S45.AddNext(S46)
        # S46.AddNext(S47)
        # # Add the state machine to the classifier
        # Class.AddState(S43)
        # self.IRIClfList.append(Class)
        #
        # # FSM 12: Recognizing the TCP Client based on Apache MINA
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "TCP Client based on Apache MINA in java")
        # S48 = State(48,
        #             "import org.apache.mina.core.session.IoSession|import org.apache.mina.filter.codec.*|import org.apache.mina.transport.socket.nio.NioSocketConnector|import org.apache.mina.core.service",
        #             "Step 1: Import necessary Apache MINA classes, including IoSession, NioSocketConnector, and various filters for the connection.")
        # S49 = State(49, "new NioSocketConnector()",
        #             "Step 2: Create a NioSocketConnector, which is responsible for managing the client-side connection to the server.")
        # S50 = State(50,
        #             "setHandler|IoHandler|IoHandlerAdapter|getFilterChain()|LoggingFilter|SSLFilter|ProtocolCodecFilter|CompressionFilter|BlackListFilter|WhiteListFilter|ExecutorFilter|TrafficShapingFilter",
        #             "Step 4: Set the IoHandler for handling events such as read, write, and exception processing for the session.")
        # S51 = State(51, "connect|getSession()|awaitUninterruptibly",
        #             "Step 5: Initiate the connection to the server, obtain the session and wait for the connection to be established.")
        # S52 = State(52, "write|getServiceAddress|send|flush|isConnected|setAttribute|setIdleTime",
        #             "Step 6: Perform various operations on the session such as writing data, sending messages, checking connection status, and setting attributes and idle time.")
        # S53 = State(53, "dispose|getCloseFuture|awaitUninterruptibly",
        #             "Step 7: Dispose of the connection, wait for it to close, and release resources associated with the session.")
        # S48.AddNext(S49)
        # S49.AddNext(S50)
        # S50.AddNext(S51)
        # S51.AddNext(S52)
        # S52.AddNext(S53)
        # Class.AddState(S48)
        # self.IRIClfList.append(Class)
        #
        # # FSM 13: Recognizing the TCP Server based on Apache MINA
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "TCP Server based on Apache MINA in java")
        # S54 = State(54,
        #             "import org.apache.mina.core.session.IoSession|import org.apache.mina.filter.codec.*|import org.apache.mina.transport.socket.nio.NioSocketAcceptor|import org.apache.mina.core.service",
        #             "Step 1: Import necessary Apache MINA classes")
        # S55 = State(55, "new NioSocketAcceptor()", "Step 2: Create a NioSocketAcceptor")
        # S56 = State(56,
        #             "getFilterChain()|LoggingFilter|SSLFilter|ProtocolCodecFilter|CompressionFilter|BlackListFilter|WhiteListFilter|ExecutorFilter|TrafficShapingFilter",
        #             "Step 3: Configure filter chain")
        # S57 = State(57, "setHandler|IoHandler|IoHandlerAdapter", "Step 4: Set the handler")
        # S58 = State(58, "bind", "Step 5: Bind to a port and start the server")
        #
        # S54.AddNext(S55)
        # S55.AddNext(S56)
        # S56.AddNext(S57)
        # S57.AddNext(S58)
        # Class.AddState(S54)
        # self.IRIClfList.append(Class)
        #
        # # FSM 14: Recognizing Vert.x TCP Client
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Vert.x TCP Client in Java")
        # S59 = State(59,
        #             "import io.vertx.core.AbstractVerticle|import io.vertx.core.Vertx|import io.vertx.core.buffer.Buffer|import io.vertx.core.net.NetClient|import io.vertx.core.net.NetClientOptions|import io.vertx.core.net.NetSocket",
        #             "Step 1: Import necessary Vert.x classes for TCP client, including NetClient for handling connections and NetClientOptions for configuration.")
        # S60 = State(60, "new NetClientOptions()",
        #             "Step 2: Initialize NetClientOptions to configure TCP client settings, such as reconnect attempts, SSL, and timeouts.")
        # S61 = State(61, "vertx.createNetClient()",
        #             "Step 3: Create a NetClient instance, which will be used to establish a TCP connection with the server.")
        # S62 = State(62, "connect",
        #             "Step 4: Connect to the server by specifying the target host and port, and obtain a NetSocket instance upon a successful connection.")
        # S63 = State(63, "write|sendFile",
        #             "Step 5: Use NetSocket to write data to the server or send files over the TCP connection.")
        # S59.AddNext(S60)
        # S60.AddNext(S61)
        # S61.AddNext(S62)
        # S62.AddNext(S63)
        # Class.AddState(S59)
        # self.IRIClfList.append(Class)
        #
        # # FSM 15: Recognizing Vert.x TCP Server
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Vert.x TCP Server in Java")
        # S64 = State(64,
        #             "import io.vertx.core.AbstractVerticle|import io.vertx.core.Vertx|import io.vertx.core.buffer.Buffer|import io.vertx.core.net.NetServer|import io.vertx.core.net.NetServerOptions",
        #             "Step 1: Import necessary Vert.x classes for TCP server, including NetServer for handling incoming connections and NetServerOptions for configuration.")
        # S65 = State(65, "new NetServerOptions()",
        #             "Step 2: Initialize NetServerOptions to configure server settings such as port, host, SSL, and connection timeout.")
        # S66 = State(66, "createNetServer()",
        #             "Step 3: Create a NetServer instance using Vert.x, allowing it to accept and manage multiple TCP client connections.")
        # S67 = State(67, "connectHandler",
        #             "Step 4: Define a connection handler function that will be triggered when a new client connects to the server, providing a NetSocket instance to manage communication.")
        # S68 = State(68, "write|sendFile",
        #             "Step 5: Use the NetSocket instance to process incoming data from clients, send responses, or transfer files over the TCP connection.")
        # S64.AddNext(S65)
        # S65.AddNext(S66)
        # S66.AddNext(S67)
        # S67.AddNext(S68)
        # Class.AddState(S64)
        # self.IRIClfList.append(Class)
        #
        # # FSM 16: Recognizing Vert.x UDP sender
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Vert.x UDP sender in Java")
        # S69 = State(69,
        #             "import io.vertx.core.AbstractVerticle|import io.vertx.core.Vertx|import io.vertx.core.buffer.Buffer|import io.vertx.core.net.DatagramSocket|import io.vertx.core.net.DatagramSocketOptions",
        #             "Step 1: Import necessary Vert.x classes for UDP communication, including DatagramSocket for sending and receiving packets and DatagramSocketOptions for socket configuration.")
        # S70 = State(70, "vertx.createDatagramSocket()",
        #             "Step 2: Create a DatagramSocket instance using Vert.x, enabling UDP communication with optional configuration via DatagramSocketOptions.")
        # S71 = State(71, "send",
        #             "Step 3: Send a UDP packet using send(), specifying the target address, port, and data buffer. Optionally, define handlers to track send success or failure.")
        # S69.AddNext(S70)
        # S70.AddNext(S71)
        # Class.AddState(S69)
        # self.IRIClfList.append(Class)
        #
        # # FSM 17: Recognizing Vert.x UDP receiver
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Vert.x UDP receiver in Java")
        # S72 = State(72,
        #             "import io.vertx.core.AbstractVerticle|import io.vertx.core.Vertx|import io.vertx.core.buffer.Buffer|import io.vertx.core.net.DatagramSocket|import io.vertx.core.net.DatagramSocketOptions",
        #             "Step 1: Import necessary Vert.x classes for UDP reception, including DatagramSocket for receiving datagrams and DatagramSocketOptions for socket configuration.")
        # S73 = State(73, "vertx.createDatagramSocket()",
        #             "Step 2: Create a DatagramSocket instance with Vert.x, configuring it using DatagramSocketOptions if necessary.")
        # S74 = State(74, "listen",
        #             "Step 3: Bind the DatagramSocket to a specific port using listen(), enabling it to receive incoming UDP packets.")
        # S75 = State(75, "handler",
        #             "Step 4: Set a handler function to process received UDP packets, extracting and handling data using the provided Buffer object.")
        # S72.AddNext(S73)
        # S73.AddNext(S74)
        # S74.AddNext(S75)
        # Class.AddState(S72)
        # self.IRIClfList.append(Class)
        #
        # # FSM 18: Recognizing TCP Client-side based on Java.io
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "TCP Client-side Java.io")
        # S76 = State(76, "import java.io.*|import java.net.*",
        #             "Step 1: Import necessary Java IO and networking classes")
        # S77 = State(77, "new Socket()", "Step 2: Create a new Socket to connect to the server")
        # S78 = State(78, "getOutputStream()|getInputStream()|BufferedReader|BufferedWriter",
        #             "Step 3: Create writers and readers for data exchange, get input and output streams")
        # S79 = State(79, "read|readLine|write|flush|nextLine|next", "Step 5: Read data or send data to the server")
        # S80 = State(80, "close()", "Step 7: Close the connection")
        #
        # S76.AddNext(S77)
        # S77.AddNext(S78)
        # S78.AddNext(S79)
        # S79.AddNext(S80)
        # Class.AddState(S76)
        # self.IRIClfList.append(Class)
        #
        # # FSM 19: Recognizing TCP Server-side based on Java.io
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "TCP Server-side based on Java.io")
        # S81 = State(81, "import java.io.*|import java.net.*",
        #             "Step 1: Import necessary Java IO and networking classes")
        # S82 = State(82, "new ServerSocket()", "Step 2: Create a ServerSocket to listen for client connections")
        # S83 = State(83, "accept()", "Step 3: Accept a client connection")
        # S84 = State(84, "getOutputStream()|getInputStream()|BufferedReader|BufferedWriter",
        #             "Step 3: Create writers and readers for data exchange, get input and output streams")
        # S85 = State(85, "read|readLine|write|flush|nextLine|next", "Step 5: Read data or send data to the client")
        # S86 = State(86, "close()", "Step 6: Close the connection")
        #
        # S81.AddNext(S82)
        # S82.AddNext(S83)
        # S83.AddNext(S84)
        # S84.AddNext(S85)
        # S85.AddNext(S86)
        # Class.AddState(S81)
        # self.IRIClfList.append(Class)
        #
        # # FSM 20: Recognizing UDP send data based on Java.io
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "UDP Client-side based on Java.io")
        # S87 = State(87, "import java.io.*|import java.net.*",
        #             "Step 1: Import necessary Java IO and networking classes")
        # S88 = State(88, "new DatagramSocket()", "Step 2: Create a new DatagramSocket for communication")
        # S89 = State(89, "DatagramPacket", "Step 3: Prepare the data packet to send")
        # S90 = State(90, "send()", "Step 4: Send data using DatagramSocket")
        # S91 = State(91, "close()", "Step 6: Close the DatagramSocket")
        #
        # S87.AddNext(S88)
        # S88.AddNext(S89)
        # S89.AddNext(S90)
        # S90.AddNext(S91)
        # Class.AddState(S87)
        # self.IRIClfList.append(Class)
        #
        # # FSM 21: Recognizing UDP recieve data based on Java.io
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "UDP Server-side based on Java.io")
        # S92 = State(92, "import java.io.*|import java.net.*",
        #             "Step 1: Import necessary Java IO and networking classes")
        # S93 = State(93, "new DatagramSocket", "Step 2: Create a DatagramSocket and bind to a port")
        # S94 = State(94, "DatagramPacket", "Step 3: Create a DatagramPacket to receive data")
        # S95 = State(95, "receive()", "Step 4: Receive data from a client")
        # S96 = State(96, "close()", "Step 6: Close the DatagramSocket")
        #
        # S92.AddNext(S93)
        # S93.AddNext(S94)
        # S94.AddNext(S95)
        # S95.AddNext(S96)
        # Class.AddState(S92)
        # self.IRIClfList.append(Class)
        #
        # # FSM 22: Recognizing Http client based on Java.io & HttpURLConnection
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Http client-side based on Java.io & HttpURLConnection")
        # S97 = State(97, "import java.io.*|import java.net.URL|import java.net.HttpURLConnection",
        #             "Step 1: Import necessary Java IO and networking classes")
        # S98 = State(98, "new URL", "Step 2: Get the access URL")
        # S99 = State(99, "openConnection", "Step 3: Create an HttpURLConnection object")
        # S100 = State(100,
        #              "setRequestMethod|setConnectTimeout|setDoOutput|setDoInput|setUseCaches|setInstanceFollowRedirects|setRequestProperty",
        #              "Step 4: Set request parameters")
        # S101 = State(101, "write|flush|getResponseCode|getInputStream|getOutputStream|readLine|read",
        #              "Step 5: Processing Input and Output")
        # S102 = State(102, "disconnect", "Step 6: Disconnect")
        #
        # S97.AddNext(S98)
        # S98.AddNext(S99)
        # S99.AddNext(S100)
        # S100.AddNext(S101)
        # S101.AddNext(S102)
        # Class.AddState(S97)
        # self.IRIClfList.append(Class)
        #
        # # FSM 23: Recognizing Http client based on Java.io & HttpURLConnection
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Http client-side based on HttpClient in java")
        # S103 = State(103, "import java.net.http.*|import java.net.URI",
        #              "Step 1: Import necessary Java networking classes")
        # S104 = State(104, "HttpClient.newBuilder()", "Step 2: Create an HttpClient instance")
        # S105 = State(105, "GET|POST|PUT|DELETE", "Step 3: Construct an HTTP request")
        # S106 = State(106, "send|sendAsync",
        #              "Step 4: Send the request (synchronously or asynchronously) and handle the response")
        #
        # S103.AddNext(S104)
        # S104.AddNext(S105)
        # S105.AddNext(S106)
        #
        # Class.AddState(S103)
        # self.IRIClfList.append(Class)
        #
        # # FSM 24: Netty HTTP Client
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Netty HTTP Client in java")
        # S107 = State(107,
        #              "import io.netty.bootstrap.Bootstrap|import io.netty.channel.*| import io.netty.handler.codec.http.*",
        #              "Step 1: Import required Netty classes")
        # S108 = State(108, "new NioEventLoopGroup()", "Step 2: Create EventLoopGroup")
        # S109 = State(109, "new Bootstrap()", "Step 3: Create and configure Bootstrap")
        # S110 = State(110,
        #              "pipeline().addLast|HttpClientCodec|HttpContentDecompressor|HttpObjectAggregator|NettyHttpClientHandler",
        #              "Step 4: Set up HTTP pipeline")
        # S111 = State(111, "connect", "Step 5: Connect to HTTP server")
        # S112 = State(112, "new URI|DefaultFullHttpRequest",
        #              "Step 5: Construct HTTP request,use DefaultFullHttpRequest, set GET/POST method, URI, Headers")
        # S113 = State(113, "write|flush|writeAndFlush", "Step 6: Sending Requests & Handling Responses")
        # S114 = State(114, "close|shutdownGracefully", "Step 7: Close the connection to release resources")
        #
        # S107.AddNext(S108)
        # S108.AddNext(S109)
        # S109.AddNext(S110)
        # S110.AddNext(S111)
        # S111.AddNext(S112)
        # S112.AddNext(S113)
        # S113.AddNext(S114)
        # Class.AddState(S107)
        # self.IRIClfList.append(Class)
        #
        # # FSM 25: Netty HTTP Server
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Netty HTTP Server in Java")
        # S115 = State(115,
        #              "import io.netty.bootstrap.ServerBootstrap|import io.netty.channel.*|import io.netty.handler.codec.http.*",
        #              "Step 1: Import required Netty classes, including ServerBootstrap for server setup, Channel for network communication, and HTTP handlers for processing HTTP requests and responses.")
        # S116 = State(116, "new NioEventLoopGroup()|new ServerBootstrap()",
        #              "Step 2: Create bossGroup to accept incoming connections and workerGroup to handle traffic and process events.")
        # S117 = State(117, "NioServerSocketChannel|InetSocketAddress|ChannelInitializer",
        #              "Step 3: Configure the server channel using NioServerSocketChannel for non-blocking I/O, set InetSocketAddress for binding, and use ChannelInitializer to define the channel pipeline.")
        # S118 = State(118,
        #              "HttpRequestDecoder|HttpObjectAggregator|HttpResponseEncoder|HttpContentCompressor|HttpServerCodec|HttpServerExpectContinueHandler|ChunkedWriteHandler|CorsHandler|IdleStateHandler|SslHandler",
        #              "Step 4: Set up the HTTP pipeline with HttpRequestDecoder for decoding requests, HttpObjectAggregator for handling full HTTP messages, HttpResponseEncoder for encoding responses, HttpContentCompressor for compression, HttpServerCodec as a combined codec, HttpServerExpectContinueHandler for handling 100 - Continue requests, ChunkedWriteHandler for large data transmission, CorsHandler for cross - origin requests, IdleStateHandler for connection timeout management, and SslHandler for HTTPS support if needed.")
        # S119 = State(119, "bind",
        #              "Step 5: Bind the server to a specific port and start listening for incoming HTTP connections.")
        # S115.AddNext(S116)
        # S116.AddNext(S117)
        # S117.AddNext(S118)
        # S118.AddNext(S119)
        # Class.AddState(S115)
        # self.IRIClfList.append(Class)
        #
        # # FSM 26: Recognizing Http client based on Java.nio
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "NIO HTTP Client in Java")
        # S120 = State(120, "import java.nio.*|import java.nio.channels.*|import java.net.*",
        #              "Step 1: Import necessary Java NIO and networking classes, including java.nio for buffer operations, java.nio.channels for non-blocking I/O, and java.net for handling network communication.")
        # S121 = State(121, "SocketChannel.open()|configureBlocking(false)|Selector.open()",
        #              "Step 2: Open a non-blocking SocketChannel and configure it to operate asynchronously. Create a Selector to handle multiple non-blocking connections.")
        # S122 = State(122, "selectedKeys()",
        #              "Step 3: Register the SocketChannel with the Selector and initiate a connection to the HTTP server. The Selector will monitor connection readiness events.")
        # S123 = State(123, "isConnectable()",
        #              "Step 4: Once the connection is established, check if the channel is in a connectable state using isConnectable(). Complete the connection if necessary.")
        # S120.AddNext(S121)
        # S121.AddNext(S122)
        # S122.AddNext(S123)
        # Class.AddState(S120)
        # self.IRIClfList.append(Class)
        #
        # # FSM 27: Recognizing Http Server based on Java.nio
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "NIO HTTP Server in Java")
        # S124 = State(124, "import java.nio.*|import java.nio.channels.*|import java.net.*",
        #              "Step 1: Import necessary Java NIO and networking classes, including java.nio for buffer handling, java.nio.channels for non-blocking IO operations, and java.net for network communication.")
        # S125 = State(125, "ServerSocketChannel.open()|bind|configureBlocking(false)|Selector.open()",
        #              "Step 2: Open a ServerSocketChannel, bind it to a specific port, and set it to non-blocking mode using configureBlocking(false) to handle connections asynchronously, and Create a Selector instance, which will manage multiple non-blocking channels and handle events efficiently.")
        # S126 = State(126, "register",
        #              "Step 4: Register the ServerSocketChannel with the Selector, specifying interest in accepting new client connections.")
        # S127 = State(127, "selectedKeys()",
        #              "Step 5: Retrieve the set of selected keys from the Selector, which indicate channels that are ready for I/O operations such as accepting connections or reading data.")
        # S128 = State(128, "isAcceptable()|isReadable()|isWritable()",
        #              "Step 6: Handle incoming connections and data processing based on the SelectionKey state. Use isAcceptable() to accept new client connections, isReadable() to read incoming requests, and isWritable() to send responses.")
        # S124.AddNext(S125)
        # S125.AddNext(S126)
        # S126.AddNext(S127)
        # S127.AddNext(S128)
        # Class.AddState(S124)
        # self.IRIClfList.append(Class)
        #
        # # FSM 28：Java RESTful API HTTP Client
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Java RESTful API HTTP Client")
        # S129 = State(129, "import java.net.http.*|import org.springframework.web.client.RestTemplate|import okhttp3.*",
        #              "Step 1: Import required libraries")
        # S130 = State(130, "HttpClient.newHttpClient()|new RestTemplate()|new OkHttpClient()",
        #              "Step 2: Create HTTP client instance")
        # S131 = State(131, "HttpRequest.newBuilder()|new Request.Builder()", "Step 3: Construct HTTP request (GET/POST)")
        # S132 = State(132, "setHeader|header()", "Step 4: Set request headers")
        # S133 = State(133, "send|sendAsync|execute|exchange", "Step 5: Send HTTP request")
        # S134 = State(134, "getBody|body|parse response", "Step 6: Handle response")
        #
        # S129.AddNext(S130)
        # S130.AddNext(S131)
        # S131.AddNext(S132)
        # S132.AddNext(S133)
        # S133.AddNext(S134)
        #
        # Class.AddState(S129)
        # self.IRIClfList.append(Class)
        #
        # # FSM 29: Recognizing Java GRPC client-side
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "gRPC Client in java")
        # S135 = State(135,
        #              "import io.grpc.ManagedChannel|import io.grpc.ManagedChannelBuilder|import io.grpc.stub.AbstractStub|import io.grpc.StatusRuntimeException",
        #              "Step 1: Import ManagedChannel, ManagedChannelBuilder, AbstractStub for GRPC client, and StatusRuntimeException for error handling")
        # S136 = State(136, "ManagedChannelBuilder.forAddress|ManagedChannelBuilder.forTarget",
        #              "Step 2: Create ManagedChannel for client and establish connection to the GRPC server")
        # S137 = State(137, "newBlockingStub|newStub|asyncStub|StreamObserver",
        #              "Step 3: Create a GRPC stub (blocking or async) and invoke remote method via stub")
        # S138 = State(138, "shutdown|awaitTermination",
        #              "Step 4: Shutdown the ManagedChannel or await termination of GRPC client connection")
        # # State transitions for the FSM
        # S135.AddNext(S136)
        # S136.AddNext(S137)
        # S137.AddNext(S138)
        # # Add states to the client classifier
        # Class.AddState(S135)
        # self.IRIClfList.append(Class)
        #
        # # FSM 30: Recognizing Java gRPC server-side
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "gRPC Server in java")
        # S139 = State(139,
        #              "import io.grpc.Server|import io.grpc.ServerBuilder|import io.grpc.BindableService|import io.grpc.stub.StreamObserver|import io.grpc.ServerServiceDefinition",
        #              "Step 1: Import Server, ServerBuilder for server creation, BindableService for service binding, StreamObserver for handling responses")
        # S140 = State(140, "ServerBuilder.forPort",
        #              "Step 2:Create server using ServerBuilder and specify port")
        # S141 = State(141, "addService|addMethodHandler|serviceConfiguration",
        #              "Add service or method handler to GRPC server, configure service options or middleware")
        # S142 = State(142, "start",
        #              "Step 4: Start the server")
        # S143 = State(143, "shutdown|awaitTermination|gracefulShutdown",
        #              "Step 5: Shutdown GRPC server gracefully, or await termination to wait for all ongoing calls to complete.")
        # # State transitions for the FSM
        # S139.AddNext(S140)
        # S140.AddNext(S141)
        # S141.AddNext(S142)
        # S142.AddNext(S143)
        # # Add states to the server classifier
        # Class.AddState(S139)
        # self.IRIClfList.append(Class)
        #
        # # FSM 31: Recognizing Java EE WebSocket Client
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "WebSocket Client based on Java EE")
        # S144 = State(144,
        #              "import javax.websocket.ContainerProvider|import javax.websocket.WebSocketContainer|import javax.websocket.Session|import javax.websocket.MessageHandler",
        #              "Step 1: Import necessary WebSocket client classes")
        # S145 = State(145, "Session", "Step 2: Create a session for the WebSocket connection")
        # S146 = State(146, "onOpen|onMessage|onClose|onError|sendText|sendBinary|sendObject",
        #              "Step 3: Override OnOpen, OnMessage, OnClose, OnError methods, and optionally handle received messages and send messages within these methods")
        # S147 = State(147, "getWebSocketContainer", "Step 4: Create a WebSocket container instance in the main function")
        # S148 = State(148, "connectToServer|sendText|sendBinary|sendObject",
        #              "Step 5: Connect to the WebSocket server in the main function, provide the endpoint, and optionally send messages after the connection is established if needed")
        # S144.AddNext(S145)
        # S145.AddNext(S146)
        # S146.AddNext(S147)
        # S147.AddNext(S148)
        # Class.AddState(S144)
        # self.IRIClfList.append(Class)
        #
        # # FSM 32: Recognizing Java EE WebSocket Server
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "WebSocket Server based on Java EE")
        # S149 = State(149,
        #              "import javax.websocket.server.ServerEndpoint|import javax.websocket.Session|import javax.websocket.OnMessage|import javax.websocket.OnOpen|import javax.websocket.OnClose",
        #              "Step 1: Import the necessary WebSocket server classes")
        # S150 = State(150, "@ServerEndpoint",
        #              "Step 2: Define a WebSocket server endpoint using the @ServerEndpoint annotation")
        # S151 = State(151, "Session",
        #              "Step 3: Define the WebSocket server endpoint and manage client connections using the Session object")
        # S152 = State(152, "onOpen|onMessage|onClose|sendText|sendBinary|sendObject",
        #              "Step 4: Implement the methods like onOpen, onMessage, onClose to handle client communication and data exchange")
        #
        # S149.AddNext(S150)
        # S150.AddNext(S151)
        # S151.AddNext(S152)
        # Class.AddState(S149)
        # self.IRIClfList.append(Class)
        #
        # # FSM 33：WebSocket Client Implementation using org.java_websocket
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java",
        #                       "WebSocket Client Implementation using org.java_websocket")
        # S153 = State(153,
        #              "import java.net.URI|import org.java_websocket.client.WebSocketClient|import org.java_websocket.handshake.ServerHandshake",
        #              "Step 1: Import necessary WebSocket client classes")
        # S154 = State(154, "extends WebSocketClient", "Step 2: Define MyWebSocketClient class extending WebSocketClient")
        # S155 = State(155, "onOpen|onMessage|onClose|onError", "Step 3: Override WebSocket event - handling methods")
        # S153.AddNext(S154)
        # S154.AddNext(S155)
        # Class.AddState(S153)
        # self.IRIClfList.append(Class)
        #
        # # FSM 34: WebSocket Server Handler using org.java_websocket
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "WebSocket Server Handler using org.java_websocket")
        # S156 = State(156,
        #              "import org.java_websocket.server.WebSocketServer|import org.java_websocket.WebSocket|import org.java_websocket.handshake.ClientHandshake",
        #              "Step 1: Import necessary classes from org.java_websocket, including WebSocketServer, WebSocket, and ClientHandshake for server implementation.")
        # S157 = State(157, "extends WebSocketServer",
        #              "Step 2: Extend WebSocketServer class to create a custom WebSocket server, overriding lifecycle methods for handling connections, messages, and disconnections.")
        # S158 = State(158, "onOpen|onMessage|onClose|onError",
        #              "Step 3: Implement WebSocket lifecycle methods: onOpen for new client connections, onMessage for processing received messages, onClose for handling disconnections, and onError for error handling.")
        # # State transitions for the FSM
        # S156.AddNext(S157)
        # S157.AddNext(S158)
        # Class.AddState(S156)
        # self.IRIClfList.append(Class)
        #
        # # FSM 35：WebSocket Server Initialization using org.java_websocket
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java",
        #                       "WebSocket Server Initialization using org.java_websocket")
        # S159 = State(159, "import org.java_websocket.server.WebSocketServer|import org.java_websocket.Server",
        #              "Step 1: Import necessary WebSocketServer and Server classes")
        # S160 = State(160, "start()", "Step 3: Start the WebSocket server")
        # S161 = State(161, "run()",
        #              "Step 4: Run the WebSocket server, it listens for connections and handles incoming requests")
        # S162 = State(162, "stop()", "Step 5: Stop the WebSocket server after the work is done")
        # # State transitions for the FSM
        # S159.AddNext(S160)
        # S160.AddNext(S161)
        # S161.AddNext(S162)
        # Class.AddState(S159)
        # self.IRIClfList.append(Class)
        #
        # # FSM 36: WebSocket Client using Netty
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "WebSocket Client using Netty in Java")
        # S163 = State(163,
        #              "import io.netty.bootstrap.Bootstrap|import io.netty.channel.*|import io.netty.handler.codec.http.*|import io.netty.handler.codec.http.websocketx.*",
        #              "Step 1: Import necessary classes, including Bootstrap for client setup, Channel for network communication, HTTP handlers for WebSocket upgrade, and WebSocket handlers for processing frames.")
        # S164 = State(164, "new NioEventLoopGroup()|new Bootstrap()",
        #              "Step 2: Create EventLoopGroup for managing I/O operations asynchronously and initialize a Bootstrap instance to configure the WebSocket client.")
        # S165 = State(165, "NioSocketChannel|LoggingHandler|ChannelInitializer",
        #              "Step 3: Set up the Netty client pipeline using NioSocketChannel for non-blocking I/O, LoggingHandler for debugging, and ChannelInitializer for configuring the channel handlers.")
        # S166 = State(166, "HttpClientCodec|WebSocketClientProtocolHandler|WebSocketFrameDecoder|WebSocketFrameEncoder",
        #              "Step 4: Configure the WebSocket client pipeline by adding HttpClientCodec to handle HTTP requests, WebSocketClientProtocolHandler for managing the WebSocket handshake and frame processing, WebSocketFrameDecoder/WebSocketFrameEncoder for decoding and encoding WebSocket frames.")
        # S167 = State(167, "connect", "Step 5: Establish connection to the WebSocket server.")
        # S168 = State(168, "sync|addListener|syncUninterruptibly|await",
        #              "Step 6: Handshake with the WebSocket server and wait for the connection to complete, using sync and addListener methods to monitor connection status.")
        # S169 = State(169, "writeAndFlush|write|flush|ChannelFuture|ChannelHandlerContext",
        #              "Step 7: Send WebSocket messages using writeAndFlush method or equivalent, sending WebSocket frames to the server.")
        # S170 = State(170, "closeFuture().sync|closeFuture().addListener|close|shutdownGracefully|fireChannelInactive",
        #              "Step 8: Close the connection, release resources, and handle shutdown gracefully by monitoring closeFuture() and calling shutdownGracefully() on the EventLoopGroup.")
        # # Define state transitions
        # S163.AddNext(S164)
        # S164.AddNext(S165)
        # S165.AddNext(S166)
        # S166.AddNext(S167)
        # S167.AddNext(S168)
        # S168.AddNext(S169)
        # S169.AddNext(S170)
        # # Add states to the classifier
        # Class.AddState(S163)
        # self.IRIClfList.append(Class)
        #
        # # FSM 37: WebSocket Server using Netty
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "WebSocket Server using Netty in Java")
        # S171 = State(171,
        #              "import io.netty.bootstrap.ServerBootstrap|import io.netty.channel.*|import io.netty.handler.codec.http.*|import io.netty.handler.codec.http.websocketx.*",
        #              "Step 1: Import required Netty classes, including ServerBootstrap for server setup, Channel for network communication, HTTP handlers for handling HTTP upgrade requests, and WebSocket handlers for processing WebSocket frames.")
        # S172 = State(172, "new NioEventLoopGroup()|new ServerBootstrap()",
        #              "Step 2: Create a NioEventLoopGroup for managing event loops and initialize a ServerBootstrap instance to configure the WebSocket server.")
        # S173 = State(173, "NioServerSocketChannel|LoggingHandler|ChannelInitializer",
        #              "Step 3: Set up the Netty server pipeline using NioServerSocketChannel for non-blocking I/O, LoggingHandler for debugging, and ChannelInitializer for configuring pipeline handlers.")
        # S174 = State(174,
        #              "HttpServerCodec|HttpObjectAggregator|WebSocketServerCompressionHandler|WebSocketServerProtocolHandler|WebSocketFrameDecoder|WebSocketFrameEncoder",
        #              "Step 4: Configure the WebSocket server pipeline. Add HttpServerCodec to handle HTTP requests, HttpObjectAggregator to aggregate HTTP messages, WebSocketServerCompressionHandler for frame compression, WebSocketServerProtocolHandler to manage the WebSocket handshake and frame processing, and WebSocketFrameDecoder/WebSocketFrameEncoder for decoding and encoding WebSocket messages.")
        # S175 = State(175, "bind",
        #              "Step 5: Bind the server to a specified host and port using ServerBootstrap to start listening for incoming WebSocket connections.")
        # S176 = State(176,
        #              "channelFuture.sync|closeFuture().sync()|shutdownGracefully()|shutdown()|fireChannelInactive()",
        #              "Step 6: Synchronize on the server channel’s Future to ensure the server runs, wait for closeFuture() to detect server shutdown, and release resources gracefully using shutdownGracefully() on the EventLoopGroup.")
        # # Define state transitions
        # S171.AddNext(S172)
        # S172.AddNext(S173)
        # S173.AddNext(S174)
        # S174.AddNext(S175)
        # S175.AddNext(S176)
        # # Add states to the classifier
        # Class.AddState(S171)
        # self.IRIClfList.append(Class)
        #
        # # FSM 38：Kafka client Producer
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Kafka client Producer in java")
        # S177 = State(177,
        #              "import org.apache.kafka.clients.producer.KafkaProducer|import org.apache.kafka.clients.producer.ProducerConfig|import org.apache.kafka.clients.producer.ProducerRecord|import org.apache.kafka.common.serialization.StringSerializer|import java.util.Properties",
        #              "Step 1: Import Kafka dependencies and related classes for configuring and creating a Kafka Producer")
        # S178 = State(178, "ProducerConfig", "Step 2: Configure Kafka Producer properties")
        # S179 = State(179, "new KafkaProducer", "Step 3: Create a Kafka Producer instance using the configuration")
        # S180 = State(180, "send|ProducerRecord|flush", "Step 4: Send messages to Kafka")
        # S181 = State(181, "close", "Step 5: Close the Kafka Producer")
        # # State transitions
        # S177.AddNext(S178)
        # S178.AddNext(S179)
        # S179.AddNext(S180)
        # S180.AddNext(S181)
        # # Add states to the classifier
        # Class.AddState(S177)
        # self.IRIClfList.append(Class)
        #
        # # FSM 39：Kafka client Consumer
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Kafka client Consumer in java")
        # S182 = State(182,
        #              "import org.apache.kafka.clients.consumer.ConsumerConfig|import org.apache.kafka.clients.consumer.KafkaConsumer|import org.apache.kafka.common.serialization.StringDeserializer|import java.util.Collections|import java.util.Properties;",
        #              "Step 1: Import Kafka dependencies and related classes for configuring and creating a Kafka Consumer")
        # S183 = State(183, "ConsumerConfig", "Step 2: Configure Kafka Consumer properties")
        # S184 = State(184, "new KafkaConsumer", "Step 3: Create a Kafka Consumer instance using the configuration")
        # S185 = State(185, "subscribe|assign|ConsumerRecords|unsubscribe", "Step 4: Subscribe to a Kafka topic")
        # S186 = State(186, "poll|commitSync|commitAsync|seek|pause|resume", "Step 5: Consume messages from Kafka")
        # S187 = State(187, "close", "Step 6: Close the Kafka Consumer")
        # # State transitions
        # S182.AddNext(S183)
        # S183.AddNext(S184)
        # S184.AddNext(S185)
        # S185.AddNext(S186)
        # S186.AddNext(S187)
        # # Add states to the classifier
        # Class.AddState(S182)
        # self.IRIClfList.append(Class)
        #
        # # FSM 40: Create Kafka AdminClient in Java
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Create and Configure Kafka AdminClient in java")
        # S188 = State(188, "import org.apache.kafka.clients.admin.*",
        #              "Step 1: Import necessary Kafka AdminClient classes for managing Kafka topics and configurations.")
        # S189 = State(189, "new Properties|newHashMap",
        #              "Step 2: Create a Properties object to store Kafka AdminClient configuration settings.")
        # S190 = State(190, "setProperty|put|AdminClientConfig",
        #              "Step 3: Set Kafka AdminClient properties such as bootstrap servers and security settings.")
        # S191 = State(191, "AdminClient.create",
        #              "Step 4: Instantiate Kafka AdminClient using the configured properties.")
        # # Define state transitions for Kafka AdminClient FSM
        # S188.AddNext(S189)
        # S189.AddNext(S190)
        # S190.AddNext(S191)
        # Class.AddState(S188)
        # self.IRIClfList.append(Class)
        #
        # # FSM 41: Create Kafka Topic Instance
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Create Kafka topic instance in AdminClient in java")
        # S192 = State(192, "import org.apache.kafka.clients.admin.*",
        #              "Step 1: Import Kafka AdminClient classes to work with Kafka topics")
        # S193 = State(193, "adminClient()", "Step 2: Create an AdminClient instance to interact with Kafka broker")
        # S194 = State(194, "new NewTopic",
        #              "Step 3: Create a NewTopic object which defines the topic's configuration like name, partitions, and replication factor")
        # S195 = State(195, "createTopics",
        #              "Step 4: Use AdminClient to create the topic in Kafka using the NewTopic object")
        # # Define state transitions
        # S192.AddNext(S193)
        # S193.AddNext(S194)
        # S194.AddNext(S195)
        # # Add states to the classifier
        # Class.AddState(S192)
        # self.IRIClfList.append(Class)
        #
        # # FSM 42: View/Delete/Describe Topic in Kafka using AdminClient
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "View/Delete/Describe topic in AdminClient in java")
        # S196 = State(196, "import org.apache.kafka.clients.admin.*",
        #              "Step 1: Import Kafka AdminClient classes for performing administrative operations on Kafka topics.")
        # S197 = State(197, "listTopics|deleteTopics|describeTopics|describeCluster|listConsumerGroups|listOffsets",
        #              "Step 3: Use AdminClient methods to perform actions such as listing topics, deleting topics, or describing topics and clusters.")
        # S198 = State(198, "get",
        #              "Step 4: Retrieve the results of the operation (e.g., list topics, delete topics, or describe topics) using the `get()` method to fetch the response.")
        # # Define state transitions
        # S196.AddNext(S197)
        # S197.AddNext(S198)
        # # Add states to the classifier
        # Class.AddState(S196)
        # self.IRIClfList.append(Class)
        #
        # # FSM 43: View Kafka AdminClient Configuration in Java
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "View Kafka AdminClient  Config in java")
        # S199 = State(199,
        #              "import org.apache.kafka.clients.admin.*|import org.apache.kafka.common.config.ConfigResource",
        #              "Step 1: Import required Kafka AdminClient and ConfigResource classes for viewing topic or broker configurations.")
        # S200 = State(200, "ConfigResource",
        #              "Step 2: Define a ConfigResource for the topic or broker whose configuration needs to be described. This specifies the resource (e.g., topic) whose configuration will be fetched.")
        # S201 = State(201, "describeConfigs",
        #              "Step 3: Call `describeConfigs` method on AdminClient to retrieve the configuration of the specified topic or broker.")
        # S202 = State(202, "get",
        #              "Step 4: Use the `get()` method to fetch the configuration details retrieved by `describeConfigs`.")
        # # Define state transitions
        # S199.AddNext(S200)
        # S200.AddNext(S201)
        # S201.AddNext(S202)
        # # Add states to the classifier
        # Class.AddState(S199)
        # self.IRIClfList.append(Class)
        #
        # # FSM 44: Update Kafka Topic Partition
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Update Kafka Topic Partition in java")
        # S203 = State(203,
        #              "import org.apache.kafka.clients.admin.*|import org.apache.kafka.common.errors.*|import com.google.common.collect.Maps",
        #              "Step 1: Import necessary Kafka AdminClient and other classes")
        # S204 = State(204, "newPartitions.put|increaseTo", "Step 2: Prepare new partition configurations")
        # S205 = State(205, "createPartitions", "Step 3: Execute partition update request")
        # S206 = State(206, "get()", "Step 4: Wait for the operation to complete (blocking call)")
        # # Define state transitions
        # S203.AddNext(S204)
        # S204.AddNext(S205)
        # S205.AddNext(S206)
        # # Add states to the classifier
        # Class.AddState(S203)
        # self.IRIClfList.append(Class)
        #
        # # FSM 45: Redis in Java
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Redis in Java")
        # S207 = State(207,
        #              "import redis.clients.jedis.*|import io.lettuce.core.*|import org.springframework.data.redis.core.*",
        #              "Step 1: Import necessary Redis client libraries (Jedis, Lettuce, Spring Data Redis)")
        # S208 = State(208, "new Jedis|new JedisPool|new JedisCluster|RedisClient.create|new RedisTemplate",
        #              "Step 2: Create a Redis connection instance")
        # S209 = State(209, "auth|getResource|connect|setConnectionFactory",
        #              "Step 3: Authenticate (if required) and establish the connection")
        # S210 = State(210,
        #              "set|get|del|exists|expire|ttl|ftCreate|ftSearch|getDocuments|hset|hget|hmget|hmset|hdel|hlen|hkeys|hvals|lpush|rpush|lpop|rpop|lrange|sadd|srem|smembers|scard|zadd|zrem|zincrby|zscore|zrange|zrevrange|multi|exec|discard|watch|unwatch|pipeline|scriptLoad|eval|evalsha|publish|subscribe|xadd|xread|xgroupCreate|xgroupDestroy|xack",
        #              "Step 4: Perform Redis operations (CRUD, transactions, scripting, pub/sub, streams)")
        # S211 = State(211, "close|shutdown", "Step 5: Close the Redis connection to release resources")
        # # Define state transitions
        # S207.AddNext(S208)
        # S208.AddNext(S209)
        # S209.AddNext(S210)
        # S210.AddNext(S211)
        # S208.AddNext(S210)
        # Class.AddState(S207)
        # self.IRIClfList.append(Class)
        #
        # # FSM 46: ActiveMQ Producer in Java
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "ActiveMQ Producer in Java")
        # S212 = State(212, "import org.apache.activemq.ActiveMQConnectionFactory|import javax.jms.*",
        #              "Step 1: Import necessary ActiveMQ and JMS libraries")
        # S213 = State(213, "new ActiveMQConnectionFactory", "Step 2: Create a connection factory for the broker")
        # S214 = State(214, "createConnection", "Step 3: Create a connection to the ActiveMQ broker")
        # S215 = State(215, "start()", "Step 4: Start the connection to begin communication")
        # S216 = State(216, "createSession", "Step 5: Create a session for sending and receiving messages")
        # S217 = State(217,
        #              "createQueue|createTopic|createTemporaryQueue|createTemporaryTopic|createSharedQueue|createSharedTopic",
        #              "Step 6: Create a destination queue or topic for the messages")
        # S218 = State(218, "createProducer", "Step 7: Create a producer to send messages to the queue or topic")
        # S219 = State(219,
        #              "createTextMessage|createMapMessage|createObjectMessage|createBytesMessage|createStreamMessage|createMessage|createBytesMessage",
        #              "Step 8: Create a message to be sent")
        # S220 = State(220, "send|close()",
        #              "Step 9: Send the created message to the queue or topic and close the connection to release resources")
        # # Define state transitions
        # S212.AddNext(S213)
        # S213.AddNext(S214)
        # S214.AddNext(S215)
        # S215.AddNext(S216)
        # S216.AddNext(S217)
        # S217.AddNext(S218)
        # S218.AddNext(S219)
        # S219.AddNext(S220)
        #
        # Class.AddState(S212)
        # self.IRIClfList.append(Class)
        #
        # # FSM 47: ActiveMQ Consumer in Java
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "ActiveMQ Consumer in Java")
        # S221 = State(221, "import org.apache.activemq.ActiveMQConnectionFactory|import javax.jms.*",
        #              "Step 1: Import necessary ActiveMQ and JMS libraries")
        # S222 = State(222, "new ActiveMQConnectionFactory", "Step 2: Create a connection factory for the broker")
        # S223 = State(223, "createConnection", "Step 3: Create a connection to the ActiveMQ broker")
        # S224 = State(224, "start()", "Step 4: Start the connection to begin communication")
        # S225 = State(225, "createSession", "Step 5: Create a session for receiving messages")
        # S226 = State(226,
        #              "createQueue|createTopic|createTemporaryQueue|createTemporaryTopic|createSharedQueue|createSharedTopic",
        #              "Step6: Create a destination queue or topic for receiving messages")
        # S227 = State(227, "createConsumer", "Step 7: Create a consumer to receive messages from the queue or topic")
        # S228 = State(228, "receive|receiveNoWait|close",
        #              "Step 8: Receive a message from the queue or topic and then close the connection to release resources")
        #
        # # Define state transitions
        # S221.AddNext(S222)
        # S222.AddNext(S223)
        # S223.AddNext(S224)
        # S224.AddNext(S225)
        # S225.AddNext(S226)
        # S226.AddNext(S227)
        # S227.AddNext(S228)
        # Class.AddState(S221)
        # self.IRIClfList.append(Class)
        #
        # # FSM 48: RabbitMQ Producer in Java
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "RabbitMQ Producer in Java")
        # S229 = State(229, "import com.rabbitmq.client.*",
        #              "Step 1: Import the RabbitMQ client library for communication")
        # S230 = State(230, "new ConnectionFactory",
        #              "Step 2: Create a connection factory to configure RabbitMQ connection settings")
        # S231 = State(231, "newConnection()", "Step 3: Establish a connection to the RabbitMQ broker")
        # S232 = State(232, "createChannel()", "Step 4: Create a channel for sending messages")
        # S233 = State(233, "queueDeclare|exchangeDeclare", "Step 5: Declare a queue or exchange to send messages to")
        # S234 = State(234, "basicPublish|basicReturn",
        #              "Step 6: Create and send a message to the declared queue or exchange")
        # S235 = State(235, "close()", "Step 7: Close the channel and the connection to release resources")
        # # Define state transitions
        # S229.AddNext(S230)
        # S230.AddNext(S231)
        # S231.AddNext(S232)
        # S232.AddNext(S233)
        # S233.AddNext(S234)
        # S234.AddNext(S235)
        # Class.AddState(S229)
        # self.IRIClfList.append(Class)
        #
        # # FSM 49: RabbitMQ Consumer in Java
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "RabbitMQ Consumer in Java")
        # S236 = State(236, "import com.rabbitmq.client.*",
        #              "Step 1: Import the RabbitMQ client library to enable communication with the RabbitMQ broker")
        # S237 = State(237, "new ConnectionFactory",
        #              "Step 2: Create a ConnectionFactory instance to configure RabbitMQ connection settings, such as host, port, and authentication credentials")
        # S238 = State(238,
        #              "setHost|setPort|setUsername|setPassword|setVirtualHost|setConnectionTimeout|setRequestedHeartbeat|setAutomaticRecoveryEnabled|setNetworkRecoveryInterval",
        #              "Step 3: Configure the ConnectionFactory settings, including host, port, authentication, virtual host, connection timeout, heartbeat interval, and automatic recovery options")
        # S239 = State(239, "newConnection()",
        #              "Step 4: Establish a connection to the RabbitMQ broker using the configured ConnectionFactory")
        # S240 = State(240, "createChannel()",
        #              "Step 5: Create a channel to interact with the message broker, including message consumption and acknowledgment handling")
        # S241 = State(241, "new DefaultConsumer|handleDelivery",
        #              "Step 6: Implement a message consumer using DefaultConsumer and handle incoming messages in the handleDelivery method")
        # S242 = State(242, "basicConsume",
        #              "Step 7: Start consuming messages from a specific queue, specifying auto-acknowledge or manual acknowledgment mode")
        # # Define state transitions
        # S236.AddNext(S237)
        # S237.AddNext(S238)
        # S238.AddNext(S239)
        # S239.AddNext(S240)
        # S240.AddNext(S241)
        # S241.AddNext(S242)
        # Class.AddState(S236)
        # self.IRIClfList.append(Class)
        #
        # # FSM 50: RocketMQ Producer in Java
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "RocketMQ Producer in Java")
        # S243 = State(243,
        #              "import org.apache.rocketmq.client.producer.*|import org.apache.rocketmq.common.message.Message;",
        #              "Step 1: Import RocketMQ producer-related libraries")
        # S244 = State(244, "new DefaultMQProducer|new TransactionMQProducer|new OnewayMQProducer",
        #              "Step 2: Create a producer instance (Default, Transactional, or One-way producer)")
        # S245 = State(245,
        #              "setNamesrvAddr|setRetryTimesWhenSendFailed|setRetryTimesWhenSendAsyncFailed|setSendLatencyFaultEnable|setRetryAnotherBrokerWhenNotStoreOK|setCompressMsgBodyOverHowmuch|setMaxMessageSize|setCreateTopicKey|setSendMsgTimeout|setVipChannelEnabled|setInstanceName",
        #              "Step 3: Configure the producer settings. Set the NameServer address and configure retry policies, timeout settings, message size limits, and other advanced parameters to optimize performance and reliability.")
        # S246 = State(246, "start()", "Step 4: Start the producer to initialize it for sending messages")
        # S247 = State(247, "new Message", "Step 5: Create a message to send")
        # S248 = State(248, "send|sendOneway|sendMessageInTransaction",
        #              "Step 6: Send the message (sync, async, or transactional)")
        #
        # # Define state transitions
        # S243.AddNext(S244)
        # S244.AddNext(S245)
        # S245.AddNext(S246)
        # S246.AddNext(S247)
        # S247.AddNext(S248)
        #
        # Class.AddState(S243)
        # self.IRIClfList.append(Class)
        #
        # # FSM 51: RocketMQ Consumer in Java
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "RocketMQ Consumer in Java")
        # S249 = State(249,
        #              "import org.apache.rocketmq.client.consumer.*|import org.apache.rocketmq.common.message.Message;",
        #              "Step 1: Import necessary RocketMQ consumer-related libraries, including consumer classes and message handling utilities.")
        # S250 = State(250, "new DefaultMQPushConsumer|new DefaultMQPullConsumer",
        #              "Step 2: Create a consumer instance. Use DefaultMQPushConsumer for push-based consumption or DefaultMQPullConsumer for pull-based consumption.")
        # S251 = State(251,
        #              "setNamesrvAddr|setConsumeFromWhere|setMessageModel|setMaxReconsumeTimes|setConsumeThreadMin|setConsumeThreadMax|setPullBatchSize|setConsumeTimeout|setInstanceName|setAdjustThreadPool|setUnitName",
        #              "Step 3: Configure the consumer settings. Set the NameServer address, define consumption strategy (e.g., ConsumeFromWhere), choose a message model (Clustering or Broadcasting), and specify retry policies. Additionally, configure thread pool size, batch size, timeout settings, instance name, and other performance-related parameters.")
        # S252 = State(252, "subscribe",
        #              "Step 4: Subscribe to a specific topic and optionally filter messages based on tags.")
        # S253 = State(253, "registerMessageListener",
        #              "Step 5: Register a message listener (either MessageListenerConcurrently or MessageListenerOrderly) to handle incoming messages asynchronously.")
        # S254 = State(254, "start()",
        #              "Step 6: Start the consumer to establish connection with the broker and begin consuming messages.")
        # # Define state transitions
        # S249.AddNext(S250)
        # S250.AddNext(S251)
        # S251.AddNext(S252)
        # S252.AddNext(S253)
        # S253.AddNext(S254)
        #
        # Class.AddState(S249)
        # self.IRIClfList.append(Class)
        #
        # # FSM 52: ProcessBuilder in java.io
        # Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "ProcessBuilder in java.io")
        # S255 = State(255, "import java.io.*",
        #              "Step 1: Import necessary Java I/O classes to handle process input, output, and error streams.")
        # S256 = State(256, "new ProcessBuilder|redirectErrorStream",
        #              "Step 2: Create a new ProcessBuilder instance, configure it with the command to execute, and optionally redirect error streams to standard output.")
        # S257 = State(257, "start()",
        #              "Step 3: Start the external process using the start() method, which returns a Process instance representing the running process.")
        # S258 = State(258, "getOutputStream|getInputStream",
        #              "Step 4: Retrieve the process's input and output streams using getOutputStream() for writing to the process and getInputStream() for reading from it.")
        # S259 = State(259, "waitFor()",
        #              "Step 5: Call waitFor() to block the current thread until the external process terminates, ensuring proper synchronization.")
        #
        # # Define state transitions
        # S255.AddNext(S256)
        # S256.AddNext(S257)
        # S257.AddNext(S258)
        # S258.AddNext(S259)
        # Class.AddState(S255)
        # self.IRIClfList.append(Class)



        ############################################################
        # Class: Python*
        ############################################################
        # PHP语言面向多编程语言交互的进程间通信方法包括：
        # 套接字技术：TCP/UDP/Websocket
        # 内存共享技术:
        # 消息队列：Redis/Kafka/RabbitMQ/RocketMQ
        # gRPC
        # 文件交互:JSON-RPC/XML-RPC
        # FSM 1: WebSocket Server-side by using asyncio+websockets in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py",
                              "WebSocket Server-side by using asyncio+websockets in python")
        S0 = State(0, "import asyncio|import websockets", "Step 1: Import the asyncio and websockets libraries")
        S1 = State(1, "async def", "Step 2: Define an asynchronous function to handle WebSocket logic")
        S2 = State(2, "serve", "Step 3: Start the WebSocket server")
        S3 = State(3, "send|recv()", "Step 4: Send or receive messages through the WebSocket connection")
        S4 = State(4, "asyncio.run|run_until_complete|call_soon|call_later", "Step 5: Run the asyncio event loop")
        # State transitions for the FSM
        S0.AddNext(S1)
        S1.AddNext(S2)
        S2.AddNext(S3)
        S3.AddNext(S4)
        # Add state to the server classifier
        Class.AddState(S0)
        self.IRIClfList.append(Class)

        # FSM 2: WebSocket Client-side by using asyncio+websockets in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py",
                              "WebSocket Client-side by using asyncio+websockets in python")
        S5 = State(5, "import asyncio|import websockets", "Step 1: Import the asyncio and websockets libraries")
        S6 = State(6, "async def", "Step 2: Define an asynchronous function to handle WebSocket client logic")
        S7 = State(7, "connect", "Step 3: Establish a connection to the WebSocket server using websockets.connect()")
        S8 = State(8, "send|recv()", "Step 4: Send or receive messages through the WebSocket connection")
        S9 = State(9, "asyncio.run|run_until_complete|call_soon|call_later", "Step 5: Run the asyncio event loop")
        # State transitions for the FSM
        S5.AddNext(S6)
        S6.AddNext(S7)
        S7.AddNext(S8)
        S8.AddNext(S9)
        # Add state to the server classifier
        Class.AddState(S5)
        self.IRIClfList.append(Class)

        # FSM 3: Broadcast messages to multiple clients by using asyncio+websockets in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py",
                              "WebSocket Server-side for broadcasting using asyncio+websockets in python")
        S10 = State(10, "import asyncio|import websockets", "Step 1: Import the asyncio and websockets libraries")
        S11 = State(11, "set()", "Step 2: Maintain a set to track all connected clients")
        S12 = State(12, "async def", "Step 3: Define an asynchronous function to handle incoming WebSocket connections")
        S13 = State(13, "add", "Step 4: Add a newly connected client to the client set")
        S14 = State(14, "asyncio.gather", "Step 5: Broadcast messages to all connected clients using asyncio.gather()")
        S15 = State(15, "remove", "Step 6: Remove disconnected clients from the client set")
        S16 = State(16, "serve", "Step 7: Start the WebSocket server using websockets.serve()")
        S17 = State(17, "asyncio.run|run_until_complete|call_soon|call_later", "Step 8: Run the asyncio event loop")
        # State transitions for the FSM
        S10.AddNext(S11)
        S11.AddNext(S12)
        S12.AddNext(S13)
        S13.AddNext(S14)
        S14.AddNext(S15)
        S15.AddNext(S16)
        S16.AddNext(S17)
        # Add state to the server classifier
        Class.AddState(S10)
        self.IRIClfList.append(Class)

        # FSM 4: WebSocket Client-side by using websocket - client in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py",
                              "WebSocket Client-side by using websocket - client in python")
        S18 = State(18, "import websocket|from websocket import WebSocketApp",
                    "Step 1: Import the websocket and WebSocketApp classes from the websocket library")
        S19 = State(19, "on_message|on_error|on_close|on_ping|on_pong|on_open",
                    "Step 2: Define the callback functions for handling WebSocket events (on_message, on_error, on_close, etc.)")
        S20 = State(20, "WebSocketApp",
                    "Step 3: Create an instance of WebSocketApp with the necessary callback functions and URL")
        S21 = State(21, "run_forever()|run_once()",
                    "Step 4: Start the WebSocket client with run_forever() or run_once() to handle the connection")
        # State transitions for the FSM
        S18.AddNext(S19)
        S19.AddNext(S20)
        S20.AddNext(S21)
        # Add state to the server classifier
        Class.AddState(S18)
        self.IRIClfList.append(Class)

        # FSM 5: WebSocket Server - side by using fastapi in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "WebSocket Server - side by using FastAPI in python")
        S22 = State(22, "from fastapi import .*", "Step 1: Import necessary libraries from FastAPI")
        S23 = State(23, "FastAPI()", "Step 2: Create a FastAPI instance to set up the WebSocket server")
        S24 = State(24, "await websocket.accept()", "Step 3: Accept the incoming WebSocket connection from the client")
        S25 = State(25, "receive_text()|receive_bytes()|receive_json()|send_text()|send_bytes()|send_json()",
                    "Step 4: Handle incoming and outgoing WebSocket messages using appropriate methods")
        # State transitions for the FSM
        S22.AddNext(S23)
        S23.AddNext(S24)
        S24.AddNext(S25)
        # Add state to the server classifier
        Class.AddState(S22)
        self.IRIClfList.append(Class)

        # FSM 6: WebSocket Server - side by using Sanic in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "WebSocket Server - side by using Sanic in python")
        S26 = State(26, "from sanic import Sanic|from sanic.response import .*|from sanic.websocket import .*",
                    "Step 1: Import the necessary modules from Sanic, including Sanic for the app, response for sending responses, and websocket for handling WebSocket connections.")
        S27 = State(27, "Sanic", "Step 2: Create a Sanic app instance to initialize the web server.")
        S28 = State(28, "async def",
                    "Step 3: Define an asynchronous function to handle WebSocket connections and manage the communication logic.")
        S29 = State(29, "recv()|send",
                    "Step 4: Use WebSocket's recv() method to receive messages from clients and send() method to send messages back to clients.")
        # State transitions for the FSM
        S26.AddNext(S27)
        S27.AddNext(S28)
        S28.AddNext(S29)
        # Add state to the server classifier
        Class.AddState(S26)
        self.IRIClfList.append(Class)

        # FSM 7: WebSocket Server - side by using Tornado in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "WebSocket Server - side by using Tornado in python")
        S30 = State(30, "import tornado.ioloop|import tornado.web|import tornado.websocket|from tornado import.*",
                    "Step 1: Import necessary Tornado libraries for WebSocket server")
        S31 = State(31, "WebSocketHandler", "Step 2: Define a WebSocketHandler class to handle WebSocket connections")
        S32 = State(32, "open|on_message|on_close|on_error",
                    "Step 3: Implement WebSocketHandler methods such as open, on_message, on_close, and on_error to handle the lifecycle of a WebSocket connection")
        S33 = State(33, "Application",
                    "Step 4: Create an Application instance and add the WebSocketHandler to route WebSocket connections")
        # State transitions for the FSM
        S30.AddNext(S31)
        S31.AddNext(S32)
        S32.AddNext(S33)
        # Add state to the server classifier
        Class.AddState(S30)
        self.IRIClfList.append(Class)

        # FSM 8: WebSocket Client - side by using Tornado in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "WebSocket Client - side by using Tornado in python")
        S34 = State(34, "import tornado.ioloop|import tornado.websocket|from tornado import.*",
                    "Step 1: Import necessary Tornado libraries for WebSocket client")
        S35 = State(35, "WebSocketClientConnection",
                    "Step 2: Create a WebSocketClientConnection to initiate a WebSocket connection to the server")
        S36 = State(36, "open|on_message|on_close|on_error",
                    "Step 3: Implement methods like open, on_message, on_close, and on_error to handle WebSocket connection events and data")
        S37 = State(37, "websocket_connect",
                    "Step 4: Use websocket_connect to establish the connection with the WebSocket server")
        # State transitions for the FSM
        S34.AddNext(S35)
        S35.AddNext(S36)
        S36.AddNext(S37)
        # Add state to the server classifier
        Class.AddState(S34)
        self.IRIClfList.append(Class)

        # FSM 9: WebSocket Server - side by using autobahn+asyncio in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py",
                              "WebSocket Server - side by using autobahn+asyncio in python")
        S38 = State(38,
                    "import asyncio|from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory|from autobahn.websocket import connect",
                    "Step 1: Import necessary modules for Autobahn and asyncio WebSocket server")
        S39 = State(39, "WebSocketServerProtocol",
                    "Step 2: Define a custom class that inherits from WebSocketServerProtocol to handle WebSocket events")
        S40 = State(40, "onConnect|onOpen|onMessage|onClose",
                    "Step 3: Implement WebSocket lifecycle methods such as onConnect, onOpen, onMessage, and onClose")
        S41 = State(41, "WebSocketServerFactory",
                    "Step 4: Create a WebSocketServerFactory instance to manage connections")
        S42 = State(42, "get_event_loop()|create_server", "Step 5: Set up the asyncio event loop and create the server")
        S43 = State(43, "run_until_complete|run_forever", "Step 6: Start the event loop to run the server continuously")
        # State transitions for the FSM
        S38.AddNext(S39)
        S39.AddNext(S40)
        S40.AddNext(S41)
        S41.AddNext(S42)
        S42.AddNext(S43)
        # Add state to the server classifier
        Class.AddState(S38)
        self.IRIClfList.append(Class)

        # FSM 10: WebSocket Client - side by using autobahn+asyncio in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py",
                              "WebSocket Client - side by using autobahn+asyncio in python")
        S44 = State(44,
                    "import asyncio|from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory|from autobahn.websocket import connect",
                    "Step 1: Import necessary modules for Autobahn and asyncio WebSocket client")
        S45 = State(45, "WebSocketClientProtocol",
                    "Step 2: Define a custom class that inherits from WebSocketClientProtocol to handle WebSocket client behavior")
        S46 = State(46, "onConnect|onOpen|onMessage|onClose",
                    "Step 3: Implement WebSocket lifecycle methods such as onConnect, onOpen, onMessage, and onClose")
        S47 = State(47, "WebSocketClientFactory",
                    "Step 4: Create a WebSocketClientFactory instance to manage client - side WebSocket connections")
        S48 = State(48, "get_event_loop()|create_connection",
                    "Step 5: Set up the asyncio event loop and create the client connection")
        S49 = State(49, "run_until_complete|run_forever", "Step 6: Start the event loop to run the client continuously")
        # State transitions for the FSM
        S44.AddNext(S45)
        S45.AddNext(S46)
        S46.AddNext(S47)
        S47.AddNext(S48)
        S48.AddNext(S49)
        # Add state to the server classifier
        Class.AddState(S44)
        self.IRIClfList.append(Class)

        # FSM 11: HTTP Server - side by using http.server in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "HTTP Server - side by using http.server in python")
        S50 = State(50, "from http.server import HTTPServer|from http.server import BaseHTTPRequestHandler",
                    "Step 1: Import HTTPServer and BaseHTTPRequestHandler from the http.server module")
        S51 = State(51, "BaseHTTPRequestHandler",
                    "Step 2: Define a custom request handler class by extending BaseHTTPRequestHandler")
        S52 = State(52, "do_GET|do_POST|do_PUT|do_DELETE|do_HEAD",
                    "Step 3: Override request handling methods such as do_GET or do_POST")
        S53 = State(53, "HTTPServer", "Step 4: Create an HTTPServer instance with the handler class and server address")
        S54 = State(54, "serve_forever()",
                    "Step 5: Start the server to handle requests indefinitely using serve_forever()")
        # State transitions for the FSM
        S50.AddNext(S51)
        S51.AddNext(S52)
        S52.AddNext(S53)
        S53.AddNext(S54)
        # Add state to the server classifier
        Class.AddState(S50)
        self.IRIClfList.append(Class)

        # FSM 12: HTTP Client - side by using http.client in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "HTTP Client - side by using http.client in python")
        S55 = State(55, "from http.client import HTTPConnection|HTTPSConnection",
                    "Step 1: Import HTTPConnection or HTTPSConnection")
        S56 = State(56, "HTTPConnection|HTTPSConnection",
                    "Step 2: Create a connection object with the target server and port")
        S57 = State(57, "request|GET|POST|PUT|DELETE",
                    "Step 3: Send an HTTP request using request(method, url, body, headers)")
        S58 = State(58, "getresponse", "Step 4: Receive and process the HTTP response")
        S59 = State(59, "close", "Step 5: Close the connection")
        # State transitions for the FSM
        S55.AddNext(S56)
        S56.AddNext(S57)
        S57.AddNext(S58)
        S58.AddNext(S59)
        # Add state to the server classifier
        Class.AddState(S55)
        self.IRIClfList.append(Class)

        # FSM 13: HTTP Client-side by using requests in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "HTTP Client-side by using requests in python")
        S60 = State(60, "import requests",
                    "Step 1: Import the requests module to enable HTTP client functionality.")
        S61 = State(61, "requests.get|requests.post|requests.put|requests.delete",
                    "Step 2: Send an HTTP request using the appropriate method such as GET, POST, PUT, or DELETE.")
        S62 = State(62, "response.status_code",
                    "Step 3: Check the HTTP response status code to determine if the request was successful.")
        S63 = State(63, "response.text|response.json|response.content|response.headers|response.cookies",
                    "Step 4: Parse the response data using properties like .text, .json(), .content, .headers, or .cookies.")

        # State transitions for the FSM
        S60.AddNext(S61)
        S61.AddNext(S62)
        S62.AddNext(S63)
        # Add state to the classifier
        Class.AddState(S60)
        self.IRIClfList.append(Class)

        # FSM 14: Synchronous HTTP Client-side by using httpx in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "HTTP Client-side by using httpx in python")
        S64 = State(64, "import httpx", "Step 1: Import the httpx library")
        S65 = State(65, "with httpx.Client", "Step 2: Create a synchronous HTTP client using a context manager")
        S66 = State(66, "get|post|put|delete",
                    "Step 3: Send HTTP requests using supported methods like GET, POST, PUT, DELETE")
        S67 = State(67, "status_code|text|json|content|headers|cookies|raise_for_status",
                    "Step 4: Access response properties such as status code, body content, headers, cookies, or raise exceptions")
        # State transitions for the FSM
        S64.AddNext(S65)
        S65.AddNext(S66)
        S66.AddNext(S67)
        # Add state to the server classifier
        Class.AddState(S64)
        self.IRIClfList.append(Class)

        # FSM 15: Asynchronous HTTP Client-side by using httpx+asyncio in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "HTTP Client-side by using httpx+asyncio in python")
        S68 = State(68, "import httpx|import asyncio", "Step 1: Import httpx and asyncio libraries")
        S69 = State(69, "async with httpx.AsyncClient",
                    "Step 2: Create an asynchronous HTTP client using a context manager")
        S70 = State(70, "get|post|put|delete",
                    "Step 3: Send HTTP requests asynchronously using methods like GET, POST, PUT, DELETE")
        S71 = State(71, "status_code|text|json|content|headers|cookies|raise_for_status",
                    "Step 4: Access response details or raise exceptions on non-success status codes")
        # State transitions for the FSM
        S68.AddNext(S69)
        S69.AddNext(S70)
        S70.AddNext(S71)
        # Add state to the server classifier
        Class.AddState(S68)
        self.IRIClfList.append(Class)

        # FSM 16: HTTP Server - side by using Flask in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "HTTP Server - side by using Flask in python")
        S72 = State(72, "import flask|from flask import Flask|from flask import request|from flask import jsonify",
                    "Step 1: Import the required Flask modules")
        S73 = State(73, "Flask", "Step 2: Instantiate the Flask application object")
        S74 = State(74, "route", "Step 3: Define routes with @app.route decorators")
        S75 = State(75, "get_json|get|post|form|get_data",
                    "Step 4: Handle incoming request data using Flask's request object")
        S76 = State(76, "return", "Step 5: Create and return the response")
        # FSM transitions
        S72.AddNext(S73)
        S73.AddNext(S74)
        S74.AddNext(S75)
        S75.AddNext(S76)
        # Add state to the server classifier
        Class.AddState(S72)
        self.IRIClfList.append(Class)

        # FSM 17: HTTP Server - side by using FastAPI in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "HTTP Server - side by using FastAPI in python")
        S77 = State(77, "from fastapi import FastAPI|from fastapi import.*",
                    "Step 1: Import FastAPI and necessary components from the FastAPI module")
        S78 = State(78, "FastAPI()",
                    "Step 2: Instantiate the FastAPI application object, which will handle HTTP requests")
        S79 = State(79, "get|post|put|delete",
                    "Step 3: Define route handlers using decorators (e.g., get, post) for each HTTP method")
        S80 = State(80, "BaseModel",
                    "Step 4: Optionally, define request and response models using Pydantic BaseModel for validation")
        S81 = State(81, "Query|Path|Body",
                    "Step 5: Extract query parameters, path variables, and request body using FastAPI's parameter extraction mechanisms")
        S82 = State(82, "return",
                    "Step 6: Return the response from the route handler, typically as JSON or using FastAPI's built - in response classes")
        # State transitions
        S77.AddNext(S78)
        S78.AddNext(S79)
        S79.AddNext(S80)
        S80.AddNext(S81)
        S81.AddNext(S82)
        # Add state to the server classifier
        Class.AddState(S77)
        self.IRIClfList.append(Class)

        # FSM 18: HTTP Server - side by using Tornado in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "HTTP Server - side by using Tornado in python")
        S83 = State(83, "import tornado.ioloop|import tornado.web", "Step 1: Import Tornado I/O loop and web modules")
        S84 = State(84, "tornado.web.RequestHandler", "Step 2: Define request handler class to handle HTTP requests")
        S85 = State(85, "Application", "Step 3: Create Tornado application and define route mappings")
        S86 = State(86, "tornado.httpserver.HTTPServer",
                    "Step 4: Create HTTP server using the Tornado HTTPServer class")
        S87 = State(87, "bind", "Step 5: Bind server to a specific port")
        S88 = State(88, "start()", "Step 6: Start the Tornado server to handle incoming requests")
        # State transitions
        S83.AddNext(S84)
        S84.AddNext(S85)
        S85.AddNext(S86)
        S86.AddNext(S87)
        S87.AddNext(S88)
        # Add state to the server classifier
        Class.AddState(S83)
        self.IRIClfList.append(Class)

        # FSM 19: HTTP Client - side by using Tornado in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "HTTP Client - side by using Tornado in python")
        S89 = State(89, "import tornado.ioloop|import tornado.httpclient",
                    "Step 1: Import necessary modules for HTTP client and I/O loop")
        S90 = State(90, "httpclient.AsyncHTTPClient()",
                    "Step 2: Instantiate an asynchronous HTTP client using Tornado's AsyncHTTPClient")
        S91 = State(91, "await http_client.fetch", "Step 3: Perform asynchronous HTTP request using the fetch method")
        S92 = State(92, "tornado.httpclient.HTTPError", "Step 4: Handle any HTTP errors using the HTTPError exception")
        S93 = State(93, "run_sync",
                    "Step 5: Run the asynchronous code synchronously using Tornado's IOLoop's run_sync method")
        # State transitions
        S89.AddNext(S90)
        S90.AddNext(S91)
        S91.AddNext(S92)
        S92.AddNext(S93)
        # Add state to the server classifier
        Class.AddState(S89)
        self.IRIClfList.append(Class)

        # FSM 20: HTTP Server - side by using Sanic in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "HTTP Server - side by using Sanic in python")
        S94 = State(94, "from sanic import.*|from sanic.response import.*",
                    "Step 1: Import necessary modules from Sanic")
        S95 = State(95, "Sanic", "Step 2: Instantiate the Sanic app object")
        S96 = State(96, "route", "Step 3: Define routes using the @app.route decorator")
        S97 = State(97, "async def", "Step 4: Define asynchronous route handlers")
        S98 = State(98, "text|html|file|stream|redirect|empty|json",
                    "Step 5: Return appropriate response types such as text, HTML, file, stream, redirect, empty, or JSON")
        # State transitions
        S94.AddNext(S95)
        S95.AddNext(S96)
        S96.AddNext(S97)
        S97.AddNext(S98)
        # Add state to the server classifier
        Class.AddState(S94)
        self.IRIClfList.append(Class)

        # FSM 21: HTTP Server - side by using Sanic in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "HTTP Server - side by using Sanic in python")
        S99 = State(99,
                    "from starlette.responses import.*|from starlette.requests import Request|from starlette.applications import Starlette|from starlette.routing import Route|import uvicorn",
                    "Step 1: Import necessary modules from Starlette")
        S100 = State(100, "async def|Request", "Step 2: Define asynchronous route handlers and request objects")
        S101 = State(101,
                     "JSONResponse|PlainTextResponse|HTMLResponse|RedirectResponse|FileResponse|StreamingResponse|UJSONResponse|Response",
                     "Step 3: Return appropriate response types such as JSON, plain text, HTML, redirect, file, streaming, etc.")
        S102 = State(102, "Route", "Step 4: Define routes using the Route object")
        S103 = State(103, "Starlette", "Step 5: Instantiate the Starlette application")
        S104 = State(104, "run", "Step 6: Run the application with uvicorn")
        # State transitions
        S99.AddNext(S100)
        S100.AddNext(S101)
        S101.AddNext(S102)
        S102.AddNext(S103)
        S103.AddNext(S104)
        # Add state to the server classifier
        Class.AddState(S99)
        self.IRIClfList.append(Class)

        # FSM 22: TCP Server - side by using socket in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "TCP Server - side by using socket in python")
        S105 = State(105, "import socket", "Step 1: Import the socket module")
        S106 = State(106, "socket(socket.AF_INET, socket.SOCK_STREAM)", "Step 2: Create a TCP socket object using IPv4")
        S107 = State(107, "bind", "Step 3: Bind the socket to a local IP address and port")
        S108 = State(108, "listen", "Step 4: Start listening for incoming client connections")
        S109 = State(109, "accept()", "Step 5: Accept a connection request from a client")
        S110 = State(110, "recv|send", "Step 6: Receive data from or send data to the client")
        S111 = State(111, "close", "Step 7: Close the connection with the client")
        # State transitions
        S105.AddNext(S106)
        S106.AddNext(S107)
        S107.AddNext(S108)
        S108.AddNext(S109)
        S109.AddNext(S110)
        S110.AddNext(S111)
        # Add state to the server classifier
        Class.AddState(S105)
        self.IRIClfList.append(Class)

        # FSM 23: TCP Client - side by using socket in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "TCP Client - side by using socket in python")
        S112 = State(112, "import socket", "Step 1: Import the socket module")
        S113 = State(113, "socket(socket.AF_INET, socket.SOCK_STREAM)", "Step 2: Create a TCP socket object using IPv4")
        S114 = State(114, "connect", "Step 3: Connect the socket to the target server's IP and port")
        S115 = State(115, "send|recv", "Step 4: Send data to or receive data from the server")
        S116 = State(116, "close", "Step 5: Close the connection with the server")
        # State transitions
        S112.AddNext(S113)
        S113.AddNext(S114)
        S114.AddNext(S115)
        S115.AddNext(S116)
        # Add state to the server classifier
        Class.AddState(S112)
        self.IRIClfList.append(Class)

        # FSM 24: UDP communication by using socket in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "UDP communication by using socket in python")
        S117 = State(117, "import socket", "Step 1: Import the socket module")
        S118 = State(118, "socket(socket.AF_INET, socket.SOCK_DGRAM)", "Step 2: Create a UDP socket")
        S119 = State(119, "bind", "Step 3: Bind the socket to a local IP address and port (server - side only)")
        S120 = State(120, "sendto|recvfrom|recvfrom_into",
                     "Step 4: Send and receive data using appropriate UDP methods")
        S121 = State(121, "close()", "Step 5: Close the socket to release resources")
        # State transitions
        S117.AddNext(S118)
        S118.AddNext(S119)
        S119.AddNext(S120)
        S120.AddNext(S121)
        # Add state to the server classifier
        Class.AddState(S117)
        self.IRIClfList.append(Class)

        # FSM 25: TCP Client - side by using asyncio in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "TCP Client - side by using asyncio in python")
        S122 = State(122, "import asyncio",
                     "Step 1: Import the asyncio module to work with asynchronous I/O operations.")
        S123 = State(123, "read|decode|write",
                     "Step 2: Read data from the socket, decode it if necessary, or write data to the socket.")
        S124 = State(124, "start_server",
                     "Step 3: Start the server to listen for incoming connections and establish communication.")
        S125 = State(125, "serve_forever", "Step 4: Keep the server running indefinitely to handle incoming requests.")
        # State transitions
        S122.AddNext(S123)
        S123.AddNext(S124)
        S124.AddNext(S125)
        # Add state to the server classifier
        Class.AddState(S122)
        self.IRIClfList.append(Class)

        # FSM 26: TCP Client - side by using asyncio in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "TCP Client - side by using asyncio in python")
        S126 = State(126, "import asyncio",
                     "Step 1: Import the asyncio module for handling asynchronous network operations.")
        S127 = State(127, "open_connection",
                     "Step 2: Open a connection to the target server and prepare for data exchange.")
        S128 = State(128, "write|read", "Step 3: Send or receive data over the connection.")
        S129 = State(129, "run", "Step 4: Start the event loop to execute the asynchronous tasks.")
        # State transitions
        S126.AddNext(S127)
        S127.AddNext(S128)
        S128.AddNext(S129)
        # Add state to the server classifier
        Class.AddState(S126)
        self.IRIClfList.append(Class)

        # FSM 27: TCP Server - side by using twisted in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "TCP Server - side by using Twisted in python")
        S130 = State(130,
                     "from twisted.internet.protocol import Protocol, Factory|from twisted.internet import reactor",
                     "Step 1: Import Protocol, Factory, and reactor")
        S131 = State(131, "Protocol",
                     "Step 2: Define a Protocol subclass to handle incoming data and connection events")
        S132 = State(132, "Factory", "Step 3: Define a Factory subclass and implement buildProtocol")
        S133 = State(133, "listenTCP", "Step 4: Bind server to a port using reactor.listenTCP(port, factory)")
        S134 = State(134, "run", "Step 5: Start the Twisted event loop with reactor.run()")
        S130.AddNext(S131)
        S131.AddNext(S132)
        S132.AddNext(S133)
        S133.AddNext(S134)
        Class.AddState(S130)
        self.IRIClfList.append(Class)

        # FSM 28: TCP Client - side by using twisted in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "TCP Client - side by using Twisted in python")
        S135 = State(135,
                     "from twisted.internet.protocol import Protocol, ClientFactory|from twisted.internet import reactor",
                     "Step 1: Import Protocol, ClientFactory, and reactor")
        S136 = State(136, "Protocol", "Step 2: Define a Protocol subclass to handle connection logic and data I/O")
        S137 = State(137, "ClientFactory", "Step 3: Define a ClientFactory subclass and implement buildProtocol")
        S138 = State(138, "connectTCP", "Step 4: Establish connection with reactor.connectTCP(host, port, factory)")
        S139 = State(139, "run", "Step 5: Start the Twisted event loop with reactor.run()")
        # State transitions
        S135.AddNext(S136)
        S136.AddNext(S137)
        S137.AddNext(S138)
        S138.AddNext(S139)
        # Add state to the server classifier
        Class.AddState(S135)
        self.IRIClfList.append(Class)

        # FSM 29: TCP Server - side by using socketserver in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "TCP Server - side by using socketserver in python")
        S140 = State(140, "import socketserver|from socketserver import.*",
                     "Step 1: Import socketserver module and its components.")
        S141 = State(141, "BaseRequestHandler", "Step 2: Define a handler class that inherits from BaseRequestHandler.")
        S142 = State(142, "handle", "Step 3: Implement the handle method to process client requests.")
        S143 = State(143, "recv|send|sendall|write|read",
                     "Step 4: Use methods like recv(), send(), sendall(), write(), or read() to communicate with the client.")
        S144 = State(144, "TCPServer",
                     "Step 5: Create a TCP server instance using TCPServer and bind it to an address.")
        S145 = State(145, "serve_forever()", "Step 6: Call serve_forever() to start the server and keep it running.")
        # State transitions
        S140.AddNext(S141)
        S141.AddNext(S142)
        S142.AddNext(S143)
        S143.AddNext(S144)
        S144.AddNext(S145)
        # Add state to the server classifier
        Class.AddState(S140)
        self.IRIClfList.append(Class)

        # FSM 30: UDP Server - side by using socketserver in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "UDP Server - side by using socketserver in python")
        S146 = State(146, "import socketserver|from socketserver import.*",
                     "Step 1: Import socketserver module and its components.")
        S147 = State(147, "BaseRequestHandler", "Step 2: Define a handler class that inherits from BaseRequestHandler.")
        S148 = State(148, "handle", "Step 3: Implement the handle method to process client requests.")
        S149 = State(149, "recv|send|sendall|write|read",
                     "Step 4: Use methods like recv(), send(), sendall(), write(), or read() to communicate with the client.")
        S150 = State(150, "UDPServer",
                     "Step 5: Create a UDP server instance using UDPServer and bind it to an address.")
        S151 = State(151, "serve_forever()", "Step 6: Call serve_forever() to start the server and keep it running.")
        # State transitions
        S146.AddNext(S147)
        S147.AddNext(S148)
        S148.AddNext(S149)
        S149.AddNext(S150)
        S150.AddNext(S151)
        # Add state to the server classifier
        Class.AddState(S146)
        self.IRIClfList.append(Class)

        # FSM 31: gRPC Server - side based on grpcio in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "gRPC Server - side based on grpcio in python")
        S152 = State(152, "import grpc|from concurrent import futures",
                     "Step 1: Import necessary libraries (grpc and futures) for server creation")
        S153 = State(153, "grpc.server|futures.ThreadPoolExecutor",
                     "Step 2: Create a gRPC server with a thread pool executor for concurrency")
        S154 = State(154, "add_insecure_port", "Step 3: Bind the server to a port using add_insecure_port method")
        S155 = State(155, "start()", "Step 4: Start the server to begin listening for incoming gRPC requests")
        # State transitions
        S152.AddNext(S153)
        S153.AddNext(S154)
        S154.AddNext(S155)
        # Add state to the server classifier
        Class.AddState(S152)
        self.IRIClfList.append(Class)

        # FSM 32: DBus Server - side based on dbus(Method invoke) in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py",
                              "DBus Server - side based on dbus(Method invoke) in python")
        S156 = State(156, "import dbus|import dbus.service|import dbus.mainloop.glib|from gi.repository import GLib",
                     "Step 1: Import necessary libraries for D - Bus service and event loop")
        S157 = State(157, "DBusGMainLoop",
                     "Step 2: Initialize the D - Bus main loop to handle asynchronous communication")
        S158 = State(158, "dbus.service.Object",
                     "Step 3: Create a D - Bus service object that exposes methods and signals")
        S159 = State(159, "@dbus.service.method",
                     "Step 4: Define a method using dbus.service.method decorator to expose it for client calls")
        S160 = State(160, "SessionBus()", "Step 5: Connect to the D - Bus session bus to interact with other services")
        S161 = State(161, "BusName", "Step 6: Register the service name on the bus so clients can discover the service")
        S162 = State(162, "MainLoop()|run()", "Step 7: Start the event loop to handle incoming method calls")
        # State transitions
        S156.AddNext(S157)
        S157.AddNext(S158)
        S158.AddNext(S159)
        S159.AddNext(S160)
        S160.AddNext(S161)
        S161.AddNext(S162)
        # Add state to the server classifier
        Class.AddState(S156)
        self.IRIClfList.append(Class)

        # FSM 33: DBus Client - side based on dbus(Method invoke) in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py",
                              "DBus Client - side based on dbus(Method invoke) in python")
        S163 = State(163, "import dbus", "Step 1: Import the dbus module to interact with the D - Bus system")
        S164 = State(164, "SessionBus()", "Step 2: Connect to the session bus to access user - level D - Bus services")
        S165 = State(165, "get_object", "Step 3: Obtain a remote object that implements the desired D - Bus interface")
        S166 = State(166, "get_dbus_method",
                     "Step 4: Retrieve a method from the object and call it to interact with the D - Bus service")
        # State transitions
        S163.AddNext(S164)
        S164.AddNext(S165)
        S165.AddNext(S166)
        # Add state to the server classifier
        Class.AddState(S163)
        self.IRIClfList.append(Class)

        # FSM 34: DBus Server - side based on dbus (Signal) in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "DBus Server - side based on dbus (Signal) in python")
        S167 = State(167, "import dbus|import dbus.service|import dbus.mainloop.glib|from gi.repository import GLib",
                     "Step 1: Import necessary libraries for D - Bus service and event loop")
        S168 = State(168, "DBusGMainLoop",
                     "Step 2: Initialize the D - Bus main loop to handle asynchronous communication")
        S169 = State(169, "dbus.service.Object",
                     "Step 3: Create a D - Bus service object to expose methods and signals")
        S170 = State(170, "@dbus.service.signal",
                     "Step 4: Define a signal using dbus.service.signal decorator to allow clients to listen for this signal")
        S171 = State(171, "SessionBus()", "Step 5: Connect to the D - Bus session bus to interact with other services")
        S172 = State(172, "BusName", "Step 6: Register the service name on the bus so clients can discover the service")
        S173 = State(173, "emit_signal",
                     "Step 7: Emit the signal at appropriate times to notify clients of changes or events")
        S174 = State(174, "MainLoop()|run()",
                     "Step 8: Start the event loop to handle incoming method calls and signal emissions")
        # State transitions
        S167.AddNext(S168)
        S168.AddNext(S169)
        S169.AddNext(S170)
        S170.AddNext(S171)
        S171.AddNext(S172)
        S172.AddNext(S173)
        S173.AddNext(S174)
        # Add state to the server classifier
        Class.AddState(S167)
        self.IRIClfList.append(Class)

        # FSM 35: DBus Client - side based on dbus(Signal) in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "DBus Client - side based on dbus (Signal) in python")
        S175 = State(175, "import dbus", "Step 1: Import necessary D - Bus library")
        S176 = State(176, "SessionBus()", "Step 2: Initialize the D - Bus session bus to interact with the service")
        S177 = State(177, "get_object", "Step 3: Get the D - Bus service object that exposes signals")
        S178 = State(178, "connect_to_signal",
                     "Step 4: Connect to the signal using dbus.connect_to_signal to listen for signal emissions")
        S179 = State(179, "loop", "Step 5: Start the main loop to listen for signals asynchronously")
        # State transitions
        S175.AddNext(S176)
        S176.AddNext(S177)
        S177.AddNext(S178)
        S178.AddNext(S179)
        # Add state to the client classifier
        Class.AddState(S175)
        self.IRIClfList.append(Class)

        # FSM 36: Pipe based on subprocess in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Pipe based on subprocess in python")
        S180 = State(180, "import subprocess", "Step 1: Import the subprocess module to interact with system processes")
        S181 = State(181, "PIPE", "Step 2: Use subprocess.PIPE to create a pipe for communication between processes")
        S182 = State(182, "Popen",
                     "Step 3: Start a new process using subprocess.Popen and connect to the pipe for input/output")
        S183 = State(183, "communicate()",
                     "Step 4: Use the communicate() method to send data to the process and retrieve the output")
        # State transitions
        S180.AddNext(S181)
        S181.AddNext(S182)
        S182.AddNext(S183)
        # Add state to the client classifier
        Class.AddState(S180)
        self.IRIClfList.append(Class)

        # FSM 37: RabbitMQ producer based on pika in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "RabbitMQ producer based on pika in python")
        S184 = State(184, "import pika", "Step 1: Import the pika library for RabbitMQ communication")
        S185 = State(185, "BlockingConnection", "Step 2: Establish a blocking connection to the RabbitMQ server")
        S186 = State(186, "channel()", "Step 3: Open a channel on the connection to perform messaging operations")
        S187 = State(187, "queue_declare", "Step 4: Declare a queue to ensure it exists before sending messages")
        S188 = State(188, "basic_publish", "Step 5: Publish a message to the declared queue")
        S189 = State(189, "close", "Step 6: Close the connection to free up resources")
        # State transitions
        S184.AddNext(S185)
        S185.AddNext(S186)
        S186.AddNext(S187)
        S187.AddNext(S188)
        S188.AddNext(S189)
        # Add state to the client classifier
        Class.AddState(S184)
        self.IRIClfList.append(Class)

        # FSM 38: RabbitMQ consumer based on pika in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "RabbitMQ consumer based on pika in python")
        S190 = State(190, "import pika", "Step 1: Import the pika library to consume messages from RabbitMQ")
        S191 = State(191, "BlockingConnection", "Step 2: Connect to the RabbitMQ server using a blocking connection")
        S192 = State(192, "channel()", "Step 3: Open a channel to start message consumption")
        S193 = State(193, "queue_declare", "Step 4: Declare the queue from which messages will be consumed")
        S194 = State(194, "basic_consume", "Step 5: Set up the callback function to handle incoming messages")
        S195 = State(195, "start_consuming", "Step 6: Start consuming messages in a blocking event loop")
        # State transitions
        S190.AddNext(S191)
        S191.AddNext(S192)
        S192.AddNext(S193)
        S193.AddNext(S194)
        S194.AddNext(S195)
        # Add state to the client classifier
        Class.AddState(S190)
        self.IRIClfList.append(Class)

        # FSM 39: Async RabbitMQ producer based on aio_pika in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Async RabbitMQ producer based on aio_pika in python")
        S196 = State(196, "import asyncio|from aio_pika import.*|import aio_pika",
                     "Step 1: Import necessary asyncio and aio_pika modules for asynchronous messaging")
        S197 = State(197, "await connect_robust",
                     "Step 2: Establish a robust asynchronous connection to the RabbitMQ broker")
        S198 = State(198, "channel()", "Step 3: Create an asynchronous channel for communication")
        S199 = State(199, "declare_exchange|queue_declare",
                     "Step 4: Declare the exchange and optionally a queue for routing messages")
        S200 = State(200, "queue_bind", "Step 5: Bind the queue to the exchange using a specific routing key")
        S201 = State(201, "publish", "Step 6: Asynchronously publish a message to the declared exchange")
        S202 = State(202, "close", "Step 7: Close the connection cleanly when done")
        # State transitions
        S196.AddNext(S197)
        S197.AddNext(S198)
        S198.AddNext(S199)
        S199.AddNext(S200)
        S200.AddNext(S201)
        S201.AddNext(S202)
        # Add state to the client classifier
        Class.AddState(S196)
        self.IRIClfList.append(Class)

        # FSM 40: Async RabbitMQ cosumer based on aio_pika in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Async RabbitMQ consumer based on aio_pika in python")
        S203 = State(203, "import asyncio|from aio_pika import.*|import aio_pika",
                     "Step 1: Import asyncio and aio_pika to support asynchronous consumption")
        S204 = State(204, "await connect_robust",
                     "Step 2: Asynchronously connect to the RabbitMQ broker using a robust method")
        S205 = State(205, "channel()", "Step 3: Create a channel to receive messages from")
        S206 = State(206, "declare_exchange|queue_declare",
                     "Step 4: Declare the exchange and the queue to receive messages")
        S207 = State(207, "queue_bind", "Step 5: Bind the declared queue to the exchange with a routing key")
        S208 = State(208, "consume", "Step 6: Start consuming messages asynchronously using a callback handler")
        S209 = State(209, "Future()", "Step 7: Keep the consumer running indefinitely with an asyncio Future")
        # State transitions
        S203.AddNext(S204)
        S204.AddNext(S205)
        S205.AddNext(S206)
        S206.AddNext(S207)
        S207.AddNext(S208)
        S208.AddNext(S209)
        # Add state to the client classifier
        Class.AddState(S203)
        self.IRIClfList.append(Class)

        # FSM 41: Kafka producer in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Kafka producer in python")
        S210 = State(210, "from kafka import KafkaProducer|import kafka",
                     "Step 1: Import the Kafka client library and required modules")
        S211 = State(211, "KafkaProducer",
                     "Step 2: Create a KafkaProducer instance with appropriate configurations (e.g., bootstrap_servers)")
        S212 = State(212, "send|flush",
                     "Step 3: Send messages to a specific topic and flush the buffer to ensure delivery")
        S213 = State(213, "close", "Step 4: Close the producer to release resources properly")
        # State transitions
        S210.AddNext(S211)
        S211.AddNext(S212)
        S212.AddNext(S213)
        # Add state to the client classifier
        Class.AddState(S210)
        self.IRIClfList.append(Class)

        # FSM 42: Kafka consumer in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Kafka consumer in python")
        S214 = State(214, "from kafka import KafkaConsumer| import kafka",
                     "Step 1: Import the Kafka client library for consumer functionality")
        S215 = State(215, "KafkaConsumer",
                     "Step 2: Create a KafkaConsumer instance, subscribe to one or more topics, and poll for messages")
        S216 = State(216, "close", "Step 3: Close the consumer to properly clean up resources")
        # State transitions
        S214.AddNext(S215)
        S215.AddNext(S216)
        # Add state to the client classifier
        Class.AddState(S214)
        self.IRIClfList.append(Class)

        # FSM 43: Async Kafka producer based on asyncio+aiokafka in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Async Kafka producer in python")
        S217 = State(217, "import asyncio|from aiokafka import AIOKafkaProducer|import aiokafka",
                     "Step 1: Import asyncio and aiokafka to enable asynchronous Kafka message production")
        S218 = State(218, "AIOKafkaProducer",
                     "Step 2: Create an AIOKafkaProducer instance with bootstrap servers and optional configurations")
        S219 = State(219, "start()", "Step 3: Start the asynchronous Kafka producer to initialize the connection")
        S220 = State(220, "send_and_wait", "Step 4: Send a message to a specific topic and wait until it is delivered")
        S221 = State(221, "stop()", "Step 5: Gracefully stop the producer and close the connection")
        # State transitions
        S217.AddNext(S218)
        S218.AddNext(S219)
        S219.AddNext(S220)
        S220.AddNext(S221)
        # Add state to the client classifier
        Class.AddState(S217)
        self.IRIClfList.append(Class)

        # FSM 44: Async Kafka consumer based on asyncio+aiokafka in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Async Kafka consumer in python")
        S222 = State(222, "import asyncio|from aiokafka import AIOKafkaConsumer|import aiokafka",
                     "Step 1: Import asyncio and aiokafka to enable asynchronous Kafka message consumption")
        S223 = State(223, "AIOKafkaConsumer",
                     "Step 2: Create an AIOKafkaConsumer instance, subscribe to topics, and configure group ID")
        S224 = State(224, "start()",
                     "Step 3: Start the consumer to establish the connection and begin fetching messages")
        S225 = State(225, "stop()", "Step 4: Gracefully stop the consumer and close the connection")
        # State transitions
        S222.AddNext(S223)
        S223.AddNext(S224)
        S224.AddNext(S225)
        # Add state to the client classifier
        Class.AddState(S222)
        self.IRIClfList.append(Class)

        # FSM 45: ActiveMQ Producer in Python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "ActiveMQ Producer in Python")
        S226 = State(226, "import stomp", "Step 1: Import the stomp.py module for STOMP protocol communication")
        S227 = State(227, "stomp.Connection", "Step 2: Create a connection object and define broker address/port")
        S228 = State(228, "connect", "Step 3: Establish connection with broker using credentials")
        S229 = State(229, "send", "Step 4: Send message to the specified queue or topic")
        S230 = State(230, "disconnect", "Step 5: Gracefully close the connection")
        # State transitions
        S226.AddNext(S227)
        S227.AddNext(S228)
        S228.AddNext(S229)
        S229.AddNext(S230)
        # Add state to the client classifier
        Class.AddState(S226)
        self.IRIClfList.append(Class)

        # FSM 46: ActiveMQ Consumer in Python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "ActiveMQ Consumer in Python")
        S231 = State(231, "import stomp", "Step 1: Import the stomp.py module for STOMP protocol communication")
        S232 = State(232, "Connection", "Step 2: Create a connection object and define broker address/port")
        S233 = State(233, "set_listener", "Step 3: Set a custom listener to handle incoming messages")
        S234 = State(234, "connect", "Step 4: Establish connection with broker using credentials")
        S235 = State(235, "subscribe", "Step 5: Subscribe to the queue or topic to receive messages")
        S236 = State(236, "disconnect", "Step 6: Gracefully close the connection (optional)")
        # State transitions
        S231.AddNext(S232)
        S232.AddNext(S233)
        S233.AddNext(S234)
        S234.AddNext(S235)
        S235.AddNext(S236)
        # Add state to the client classifier
        Class.AddState(S231)
        self.IRIClfList.append(Class)

        # FSM 47: Async ActiveMQ Consumer in Python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "ActiveMQ Consumer in Python")
        S237 = State(237, "import asyncio|import aio_stomp",
                     "Step 1: Import necessary libraries for asynchronous messaging.")
        S238 = State(238, "AioStomp", "Step 2: Initialize the AioStomp client for ActiveMQ communication.")
        S239 = State(239, "connect", "Step 3: Establish a connection to the ActiveMQ server.")
        S240 = State(240, "send", "Step 4: Send a message to the ActiveMQ server.")
        S241 = State(241, "disconnect", "Step 5: Disconnect from the ActiveMQ server.")
        # State transitions
        S237.AddNext(S238)
        S238.AddNext(S239)
        S239.AddNext(S240)
        S240.AddNext(S241)
        # Add state to the client classifier
        Class.AddState(S237)
        self.IRIClfList.append(Class)

        # FSM 48: Async ActiveMQ Consumer in Python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "ActiveMQ Consumer in Python")
        S242 = State(242, "import asyncio|import aio_stomp",
                     "Step 1: Import necessary libraries for asynchronous messaging.")
        S243 = State(243, "set_listener|AioStompListener", "Step 2: Set up a listener to handle incoming messages.")
        S244 = State(244, "connect", "Step 3: Establish a connection to the ActiveMQ server.")
        S245 = State(245, "subscribe", "Step 4: Subscribe to a specific queue/topic to receive messages.")
        # State transitions
        S242.AddNext(S243)
        S243.AddNext(S244)
        S244.AddNext(S245)
        # Add state to the client classifier
        Class.AddState(S242)
        self.IRIClfList.append(Class)

        # FSM 49: Redis List Producer
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Redis List Producer in Python")
        S246 = State(246, "import redis", "Step 1: Import the redis - py library to interact with Redis")
        S247 = State(247, "connect", "Step 2: Establish connection to the Redis server")
        S248 = State(248, "rpush|lpush|rpushx|lpushx",
                     "Step 3: Use RPUSH/LPUSH/RPUSHX/LPUSHX to add messages to the Redis list")
        S249 = State(249, "disconnect", "Step 4: Close the Redis connection")
        # State transitions
        S246.AddNext(S247)
        S247.AddNext(S248)
        S248.AddNext(S249)
        Class.AddState(S246)
        self.IRIClfList.append(Class)

        # FSM 50: Redis Pub/Sub Producer
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Redis Pub/Sub Producer in Python")
        S250 = State(250, "import redis", "Step 1: Import the redis - py library to interact with Redis")
        S251 = State(251, "connect", "Step 2: Establish connection to the Redis server")
        S252 = State(252, "publish", "Step 3: Use PUBLISH to send message to a Redis channel")
        S253 = State(253, "disconnect", "Step 4: Close the Redis connection")
        # State transitions
        S250.AddNext(S251)
        S251.AddNext(S252)
        S252.AddNext(S253)
        Class.AddState(S250)
        self.IRIClfList.append(Class)

        # FSM 51: Redis Sorted Set Producer
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Redis Sorted Set Producer in Python")
        S254 = State(254, "import redis", "Step 1: Import the redis - py library to interact with Redis")
        S255 = State(255, "connect", "Step 2: Establish connection to the Redis server")
        S256 = State(256, "zadd", "Step 3: Use ZADD to add message to a sorted set with a score")
        S257 = State(257, "disconnect", "Step 4: Close the Redis connection")
        # State transitions
        S254.AddNext(S255)
        S255.AddNext(S256)
        S256.AddNext(S257)
        Class.AddState(S254)
        self.IRIClfList.append(Class)

        # FSM 52: Redis Stream Producer
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Redis Stream Producer in Python")
        S258 = State(258, "import redis", "Step 1: Import the redis - py library to interact with Redis")
        S259 = State(259, "connect", "Step 2: Establish connection to the Redis server")
        S260 = State(260, "xadd", "Step 3: Use XADD to add message to a Redis stream")
        S261 = State(261, "disconnect", "Step 4: Close the Redis connection")
        # State transitions
        S258.AddNext(S259)
        S259.AddNext(S260)
        S260.AddNext(S261)
        Class.AddState(S258)
        self.IRIClfList.append(Class)

        # FSM 53: Redis List Consumer
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Redis List Consumer in Python")
        S262 = State(262, "import redis", "Step 1: Import the redis - py library to interact with Redis")
        S263 = State(263, "connect", "Step 2: Establish connection to the Redis server")
        S264 = State(264, "blpop|brpop", "Step 3: Use BLPOP or BRPOP to retrieve a message from the Redis list")
        S265 = State(265, "disconnect", "Step 4: Close the Redis connection")
        # State transitions
        S262.AddNext(S263)
        S263.AddNext(S264)
        S264.AddNext(S265)
        Class.AddState(S262)
        self.IRIClfList.append(Class)

        # FSM 54: Redis Pub/Sub Consumer
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Redis Pub/Sub Consumer in Python")
        S266 = State(266, "import redis", "Step 1: Import the redis - py library to interact with Redis")
        S267 = State(267, "connect", "Step 2: Establish connection to the Redis server")
        S268 = State(268, "subscribe", "Step 3: Use SUBSCRIBE or PSUBSCRIBE to subscribe to channels")
        S269 = State(269, "listen", "Step 4: Listen for incoming messages on the subscribed channels")
        S270 = State(270, "disconnect", "Step 5: Close the Redis connection")
        # State transitions
        S266.AddNext(S267)
        S267.AddNext(S268)
        S268.AddNext(S269)
        S269.AddNext(S270)
        Class.AddState(S266)
        self.IRIClfList.append(Class)

        # FSM 55: Redis Sorted Set Consumer
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Redis Sorted Set Consumer in Python")
        S271 = State(271, "import redis", "Step 1: Import the redis - py library to interact with Redis")
        S272 = State(272, "connect", "Step 2: Establish connection to the Redis server")
        S273 = State(273, "zrange|zpopmin", "Step 3: Use ZRANGE or ZPOPMIN to get messages from the sorted set")
        S274 = State(274, "disconnect", "Step 4: Close the Redis connection")
        # State transitions
        S271.AddNext(S272)
        S272.AddNext(S273)
        S273.AddNext(S274)
        Class.AddState(S271)
        self.IRIClfList.append(Class)

        # FSM 56: Redis Stream Consumer
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Redis Stream Consumer in Python")
        S275 = State(275, "import redis", "Step 1: Import the redis - py library to interact with Redis")
        S276 = State(276, "connect", "Step 2: Establish connection to the Redis server")
        S277 = State(277, "xread|xreadgroup", "Step 3: Use XREAD or XREADGROUP to read messages from the Redis stream")
        S278 = State(278, "disconnect", "Step 4: Close the Redis connection")
        # State transitions
        S275.AddNext(S276)
        S276.AddNext(S277)
        S277.AddNext(S278)
        Class.AddState(S275)
        self.IRIClfList.append(Class)

        # FSM 57: Async Redis List Producer
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Async Redis List Producer in Python")
        S279 = State(279, "import aioredis", "Step 1: Import the aioredis library for asynchronous Redis operations")
        S280 = State(280, "create_redis|create_redis_pool",
                     "Step 2: Establish asynchronous connection to the Redis server using create_redis() or create_redis_pool()")
        S281 = State(281, "rpush|lpush|rpushx|lpushx",
                     "Step 3: Use RPUSH/LPUSH/RPUSHX/LPUSHX to add messages to the Redis list asynchronously")
        S282 = State(282, "disconnect", "Step 4: Close the Redis connection asynchronously")
        # State transitions
        S279.AddNext(S280)
        S280.AddNext(S281)
        S281.AddNext(S282)
        Class.AddState(S279)
        self.IRIClfList.append(Class)

        # FSM 58: Async Redis Pub/Sub Producer
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Async Redis Pub/Sub Producer in Python")
        S283 = State(283, "import aioredis", "Step 1: Import the aioredis library for asynchronous Redis operations")
        S284 = State(284, "create_redis",
                     "Step 2: Establish asynchronous connection to the Redis server using create_redis()")
        S285 = State(285, "publish", "Step 3: Use PUBLISH to send message to a Redis channel asynchronously")
        S286 = State(286, "disconnect", "Step 4: Close the Redis connection asynchronously")
        # State transitions
        S283.AddNext(S284)
        S284.AddNext(S285)
        S285.AddNext(S286)
        Class.AddState(S283)
        self.IRIClfList.append(Class)

        # FSM 59: Async Redis Sorted Set Producer
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Async Redis Sorted Set Producer in Python")
        S287 = State(287, "import aioredis", "Step 1: Import the aioredis library for asynchronous Redis operations")
        S288 = State(288, "create_redis|create_redis_pool",
                     "Step 2: Establish asynchronous connection to the Redis server using create_redis() or create_redis_pool()")
        S289 = State(289, "zadd", "Step 3: Use ZADD to add message to a sorted set with a score asynchronously")
        S290 = State(290, "disconnect", "Step 4: Close the Redis connection asynchronously")
        # State transitions
        S287.AddNext(S288)
        S288.AddNext(S289)
        S289.AddNext(S290)
        Class.AddState(S287)
        self.IRIClfList.append(Class)

        # FSM 60: Async Redis Stream Producer
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Async Redis Stream Producer in Python")
        S291 = State(291, "import aioredis", "Step 1: Import the aioredis library for asynchronous Redis operations")
        S292 = State(292, "create_redis|create_redis_pool",
                     "Step 2: Establish asynchronous connection to the Redis server using create_redis() or create_redis_pool()")
        S293 = State(293, "xadd", "Step 3: Use XADD to add message to a Redis stream asynchronously")
        S294 = State(294, "disconnect", "Step 4: Close the Redis connection asynchronously")
        # State transitions
        S291.AddNext(S292)
        S292.AddNext(S293)
        S293.AddNext(S294)
        Class.AddState(S291)
        self.IRIClfList.append(Class)

        # FSM 61: Async Redis List Consumer
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Async Redis List Consumer in Python")
        S294 = State(294, "import aioredis", "Step 1: Import the aioredis library for asynchronous Redis operations")
        S295 = State(295, "create_redis|create_redis_pool",
                     "Step 2: Establish asynchronous connection to the Redis server using create_redis() or create_redis_pool()")
        S296 = State(296, "blpop|brpop",
                     "Step 3: Use BLPOP or BRPOP to retrieve a message from the Redis list asynchronously")
        S297 = State(297, "disconnect", "Step 4: Close the Redis connection asynchronously")
        # State transitions
        S294.AddNext(S295)
        S295.AddNext(S296)
        S296.AddNext(S297)
        Class.AddState(S294)
        self.IRIClfList.append(Class)

        # FSM 62: Async Redis Pub/Sub Consumer
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Async Redis Pub/Sub Consumer in Python")
        S298 = State(298, "import aioredis", "Step 1: Import the aioredis library for asynchronous Redis operations")
        S299 = State(299, "create_redis|create_redis_pool",
                     "Step 2: Establish asynchronous connection to the Redis server using create_redis() or create_redis_pool()")
        S300 = State(300, "subscribe", "Step 3: Use SUBSCRIBE or PSUBSCRIBE to subscribe to channels asynchronously")
        S301 = State(301, "listen", "Step 4: Listen for incoming messages on the subscribed channels asynchronously")
        S302 = State(302, "disconnect", "Step 5: Close the Redis connection asynchronously")
        # State transitions
        S298.AddNext(S299)
        S299.AddNext(S300)
        S300.AddNext(S301)
        S301.AddNext(S302)
        Class.AddState(S298)
        self.IRIClfList.append(Class)

        # FSM 63: Async Redis Sorted Set Consumer
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Async Redis Sorted Set Consumer in Python")
        S303 = State(303, "import aioredis", "Step 1: Import the aioredis library for asynchronous Redis operations")
        S304 = State(304, "create_redis|create_redis_pool",
                     "Step 2: Establish asynchronous connection to the Redis server using create_redis() or create_redis_pool()")
        S305 = State(305, "zrange|zpopmin",
                     "Step 3: Use ZRANGE or ZPOPMIN to get messages from the sorted set asynchronously")
        S306 = State(306, "disconnect", "Step 4: Close the Redis connection asynchronously")
        # State transitions
        S303.AddNext(S304)
        S304.AddNext(S305)
        S305.AddNext(S306)
        Class.AddState(S303)
        self.IRIClfList.append(Class)

        # FSM 64: Async Redis Stream Consumer
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Async Redis Stream Consumer in Python")
        S307 = State(307, "import aioredis", "Step 1: Import the aioredis library for asynchronous Redis operations")
        S308 = State(308, "create_redis|create_redis_pool",
                     "Step 2: Establish asynchronous connection to the Redis server using create_redis() or create_redis_pool()")
        S309 = State(309, "xread|xreadgroup",
                     "Step 3: Use XREAD or XREADGROUP to read messages from the Redis stream asynchronously")
        S310 = State(310, "disconnect", "Step 4: Close the Redis connection asynchronously")
        # State transitions
        S307.AddNext(S308)
        S308.AddNext(S309)
        S309.AddNext(S310)
        Class.AddState(S307)
        self.IRIClfList.append(Class)

        # FSM 65: ZeroMQ Producer in Python(REQ/REP)
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "ZeroMQ Producer in Python(REQ/REP)")
        S311 = State(311, "import zmq", "Step 1: Import the zmq library for ZeroMQ functionalities")
        S312 = State(312, "zmq.Context()", "Step 2: Create a ZeroMQ context for managing sockets")
        S313 = State(313, "socket(zmq.REQ)", "Step 3: Create a REQ socket for sending requests")
        S314 = State(314, "connect", "Step 4: Connect the REQ socket to the server endpoint")
        S315 = State(315,
                     "send|recv|send_multipart|recv_multipart|send_json|recv_json|send_string|recv_string|send_pyobj|recv_pyobj",
                     "Step 5: Send a request and wait for a reply using send/recv methods")
        S316 = State(316, "close()|term()", "Step 6: Close the socket and terminate the ZeroMQ context")
        # State transitions
        S311.AddNext(S312)
        S312.AddNext(S313)
        S313.AddNext(S314)
        S314.AddNext(S315)
        S315.AddNext(S316)
        Class.AddState(S311)
        self.IRIClfList.append(Class)

        # FSM 66: ZeroMQ Consumer in Python(REQ/REP)
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "ZeroMQ Consumer in Python(REQ/REP)")
        S317 = State(317, "import zmq", "Step 1: Import the zmq library for ZeroMQ functionalities")
        S318 = State(318, "zmq.Context()", "Step 2: Create a ZeroMQ context for managing sockets")
        S319 = State(319, "socket(zmq.REP)", "Step 3: Create a REP socket for responding to requests")
        S320 = State(320, "bind", "Step 4: Bind the REP socket to an endpoint to listen for incoming requests")
        S321 = State(321,
                     "send|recv|send_multipart|recv_multipart|send_json|recv_json|send_string|recv_string|send_pyobj|recv_pyobj",
                     "Step 5: Receive a request and send a reply using send/recv methods")
        S322 = State(322, "close()|term()", "Step 6: Close the socket and terminate the ZeroMQ context")
        # State transitions
        S317.AddNext(S318)
        S318.AddNext(S319)
        S319.AddNext(S320)
        S320.AddNext(S321)
        S321.AddNext(S322)
        Class.AddState(S317)
        self.IRIClfList.append(Class)

        # FSM 67: ZeroMQ Producer in Python(PUB/SUB)
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "ZeroMQ Producer in Python(PUB/SUB)")
        S323 = State(323, "import zmq", "Step 1: Import the zmq library for ZeroMQ functionalities")
        S324 = State(324, "zmq.Context()", "Step 2: Create a ZeroMQ context for managing sockets")
        S325 = State(325, "socket(zmq.PUB)", "Step 3: Create a PUB socket to publish messages")
        S326 = State(326, "bind", "Step 4: Bind the PUB socket to an endpoint to start sending messages")
        S327 = State(327,
                     "send|recv|send_multipart|recv_multipart|send_json|recv_json|send_string|recv_string|send_pyobj|recv_pyobj",
                     "Step 5: Send messages using send/recv methods, typically using send for publishing")
        S328 = State(328, "close()|term()", "Step 6: Close the socket and terminate the ZeroMQ context")
        # State transitions
        S323.AddNext(S324)
        S324.AddNext(S325)
        S325.AddNext(S326)
        S326.AddNext(S327)
        S327.AddNext(S328)
        Class.AddState(S323)
        self.IRIClfList.append(Class)

        # FSM 68: ZeroMQ Consumer in Python(PUB/SUB)
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "ZeroMQ Consumer in Python(PUB/SUB)")
        S329 = State(329, "import zmq", "Step 1: Import the zmq library for ZeroMQ functionalities")
        S330 = State(330, "zmq.Context()", "Step 2: Create a ZeroMQ context for managing sockets")
        S331 = State(331, "socket(zmq.SUB)", "Step 3: Create a SUB socket to subscribe to messages")
        S332 = State(332, "connect", "Step 4: Connect the SUB socket to the publisher's endpoint")
        S333 = State(333,
                     "send|recv|send_multipart|recv_multipart|send_json|recv_json|send_string|recv_string|send_pyobj|recv_pyobj",
                     "Step 5: Receive messages from the publisher using recv methods")
        S334 = State(334, "close()|term()", "Step 6: Close the socket and terminate the ZeroMQ context")
        # State transitions
        S329.AddNext(S330)
        S330.AddNext(S331)
        S331.AddNext(S332)
        S332.AddNext(S333)
        S333.AddNext(S334)
        Class.AddState(S329)
        self.IRIClfList.append(Class)

        # FSM 69: ZeroMQ Producer in Python(PUSH/PULL)
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "ZeroMQ Producer in Python(PUSH/PULL)")
        S335 = State(335, "import zmq", "Step 1: Import the zmq library for ZeroMQ functionalities")
        S336 = State(336, "zmq.Context()", "Step 2: Create a ZeroMQ context for managing sockets")
        S337 = State(337, "socket(zmq.PUSH)", "Step 3: Create a PUSH socket to send messages")
        S338 = State(338, "bind", "Step 4: Bind the PUSH socket to an endpoint to start sending messages")
        S339 = State(339,
                     "send|recv|send_multipart|recv_multipart|send_json|recv_json|send_string|recv_string|send_pyobj|recv_pyobj",
                     "Step 5: Send messages using send methods")
        S340 = State(340, "close()|term()", "Step 6: Close the socket and terminate the ZeroMQ context")
        # State transitions
        S335.AddNext(S336)
        S336.AddNext(S337)
        S337.AddNext(S338)
        S338.AddNext(S339)
        S339.AddNext(S340)
        Class.AddState(S335)
        self.IRIClfList.append(Class)

        # FSM 70: ZeroMQ Consumer in Python(PUSH/PULL)
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "ZeroMQ Consumer in Python(PUSH/PULL)")
        S341 = State(341, "import zmq", "Step 1: Import the zmq library for ZeroMQ functionalities")
        S342 = State(342, "zmq.Context()", "Step 2: Create a ZeroMQ context for managing sockets")
        S343 = State(343, "socket(zmq.PULL)", "Step 3: Create a PULL socket to receive messages")
        S344 = State(344, "connect", "Step 4: Connect the PULL socket to the PUSH socket endpoint")
        S345 = State(345,
                     "send|recv|send_multipart|recv_multipart|send_json|recv_json|send_string|recv_string|send_pyobj|recv_pyobj",
                     "Step 5: Receive messages using recv methods")
        S346 = State(346, "close()|term()", "Step 6: Close the socket and terminate the ZeroMQ context")
        # State transitions
        S341.AddNext(S342)
        S342.AddNext(S343)
        S343.AddNext(S344)
        S344.AddNext(S345)
        S345.AddNext(S346)
        Class.AddState(S341)
        self.IRIClfList.append(Class)

        # FSM 71: ZeroMQ Producer in Python(DEALER/ROUTER)
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "ZeroMQ Producer in Python(DEALER/ROUTER)")
        S347 = State(347, "import zmq", "Step 1: Import the zmq library for ZeroMQ functionalities")
        S348 = State(348, "zmq.Context()", "Step 2: Create a ZeroMQ context for managing sockets")
        S349 = State(349, "socket(zmq.DEALER)", "Step 3: Create a DEALER socket to manage multiple requests")
        S350 = State(350, "connect", "Step 4: Connect the DEALER socket to the server endpoint")
        S351 = State(351,
                     "send|recv|send_multipart|recv_multipart|send_json|recv_json|send_string|recv_string|send_pyobj|recv_pyobj",
                     "Step 5: Send and receive requests using send/recv methods")
        S352 = State(352, "close()|term()", "Step 6: Close the socket and terminate the ZeroMQ context")
        # State transitions
        S347.AddNext(S348)
        S348.AddNext(S349)
        S349.AddNext(S350)
        S350.AddNext(S351)
        S351.AddNext(S352)
        Class.AddState(S347)
        self.IRIClfList.append(Class)

        # FSM 72: ZeroMQ Consumer in Python(DEALER/ROUTER)
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "ZeroMQ Consumer in Python(DEALER/ROUTER)")
        S353 = State(353, "import zmq", "Step 1: Import the zmq library for ZeroMQ functionalities")
        S354 = State(354, "zmq.Context()", "Step 2: Create a ZeroMQ context for managing sockets")
        S355 = State(355, "socket(zmq.ROUTER)",
                     "Step 3: Create a ROUTER socket to receive messages. Note: There was an error in the original, it should be ROUTER instead of PULL for DEALER/ROUTER pattern")
        S356 = State(356, "bind", "Step 4: Bind the ROUTER socket to the endpoint to receive messages")
        S357 = State(357,
                     "send|recv|send_multipart|recv_multipart|send_json|recv_json|send_string|recv_string|send_pyobj|recv_pyobj",
                     "Step 5: Receive and process messages using recv methods")
        S358 = State(358, "close()|term()", "Step 6: Close the socket and terminate the ZeroMQ context")
        # State transitions
        S353.AddNext(S354)
        S354.AddNext(S355)
        S355.AddNext(S356)
        S356.AddNext(S357)
        S357.AddNext(S358)
        Class.AddState(S353)
        self.IRIClfList.append(Class)

        # FSM 73: Mosquitto Producer based on mqtt in Python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Mosquitto Producer based on mqtt in Python")
        S359 = State(359, "import paho.mqtt.client", "Step 1: Import the Paho MQTT client library")
        S360 = State(360, "Client", "Step 2: Create an MQTT client instance")
        S361 = State(361, "on_connect|connect",
                     "Step 3: Define connection callback and establish connection to the broker")
        S362 = State(362, "publish", "Step 4: Publish a message to a specific topic")
        S363 = State(363, "loop_start()", "Step 5: Start the MQTT loop to handle network traffic asynchronously")
        # State transitions
        S359.AddNext(S360)
        S360.AddNext(S361)
        S361.AddNext(S362)
        S362.AddNext(S363)
        Class.AddState(S359)
        self.IRIClfList.append(Class)

        # FSM 74: Mosquitto Consumer based on mqtt in Python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Mosquitto Consumer based on mqtt in Python")
        S364 = State(364, "import paho.mqtt.client", "Step 1: Import the Paho MQTT client library")
        S365 = State(365, "Client", "Step 2: Create an MQTT client instance")
        S366 = State(366, "on_connect|connect",
                     "Step 3: Define connection callback and establish connection to the broker")
        S367 = State(367, "subscribe|on_message",
                     "Step 4: Subscribe to topics and define a callback function to handle incoming messages")
        S368 = State(368, "loop_forever",
                     "Step 5: Start the MQTT loop to handle network traffic and process incoming messages continuously")
        # State transitions
        S364.AddNext(S365)
        S365.AddNext(S366)
        S366.AddNext(S367)
        S367.AddNext(S368)
        Class.AddState(S364)
        self.IRIClfList.append(Class)

        # FSM 13: HTTP Client-side by using requests in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "HTTP Client-side by using requests in python")
        S369 = State(369, "import requests",
                     "Step 1: Import the requests module to enable HTTP client functionality.")
        S370 = State(370, "requests.get|requests.post|requests.put|requests.delete",
                     "Step 2: Send an HTTP request using the appropriate method such as GET, POST, PUT, or DELETE.")
        S371 = State(371, "response.status_code",
                     "Step 3: Check the HTTP response status code to determine if the request was successful.")
        S372 = State(372, "response.text|response.json|response.content|response.headers|response.cookies",
                     "Step 4: Parse the response data using properties like .text, .json(), .content, .headers, or .cookies.")

        # State transitions for the FSM
        S369.AddNext(S370)
        S370.AddNext(S371)
        S371.AddNext(S372)
        # Add state to the classifier
        Class.AddState(S369)
        self.IRIClfList.append(Class)

        ############################################################
        # Class: JavaScript*
        ############################################################
        # FSM 1: WebSocket Client-side based on browser native API in JavaScript
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js .ts .html",
                              "WebSocket Client-side based on browser native API in JavaScript")
        S0 = State(0, "new WebSocket", "Step 1: Initialize a new WebSocket connection.")
        S1 = State(1, "onopen|onmessage|onerror|onbeforeunload",
                   "Step 2: Define event handlers for connection, messages, errors, and before window unload.")
        S2 = State(2, "send|log|error|close",
                   "Step 3: Send messages, log errors, handle connection errors, and close the WebSocket connection.")
        # State transitions for the FSM
        S0.AddNext(S1)
        S1.AddNext(S2)
        # Add state to the classifier
        Class.AddState(S0)
        self.IRIClfList.append(Class)

        # FSM 2: WebSocket Server-side based on Node.js
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js .ts .html", "WebSocket Server-side based on Node.js")
        S3 = State(3, "require('ws')", "Step 1: Require the WebSocket library ('ws').")
        S4 = State(4, "new WebSocket.Server", "Step 2: Create a new WebSocket server instance.")
        S5 = State(5, "connection|message|error|close",
                   "Step 3: Define event handlers for connection, messages, errors, and closing the server.")
        # State transitions for the FSM
        S3.AddNext(S4)
        S4.AddNext(S5)
        # Add state to the classifier
        Class.AddState(S3)
        self.IRIClfList.append(Class)

        # FSM 3: WebSocket Client-side based on Node.js
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js .ts .html", "WebSocket Client-side based on Node.js")
        S6 = State(6, "require('ws')", "Step 1: Require the WebSocket library ('ws').")
        S7 = State(7, "new WebSocket", "Step 2: Create a new WebSocket connection on the server.")
        S8 = State(8, "connection|message|error|close",
                   "Step 3: Define event handlers for connection, messages, errors, and closing the WebSocket.")
        # State transitions for the FSM
        S6.AddNext(S7)
        S7.AddNext(S8)
        # Add state to the classifier
        Class.AddState(S6)
        self.IRIClfList.append(Class)

        # FSM 4: WebSocket Server-side based on socket.io in JavaScript
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js .ts .html",
                              "WebSocket Server-side based on socket.io in JavaScript")
        S9 = State(9, "require('http')|require('socket.io')",
                   "Step 1: Import the necessary modules (http and socket.io).")
        S10 = State(10, "createServer", "Step 2: Create an HTTP server to handle incoming requests.")
        S11 = State(11, "socketIo", "Step 3: Bind socket.io to the HTTP server for WebSocket communication.")
        S12 = State(12, "connection|message|disconnect|listen",
                    "Step 4: Set up event listeners for 'connection','message', 'disconnect' events and start the server.")
        # State transitions for the FSM
        S9.AddNext(S10)
        S10.AddNext(S11)
        S11.AddNext(S12)
        # Add state to the classifier
        Class.AddState(S9)
        self.IRIClfList.append(Class)

        # FSM 5: HTTP Server - side based on XMLHttpRequest in JavaScript
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js.ts.html",
                              "HTTP Server - side based on XMLHttpRequest in JavaScript")
        S13 = State(13, "new XMLHttpRequest()", "Step 1: Create a new XMLHttpRequest object to initiate the request.")
        S14 = State(14, "open",
                    "Step 2: Configure the request with the `open()` method, defining the request type (GET, POST) and the URL.")
        S15 = State(15, "setRequestHeader",
                    "Step 3: Optionally, set the request headers using `setRequestHeader()` for specific content types.")
        S16 = State(16, "onreadystatechange",
                    "Step 4: Set up an `onreadystatechange` event listener to handle the response when the request completes.")
        S17 = State(17, "send", "Step 5: Send the request to the server using the `send()` method.")

        # State transitions for the FSM
        S13.AddNext(S14)
        S14.AddNext(S15)
        S15.AddNext(S16)
        S16.AddNext(S17)
        # Add state to the classifier
        Class.AddState(S13)
        self.IRIClfList.append(Class)

        # FSM 6: Node.js HTTP Server with JSON data processing
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js", "Node.js HTTP Server with JSON data processing")
        S18 = State(18, "require('http')|require('url')|require('string_decoder')",
                    "Step 1: Import http, url and decoder modules")
        S19 = State(19, "http.createServer", "Step 2: Create HTTP server and handle incoming requests")
        S20 = State(20, "url.parse", "Step 3: Parse incoming request URL and method")
        S21 = State(21, "on('data')|on('end')", "Step 4: Collect and decode incoming request body")
        S22 = State(22, "JSON.parse", "Step 5: Parse request body into JSON format")
        S23 = State(23, "routes", "Step 6: Route request to appropriate handler based on path")
        S24 = State(24, "res.writeHead|res.end", "Step 7: Send JSON response to the client")
        S25 = State(25, "server.listen", "Step 8: Start listening on a specific port")
        # State transitions
        S18.AddNext(S19)
        S19.AddNext(S20)
        S20.AddNext(S21)
        S21.AddNext(S22)
        S22.AddNext(S23)
        S23.AddNext(S24)
        S24.AddNext(S25)
        # Add state to the classifier
        Class.AddState(S18)
        self.IRIClfList.append(Class)

        # FSM 7: Node.js HTTP Client with JSON data processing
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js", "Node.js HTTP Client with JSON data processing")
        S26 = State(26, "require('http')", "Step 1: Import HTTP core module")
        S27 = State(27, "http.request", "Step 2: Create and configure HTTP request object")
        S28 = State(28, "req.write", "Step 3: Write JSON payload to request body for POST")
        S29 = State(29, "req.end", "Step 4: Finalize and send the HTTP request")
        S30 = State(30, "res.on('data')|res.on('end')", "Step 5: Receive and buffer response data")
        S31 = State(31, "JSON.parse", "Step 6: Parse response string into JSON object")
        S32 = State(32, "Promise|async", "Step 7: Handle asynchronous control flow using Promise/async")
        S33 = State(33, "req.on('error')", "Step 8: Handle HTTP or network level errors")
        # State transitions
        S26.AddNext(S27)
        S27.AddNext(S28)
        S28.AddNext(S29)
        S29.AddNext(S30)
        S30.AddNext(S31)
        S31.AddNext(S32)
        S32.AddNext(S33)
        # Add state to the classifier
        Class.AddState(S26)
        self.IRIClfList.append(Class)

        # FSM 8: HTTP Client-side based on Axios
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js.ts.html", "HTTP Client-side based on Axios")
        S34 = State(34, "require('axios')", "Step 1: Import the axios library to enable HTTP client functionality")
        S35 = State(35, "get|post|put|delete",
                    "Step 2: Choose and initiate the HTTP method for the request (GET, POST, etc.)")
        S36 = State(36, "URL|headers|params|data",
                    "Step 3: Configure the request with URL, headers, query parameters, and payload")
        S37 = State(37, "catch", "Step 4: Handle errors using catch block or error callback")
        # State transitions for the FSM
        S34.AddNext(S35)
        S35.AddNext(S36)
        S36.AddNext(S37)
        # Add state to the classifier
        Class.AddState(S34)
        self.IRIClfList.append(Class)

        # FSM 9: HTTP Client - side based on request in javascript
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js.ts.html",
                              "HTTP Client - side based on request in javascript")
        S38 = State(38, "require('request')", "Step 1: Import the request module")
        S39 = State(39, "request|get|post|put|delete", "Step 2: Call request method such as request.get/post/etc")
        S40 = State(40, "url|method|headers|body|json|form|formData",
                    "Step 3: Configure HTTP options like URL, headers, and data")
        S41 = State(41, "callback", "Step 4: Handle the HTTP response via callback")
        # State transitions for the FSM
        S38.AddNext(S39)
        S39.AddNext(S40)
        S40.AddNext(S41)
        # Add state to the classifier
        Class.AddState(S38)
        self.IRIClfList.append(Class)

        # FSM 10: HTTP based on express in javascript
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js.ts.html", "HTTP based on express in javascript")
        S42 = State(42, "require('express')", "Step 1: Import the Express framework module.")
        S43 = State(43, "express()", "Step 2: Create an Express application instance.")
        S44 = State(44, "use", "Step 3: Configure middleware for request processing.")
        S45 = State(45, "get|post|put|delete", "Step 4: Define route handlers for HTTP methods.")
        S46 = State(46, "listen", "Step 5: Start the server and listen on a specified port.")
        # State transitions for the FSM
        S42.AddNext(S43)
        S43.AddNext(S44)
        S44.AddNext(S45)
        S45.AddNext(S46)
        # Add state to the classifier
        Class.AddState(S42)
        self.IRIClfList.append(Class)

        # FSM 11: TCP Server - side based on node.js net
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js.ts.html", "TCP Server - side based on node.js net")
        S47 = State(47, "require('net')", "Step 1: Import the built - in 'net' module.")
        S48 = State(48, "createServer()", "Step 2: Create a TCP server instance.")
        S49 = State(49, "listen", "Step 3: Start listening on a specific port.")
        S50 = State(50, "connection|listening|close|error",
                    "Step 4: Handle server lifecycle events and client connections.")
        # State transitions for the FSM
        S47.AddNext(S48)
        S48.AddNext(S49)
        S49.AddNext(S50)
        # Add state to the classifier
        Class.AddState(S47)
        self.IRIClfList.append(Class)

        # FSM 12: TCP Client - side based on node.js net
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js.ts.html", "TCP Client - side based on node.js net")
        S51 = State(51, "require('net')", "Step 1: Import the built - in 'net' module.")
        S52 = State(52, "new net.Socket()", "Step 2: Create a new TCP socket instance.")
        S53 = State(53, "connect", "Step 3: Connect to the remote TCP server.")
        S54 = State(54, "on('connect')|on('data')", "Step 4: Handle connection and incoming data events.")
        # State transitions for the FSM
        S51.AddNext(S52)
        S52.AddNext(S53)
        S53.AddNext(S54)
        # Add state to the classifier
        Class.AddState(S51)
        self.IRIClfList.append(Class)

        # FSM 13: UDP based on node.js dgram
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js.ts.html", "UDP based on node.js dgram")
        S55 = State(55, "require('dgram')", "Step 1: Import the built - in 'dgram' module.")
        S56 = State(56, "createSocket('udp4')|createSocket('udp6')", "Step 2: Create a UDP socket for IPv4 or IPv6.")
        S57 = State(57, "message|listening|error",
                    "Step 3: Handle socket events such as incoming messages, binding status, and errors.")
        S58 = State(58, "bind", "Step 4: Bind the socket to a local port and optionally a specific address.")
        # State transitions for the FSM
        S55.AddNext(S56)
        S56.AddNext(S57)
        S57.AddNext(S58)
        # Add state to the classifier
        Class.AddState(S55)
        self.IRIClfList.append(Class)

        # FSM 14: gRPC Server - side based on @grpc/grpc - js
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js.ts.html", "gRPC Server - side based on @grpc/grpc - js")
        S59 = State(59, "require('@grpc/grpc - js')",
                    "Step 1: Import the @grpc/grpc - js library to set up the gRPC server.")
        S60 = State(60, "Server()", "Step 2: Create a new instance of the gRPC server.")
        S61 = State(61, "addService",
                    "Step 3: Add the service definition to the server, linking the service with its implementation.")
        S62 = State(62, "bindAsync",
                    "Step 4: Bind the server to a specific port asynchronously, specifying the address and options.")
        S63 = State(63, "start", "Step 5: Start the server to begin listening for incoming requests.")
        # State transitions for the FSM
        S59.AddNext(S60)
        S60.AddNext(S61)
        S61.AddNext(S62)
        S62.AddNext(S63)
        # Add state to the classifier
        Class.AddState(S59)
        self.IRIClfList.append(Class)

        # FSM 15: Dbus Server-side based on dbus-next
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js.ts.html", "Dbus Server-side based on dbus-next")
        S64 = State(64, "require('dbus-next')", "Step 1: Import the dbus-next library to interact with the D-Bus.")
        S65 = State(65, "sessionBus()",
                    "Step 2: Connect to the session bus to enable communication with other applications.")
        S66 = State(66, "export",
                    "Step 3: Export a method or service interface, making it available to other applications.")
        S67 = State(67, "requestName",
                    "Step 4: Request a unique name for the service, ensuring no conflicts with existing services.")
        # State transitions for the FSM
        S64.AddNext(S65)
        S65.AddNext(S66)
        S66.AddNext(S67)
        # Add state to the classifier
        Class.AddState(S64)
        self.IRIClfList.append(Class)

        # FSM 16: gRPC Client-side based on dbus-next
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js.ts.html", "gRPC Client-side based on dbus-next")
        S68 = State(68, "require('dbus-next')",
                    "Step 1: Import the dbus-next library to interact with the D-Bus as a client.")
        S69 = State(69, "sessionBus()",
                    "Step 2: Connect to the session bus to initiate communication with D-Bus services.")
        S70 = State(70, "invoke|addMatch",
                    "Step 3: Invoke remote method calls or add match filters to listen for specific D-Bus signals.")
        # State transitions for the FSM
        S68.AddNext(S69)
        S69.AddNext(S70)
        # Add state to the classifier
        Class.AddState(S68)
        self.IRIClfList.append(Class)

        # FSM 17: Pipe Client-side based on fs+http in JavaScript
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js.ts.html",
                              "Pipe Client-side based on fs+http in JavaScript")
        S71 = State(71, "require('fs')|require('http')",
                    "Step 1: Import the necessary modules (`fs` for file operations and `http` for making HTTP requests).")
        S72 = State(72, "createReadStream",
                    "Step 2: Create a readable stream from a file using `fs.createReadStream()`.")
        S73 = State(73, "request", "Step 3: Create an HTTP request using `http.request()` to send the file data.")
        S74 = State(74, "pipe",
                    "Step 4: Use `pipe()` to send the file stream data to the HTTP request's writable stream.")
        # State transitions for the FSM
        S71.AddNext(S72)
        S72.AddNext(S73)
        S73.AddNext(S74)
        # Add state to the classifier
        Class.AddState(S71)
        self.IRIClfList.append(Class)

        # FSM 18: Pipe Server-side based on fs+http in JavaScript
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js.ts.html",
                              "Pipe Server-side based on fs+http in JavaScript")
        S75 = State(75, "require('fs')|require('http')",
                    "Step 1: Import the necessary modules (`fs` for file system operations and `http` for creating the server).")
        S76 = State(76, "createServer",
                    "Step 2: Create an HTTP server using `http.createServer()` to handle incoming requests.")
        S77 = State(77, "pipe",
                    "Step 3: Use `pipe()` to pass the request data to a writable stream, such as a file output stream.")
        # State transitions for the FSM
        S75.AddNext(S76)
        S76.AddNext(S77)
        # Add state to the classifier
        Class.AddState(S75)
        self.IRIClfList.append(Class)

        # FSM 19: RabbitMQ Producer based on amqplib in JavaScript
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js.ts.html",
                              "RabbitMQ Producer based on amqplib in JavaScript")
        S78 = State(78, "require('amqplib')", "Step 1: Import the amqplib library to access RabbitMQ functionalities.")
        S79 = State(79, "connect",
                    "Step 2: Establish a connection to the RabbitMQ server using the `connect()` method.")
        S80 = State(80, "createChannel",
                    "Step 3: Create a communication channel using `createChannel()` to send messages.")
        S81 = State(81, "assertQueue",
                    "Step 4: Declare a queue using `assertQueue()` to ensure the queue exists before sending messages.")
        S82 = State(82, "sendToQueue", "Step 5: Use `sendToQueue()` to send messages to the queue.")
        S83 = State(83, "close", "Step 6: Close the connection to RabbitMQ after the message is sent using `close()`.")
        # State transitions for the FSM
        S78.AddNext(S79)
        S79.AddNext(S80)
        S80.AddNext(S81)
        S81.AddNext(S82)
        S82.AddNext(S83)
        # Add state to the classifier
        Class.AddState(S78)
        self.IRIClfList.append(Class)

        # FSM 20: RabbitMQ Consumer based on amqplib in JavaScript
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js.ts.html",
                              "RabbitMQ Consumer based on amqplib in JavaScript")
        S84 = State(84, "require('amqplib')", "Step 1: Import the amqplib library to access RabbitMQ functionalities.")
        S85 = State(85, "connect",
                    "Step 2: Establish a connection to the RabbitMQ server using the `connect()` method.")
        S86 = State(86, "createChannel",
                    "Step 3: Create a communication channel using `createChannel()` to receive messages.")
        S87 = State(87, "assertQueue",
                    "Step 4: Declare the queue using `assertQueue()` to ensure the queue exists for consuming messages.")
        S88 = State(88, "consume", "Step 5: Use the `consume()` method to start consuming messages from the queue.")
        # State transitions for the FSM
        S84.AddNext(S85)
        S85.AddNext(S86)
        S86.AddNext(S87)
        S87.AddNext(S88)
        # Add state to the classifier
        Class.AddState(S84)
        self.IRIClfList.append(Class)

        # FSM 21: Kafka Producer based on kafkajs in JavaScript
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js.ts.html",
                              "Kafka Producer based on kafkajs in JavaScript")
        S89 = State(89, "require('kafkajs')", "Step 1: Import the kafkajs library to access Kafka functionalities.")
        S90 = State(90, "new Kafka", "Step 2: Create a Kafka client instance with the required configuration.")
        S91 = State(91, "producer()", "Step 3: Initialize a Kafka producer from the client instance.")
        S92 = State(92, "connect()", "Step 4: Connect the producer to the Kafka broker.")
        S93 = State(93, "send", "Step 5: Send one or more messages to the specified Kafka topic.")
        S94 = State(94, "disconnect", "Step 6: Disconnect the producer to release resources.")
        # State transitions for the FSM
        S89.AddNext(S90)
        S90.AddNext(S91)
        S91.AddNext(S92)
        S92.AddNext(S93)
        S93.AddNext(S94)
        # Add state to the classifier
        Class.AddState(S89)
        self.IRIClfList.append(Class)

        # FSM 22: Kafka Consumer based on kafkajs in JavaScript
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js.ts.html",
                              "Kafka Consumer based on kafkajs in JavaScript")
        S95 = State(95, "require('kafkajs')", "Step 1: Import the kafkajs library to access Kafka functionalities.")
        S96 = State(96, "new Kafka", "Step 2: Create a Kafka client instance with the required configuration.")
        S97 = State(97, "consumer()", "Step 3: Initialize a Kafka consumer from the client instance with a group ID.")
        S98 = State(98, "connect()", "Step 4: Connect the consumer to the Kafka broker.")
        S99 = State(99, "subscribe", "Step 5: Subscribe the consumer to a specific topic.")
        S100 = State(100, "run", "Step 6: Start consuming messages by providing a message handler function.")
        # State transitions for the FSM
        S95.AddNext(S96)
        S96.AddNext(S97)
        S97.AddNext(S98)
        S98.AddNext(S99)
        S99.AddNext(S100)
        # Add state to the classifier
        Class.AddState(S95)
        self.IRIClfList.append(Class)

        # FSM 23: NATS Producer based on nats in JavaScript
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js.ts.html", "NATS Producer based on nats in JavaScript")
        S101 = State(101, "require('nats')", "Step 1: Import the official 'nats' library.")
        S102 = State(102, "servers", "Step 2: Connect to the NATS server using the 'servers' option.")
        S103 = State(103, "publish|new TextEncoder().encode", "Step 3: Encode and publish a message to a subject.")
        S104 = State(104, "drain", "Step 4: Gracefully close the connection using 'drain()'.")
        # State transitions for the FSM
        S101.AddNext(S102)
        S102.AddNext(S103)
        S103.AddNext(S104)
        # Add state to the classifier
        Class.AddState(S101)
        self.IRIClfList.append(Class)

        # FSM 24: NATS Consumer based on nats in JavaScript
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js.ts.html", "NATS Consumer based on nats in JavaScript")
        S105 = State(105, "require('nats')", "Step 1: Import the official 'nats' library.")
        S106 = State(106, "servers", "Step 2: Connect to the NATS server using the 'servers' option.")
        S107 = State(107, "subscribe", "Step 3: Subscribe to a subject to receive messages.")
        S108 = State(108, "new TextDecoder().decode", "Step 4: Decode the received message data.")
        # State transitions for the FSM
        S105.AddNext(S106)
        S106.AddNext(S107)
        S107.AddNext(S108)
        # Add state to the classifier
        Class.AddState(S105)
        self.IRIClfList.append(Class)

        # FSM 25: Redis based on redis in JavaScript
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js.ts.html", "Redis based on redis in JavaScript")
        S109 = State(109, "require('redis')",
                     "Step 1: Import the 'redis' module to enable Redis client functionalities.")
        S110 = State(110, "createClient()", "Step 2: Create a new Redis client instance using createClient().")
        S111 = State(111, "connect()", "Step 3: Establish a connection to the Redis server.")
        S112 = State(112,
                     "set|get|setex|append|hset|hget|hgetall|hmget|lpush|rpush|lpop|rpop|lrange|sadd|srem|smembers|zadd|zrange|del|keys",
                     "Step 4: Perform Redis operations including String, Hash, List, Set, Sorted Set, and key management commands.")
        S113 = State(113, "quit", "Step 5: Gracefully terminate the Redis client connection.")
        # State transitions for the FSM
        S109.AddNext(S110)
        S110.AddNext(S111)
        S111.AddNext(S112)
        S112.AddNext(S113)
        # Add state to the classifier
        Class.AddState(S109)
        self.IRIClfList.append(Class)

        # FSM 26: Redis Publisher based on redis in JavaScript
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js.ts.html",
                              "Redis Publisher based on redis in JavaScript")
        S114 = State(114, "require('redis')", "Step 1: Import the 'redis' module to access Redis features.")
        S115 = State(115, "createClient()", "Step 2: Create a Redis client instance for publishing messages.")
        S116 = State(116, "connect()", "Step 3: Establish a connection with the Redis server.")
        S117 = State(117, "publish", "Step 4: Send messages to a specific channel using the publish command.")
        S118 = State(118, "quit", "Step 5: Terminate the client connection gracefully.")
        # State transitions
        S114.AddNext(S115)
        S115.AddNext(S116)
        S116.AddNext(S117)
        S117.AddNext(S118)
        # Add state to the classifier
        Class.AddState(S114)
        self.IRIClfList.append(Class)

        # FSM 27: Redis Subscriber based on redis in JavaScript
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js.ts.html",
                              "Redis Subscriber based on redis in JavaScript")
        S119 = State(119, "require('redis')",
                     "Step 1: Import the 'redis' module to set up the subscription functionality.")
        S120 = State(120, "createClient()", "Step 2: Create a Redis client instance for subscribing to channels.")
        S121 = State(121, "duplicate()",
                     "Step 3: Duplicate the client to create a separate connection for subscription.")
        S122 = State(122, "connect()", "Step 4: Establish a connection with the Redis server for the subscriber.")
        S123 = State(123, "subscribe", "Step 5: Subscribe to a channel to begin receiving messages.")
        S124 = State(124, "quit", "Step 6: Close the connection when the subscription is no longer needed.")
        # State transitions
        S119.AddNext(S120)
        S120.AddNext(S121)
        S121.AddNext(S122)
        S122.AddNext(S123)
        S123.AddNext(S124)
        # Add state to the classifier
        Class.AddState(S119)
        self.IRIClfList.append(Class)

        # FSM 28: MQTT in JavaScript
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js.ts.html", "MQTT in JavaScript")
        S125 = State(125, "require('mqtt')", "Step 1: Import the MQTT client library to interact with MQTT broker.")
        S126 = State(126, "connect", "Step 2: Connect to an MQTT broker using the client.connect method.")
        S127 = State(127, "on('connect')|on('subscribe')|on('publish')|on('message')|on('close')",
                     "Step 3: Handle MQTT events like connection, message reception, publishing, and connection closure.")
        S128 = State(128, "end", "Step 4: Close the connection to the MQTT broker using client.end().")
        # State transitions
        S125.AddNext(S126)
        S126.AddNext(S127)
        S127.AddNext(S128)
        # Add state to the classifier
        Class.AddState(S125)
        self.IRIClfList.append(Class)

        ############################################################
        # Class: PHP*
        ############################################################
        # PHP语言面向多编程语言交互的进程间通信方法包括：
        # 套接字技术：TCP/UDP/Websocket
        # 内存共享技术:
        # 消息队列：Redis/Kafka/RabbitMQ/RocketMQ
        # gRPC
        # 文件交互:JSON-RPC/XML-RPC

        ############################################################
        # Class: Go*
        ############################################################
        # Go语言面向多编程语言交互的进程间通信方法包括：
        # 套接字技术：TCP/UDP/Websocket
        # 内存共享技术:
        # 消息队列：Redis/Kafka/RabbitMQ/RocketMQ
        # gRPC
        # 文件交互:Json/CSV/XML



    def InitFfiClass (self):
        ############################################################
        # Class: C and C++
        ############################################################
        Class = ApiClassifier("C-C++", LANG_API_FFI, ".c .cpp", "extern c")
        S0 = State(0, "extern \"C\"", "Step 1: Identify C++ code with extern \"C\" for C linkage.")
        Class.AddState(S0)
        self.FFIClfList.append(Class)







