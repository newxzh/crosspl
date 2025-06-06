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

#Define a series of classifiers/validators
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
                    if len (state.next) == 0: 
                        # MatchList_file => files matched by FSMs
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
                             "css":".css", "assembly":".as", "kotlin":".kt", "swift":".swift","rust":".rs", "perl":".pl", "r":".r", "scala":".scala", "dart":".dart","shell":".sh .zsh .bsh",}
        # Init FFI classifier
        self.InitFfiClass ()
        # Init IRI classifier
        self.InitIriClass ()

    def UpdateFinal(self):
        self.SaveData ()
    def UpdateAnalysis(self, Repo):
        ReppId  = Repo.Id
        ReppName = Repo.Name
        RepoDir = "D:\\CAE\\Splited_Repository" + "\\10\\" + f"{ReppName}_{ReppId}"
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
                bench_info = Bench_Info(Matched_files[0], "Foreign Function Interface(FFI)",Classfier_ID, Clf.name,Clf.interface_name, state_description,"D:\CAE\Repo_Info\Info_FFI_pyc.csv")
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
        Classfier_ID = 148
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
                bench_info = Bench_Info(Matched_files[0], "Inter-Process Communication (IPC)",Classfier_ID, Clf.name,Clf.interface_name, state_description,"D:\CAE\Repo_Info\Info_IRI_C++.csv")
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
        
        # 1. FFI Scan
        RepoDirs = os.walk(Dir)
        for Path, Dirs, Fs in RepoDirs: # Traverse all files under the project directory: Dirs -> all folders in RepoDirs, Fs -> all files under RepoDirs.
            for f in Fs:
                File = os.path.join(Path, f)
                if os.path.exists(File):
                    Clf = self.SnifferByFFI (File)
                    if Clf != None:
                        self.AddScanResult (ClfList, Clf)
                else:
                    continue

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
    def SaveData (self,FileName=None):
        if (len(self.AnalyzStats) == 0):
            return
        SfFile = self.FilePath + self.FileName + '.csv' 
        with open(SfFile, 'a', encoding='utf-8', newline='') as CsvFile:
            writer = csv.writer(CsvFile)
            # self.AnalyzStats.items() -> 
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
        # FSM 1: Recognizing Java ServerSocket Server-side
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "java.net ServerSocket")
        S0 = State(0, "import java.net.*|import java.net.ServerSocket|import java.net.Socket","Step 1: Import necessary networking classes for creating a TCP server")
        S1 = State(1, "new ServerSocket","Step 2: Create a ServerSocket instance to listen for incoming client connections")
        S2 = State(2, "accept", "Step 3: Accept an incoming connection request")
        S3 = State(3, "getInputStream|getOutputStream","Step 4: Obtain input and output streams to send and receive data between server and client")
        S4 = State(4, "close", "Step 5: Close the Socket and release resources after communication is complete")
        # State transitions for the FSM
        S0.AddNext(S1)
        S1.AddNext(S2)
        S2.AddNext(S3)
        S3.AddNext(S4)
        # Add state to the server classifier
        Class.AddState(S0)
        self.IRIClfList.append(Class)

        # FSM 2: Recognizing Java Socket Client-side
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "java.net Socket")
        S5 = State(5, "import java.net.*|import java.net.Socket","Step 1: Import necessary networking classes for creating a TCP client")
        S6 = State(6, "new Socket", "Step 2: Create a Socket instance to establish a connection with the server")
        S7 = State(7, "connect", "Step 3: Initiate a connection request to the server using the Socket instance")
        S8 = State(8, "getInputStream|getOutputStream","Step 4: Obtain input and output streams to send and receive data between client and servers")
        S9 = State(9, "close()", "Step 5: Close the Socket and release resources after communication is complete")
        # State transitions for the FSM
        S5.AddNext(S6)
        S6.AddNext(S7)
        S7.AddNext(S8)
        S8.AddNext(S9)
        # Add state to the client classifier
        Class.AddState(S5)
        self.IRIClfList.append(Class)

        # FSM 3: Recognizing Java using java.net UDP Server-side or Client-side
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "java.net UDP Server or Client")
        S10 = State(10,
                    "import java.net.*|import java.net.DatagramPacket|import java.net.DatagramSocket|import java.net.InetAddress",
                    "Step 1: Import Java networking classes required for UDP communication, including DatagramSocket for handling UDP sockets, DatagramPacket for sending/receiving packets, and InetAddress for managing IP addresses.")
        S11 = State(11, "new DatagramSocket",
                    "Step 2: Create a DatagramSocket instance. On the server-side, bind it to a specific port to listen for incoming packets. On the client-side, use it to send data.")
        S12 = State(12, "new DatagramPacket",
                    "Step 3: Create a DatagramPacket instance. For receiving, allocate a buffer to store incoming data. For sending, specify the target IP address and port.")
        S13 = State(13, "receive|getData|getLength|getOffset|parseData|processData|send",
                    "Step 4: Handle UDP packet transmission. The server calls receive() to wait for incoming packets, extracts data using getData(), and processes it. The client sends data using send().")
        S10.AddNext(S11)
        S11.AddNext(S12)
        S12.AddNext(S13)
        Class.AddState(S10)
        self.IRIClfList.append(Class)

        # # FSM 4: Recognizing Java using Netty TCP Client
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Java Netty TCP Client")
        S14 = State(14,
                    "import io.netty.bootstrap.Bootstrap|import io.netty.channel.*|import io.netty.channel.nio.NioEventLoopGroup|import io.netty.channel.socket.nio.NioSocketChannel",
                    "Step 1: Import Netty libraries, including Bootstrap for client initialization, EventLoopGroup for managing event-driven I/O, Channel for network communication, and NioSocketChannel for handling non-blocking TCP connections.")
        S15 = State(15, "new NioEventLoopGroup()|new Bootstrap()",
                    "Step 2: Initialize an instance of NioEventLoopGroup to manage client-side I/O threads and create a Bootstrap instance to configure Netty's TCP client behavior.")
        S16 = State(16, "NioSocketChannel",
                    "Step 3: Set the Bootstrap's channel type to NioSocketChannel, enabling non-blocking TCP connections and defining a ChannelInitializer to configure the client pipeline.")
        S17 = State(17, "connect",
                    "Step 4: Establish a connection to the remote server using Bootstrap.connect(), and configure the client pipeline with encoders, decoders, and custom handlers for message processing.")
        S18 = State(18, "closeFuture()|shutdownGracefully",
                    "Step 5: Wait for the client connection to close using closeFuture(), then call shutdownGracefully() on EventLoopGroup to release resources and ensure a graceful shutdown.")

        # Define state transitions for FSM
        S14.AddNext(S15)
        S15.AddNext(S16)
        S16.AddNext(S17)
        S17.AddNext(S18)
        # Add states to the classifier
        Class.AddState(S14)
        self.IRIClfList.append(Class)

        # FSM 5: Java Netty TCP Server-side
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Java Netty TCP Server")
        S14 = State(14,
                    "import io.netty.bootstrap.ServerBootstrap|import io.netty.channel.*|import io.netty.channel.nio.NioEventLoopGroup|import io.netty.channel.socket.nio.NioServerSocketChannel",
                    "Step 1: Import Netty's server-related classes, including ServerBootstrap for server setup, EventLoopGroup for managing I/O threads, Channel for TCP communication, and NioServerSocketChannel for non-blocking server transport.")
        S15 = State(15, "new NioEventLoopGroup()|new ServerBootstrap()",
                    "Step 2: Instantiate NioEventLoopGroup to handle server-side event loops and create a ServerBootstrap instance to configure the server’s behavior.")
        S16 = State(16, "NioServerSocketChannel",
                    "Step 3: Configure the ServerBootstrap to use NioServerSocketChannel for handling incoming TCP connections and set up the pipeline with appropriate handlers for request processing.")
        S17 = State(17, "bind",
                    "Step 4: Bind the server to a specific host and port using ServerBootstrap.bind(), allowing it to listen for and accept incoming client connections.")
        S18 = State(18, "closeFuture()|shutdownGracefully()",
                    "Step 5: Keep the server running by synchronizing on closeFuture(), and call shutdownGracefully() on EventLoopGroup during shutdown to release all associated resources.")

        # Define state transitions
        S14.AddNext(S15)
        S15.AddNext(S16)
        S16.AddNext(S17)
        S17.AddNext(S18)

        # Add states to the classifier
        Class.AddState(S14)
        self.IRIClfList.append(Class)

        # FSM 6: Java Netty UDP Client-side or Server-side
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Java Netty UDP Client or Server")
        S19 = State(19,
                    "import io.netty.bootstrap.Bootstrap|import io.netty.channel.*|import io.netty.channel.nio.NioEventLoopGroup|import io.netty.channel.socket.nio.NioDatagramChannel",
                    "Step 1: Import Netty libraries required for UDP communication, including Bootstrap for client/server setup, NioEventLoopGroup for managing event-driven I/O, Channel for UDP data handling, and NioDatagramChannel for non-blocking datagram transport.")
        S20 = State(20, "NioEventLoopGroup|new Bootstrap()",
                    "Step 2: Create a NioEventLoopGroup to handle I/O operations asynchronously and initialize a Bootstrap instance to configure the Netty UDP client or server.")
        S21 = State(21, "NioDatagramChannel",
                    "Step 3: Configure the Bootstrap with NioDatagramChannel for UDP transport, apply necessary channel options such as SO_BROADCAST, and initialize a ChannelPipeline with relevant handlers like SimpleChannelInboundHandler.")
        S22 = State(22, "bind",
                    "Step 4: Bind the DatagramChannel to a local port, enabling the UDP socket to send and receive datagrams from remote hosts.")
        S23 = State(23, "closeFuture()|shutdownGracefully",
                    "Step 5: Monitor closeFuture() to detect when the channel is closed, then release resources gracefully using shutdownGracefully() to prevent memory leaks.")

        # Define state transitions
        S19.AddNext(S20)
        S20.AddNext(S21)
        S21.AddNext(S22)
        S22.AddNext(S23)

        # Add states to the classifier
        Class.AddState(S19)
        self.IRIClfList.append(Class)

        # FSM 7: Recognizing the TCP Client-side based on Java.nio
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "TCP Client-side based on java.nio")
        S24 = State(24, "import java.nio.*|import java.nio.channels.*|import java.net.*",
                    "Step 1: Import necessary NIO classes, including networking classes")
        S25 = State(25, "SocketChannel.open|configureBlocking(false)|Selector.open()|register",
                    "Step 2: Initialize SocketChannel, set non-blocking mode, open Selector, and register the channel")
        S26 = State(26, "connect", "Step 3: Establish a connection to the server using SocketChannel")
        S27 = State(27,
                    "capacity|clear|put|flip|write|read|compact|order|getInt|putInt|getFloat|putFloat|duplicate|slice|asReadOnlyBuffer|position|limit|mark|reset",
                    "Step 4: Perform buffer operations such as writing, reading, flipping, compacting, and managing memory")
        S28 = State(28, "close()", "Step 5: Close the SocketChannel and release resources")
        # Define state transitions
        S24.AddNext(S25)
        S25.AddNext(S26)
        S26.AddNext(S27)
        S27.AddNext(S28)

        # Add the state machine to the classifier
        Class.AddState(S24)
        self.IRIClfList.append(Class)

        # FSM 8: Recognizing the TCP Server-side based on Java.nio
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "TCP Server-side based on java.nio")
        S29 = State(29, "import java.nio.*|import java.nio.channels.*",
                    "Step 1: Import necessary NIO classes, including channels and buffers for server-side operations")
        S30 = State(30,
                    "ServerSocketChannel.open|configureBlocking(false)|serverSocketChannel.socket()|bind|Selector.open()",
                    "Step 2: Create a ServerSocketChannel, configure it as non-blocking, bind to a port, and initialize a Selector for handling multiple connections")
        S31 = State(31, "accept", "Step 3: Accept client connections from the ServerSocketChannel")
        S32 = State(32,
                    "capacity|clear|put|flip|write|read|compact|order|getInt|putInt|getFloat|putFloat|duplicate|slice|asReadOnlyBuffer|position|limit|mark|reset",
                    "Step 4: Use ByteBuffer to perform data operations such as writing, reading, flipping, compacting, and managing memory")
        S33 = State(33, "close()", "Step 5: Close the ServerSocketChannel and release all associated resources")
        # Define state transitions
        S29.AddNext(S30)
        S30.AddNext(S31)
        S31.AddNext(S32)
        S32.AddNext(S33)
        # Add the state machine to the classifier
        Class.AddState(S29)
        self.IRIClfList.append(Class)

        # FSM 9: Recognizing the UDP Client-side based on Java.nio
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "UDP sender based on java.nio")

        S34 = State(34, "import java.nio.*|import java.nio.channels.*",
                    "Step 1: Import necessary Java NIO classes for non-blocking UDP communication, including DatagramChannel and ByteBuffer.")
        S35 = State(35, "DatagramChannel.open|configureBlocking(false)",
                    "Step 2: Open a DatagramChannel for UDP communication, configure it as non-blocking to allow asynchronous operations.")
        S36 = State(36, "send",
                    "Step 3: Create a ByteBuffer to store the outgoing message, set the target address using InetSocketAddress, and use send() to transmit the data.")
        S37 = State(37, "clear|close()",
                    "Step 4: Clear the ByteBuffer to prepare for new data and close the DatagramChannel to release resources.")

        S34.AddNext(S35)
        S35.AddNext(S36)
        S36.AddNext(S37)

        Class.AddState(S34)
        self.IRIClfList.append(Class)

        # FSM 10: Recognizing FileChannel usage in Java.nio
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "FileChannel usage in java.nio")
        S38 = State(38, "import java.nio.*|import java.nio.channels.*|import java.nio.file.*",
                    "Step 1: Import necessary Java NIO classes, including FileChannel and Buffer classes such as ByteBuffer and MappedByteBuffer")
        S39 = State(39, "FileChannel.open|StandardOpenOption",
                    "Step 2: Open a FileChannel using FileChannel.open() with appropriate StandardOpenOption flags like READ, WRITE, APPEND, etc., for file operations")
        S40 = State(40, "read|write|position|truncate|size|force|map|transferTo|transferFrom",
                    "Step 3: Perform file operations such as reading and writing to a file, modifying position, truncating file, transferring data, and mapping files into memory")
        S41 = State(41,
                    "clear()|flip()|put()|get()|compact()|duplicate()|slice()|asReadOnlyBuffer()|mark()|reset()|order()|force()|isDirect()|allocateDirect()",
                    "Step 4: Perform various operations on ByteBuffer, DirectByteBuffer, and MappedByteBuffer. This includes clearing, flipping, putting, getting, and other memory management tasks. For MappedByteBuffer, force writes changes to disk.")
        S42 = State(42, "close",
                    "Step 5: Close the FileChannel to release system resources and finalize the file operations")
        # Define state transitions
        S38.AddNext(S39)
        S39.AddNext(S40)
        S40.AddNext(S41)
        S41.AddNext(S42)
        # Add the state machine to the classifier
        Class.AddState(S38)
        self.IRIClfList.append(Class)

        # FSM 11: Recognizing the TCP Client based on Apache MINA
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "TCP Client based on Apache MINA in java")
        S43 = State(43,
                    "import org.apache.mina.core.session.IoSession|import org.apache.mina.filter.codec.*|import org.apache.mina.transport.socket.nio.NioSocketConnector|import org.apache.mina.core.service",
                    "Step 1: Import necessary Apache MINA classes, including IoSession, NioSocketConnector, and various filters for the connection.")
        S44 = State(44, "new NioSocketConnector()",
                    "Step 2: Create a NioSocketConnector, which is responsible for managing the client-side connection to the server.")
        S45 = State(45,
                    "setHandler|IoHandler|IoHandlerAdapter|getFilterChain()|LoggingFilter|SSLFilter|ProtocolCodecFilter|CompressionFilter|BlackListFilter|WhiteListFilter|ExecutorFilter|TrafficShapingFilter",
                    "Step 4: Set the IoHandler for handling events such as read, write, and exception processing for the session.")
        S46 = State(46, "connect|getSession()|awaitUninterruptibly",
                    "Step 5: Initiate the connection to the server, obtain the session and wait for the connection to be established.")
        S47 = State(47, "write|getServiceAddress|send|flush|isConnected|setAttribute|setIdleTime",
                    "Step 6: Perform various operations on the session such as writing data, sending messages, checking connection status, and setting attributes and idle time.")
        S48 = State(48, "dispose|getCloseFuture|awaitUninterruptibly",
                    "Step 7: Dispose of the connection, wait for it to close, and release resources associated with the session.")
        S43.AddNext(S44)
        S44.AddNext(S45)
        S45.AddNext(S46)
        S46.AddNext(S47)
        S47.AddNext(S48)
        Class.AddState(S43)
        self.IRIClfList.append(Class)

        # FSM 12: Recognizing the TCP Server based on Apache MINA
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "TCP Server based on Apache MINA in java")
        S49 = State(49,
                    "import org.apache.mina.core.session.IoSession|import org.apache.mina.filter.codec.*|import org.apache.mina.transport.socket.nio.NioSocketAcceptor|import org.apache.mina.core.service",
                    "Step 1: Import necessary Apache MINA classes")
        S50 = State(50, "new NioSocketAcceptor()", "Step 2: Create a NioSocketAcceptor")
        S51 = State(51,
                    "getFilterChain()|LoggingFilter|SSLFilter|ProtocolCodecFilter|CompressionFilter|BlackListFilter|WhiteListFilter|ExecutorFilter|TrafficShapingFilter",
                    "Step 3: Configure filter chain")
        S52 = State(52, "setHandler|IoHandler|IoHandlerAdapter", "Step 4: Set the handler")
        S53 = State(53, "bind", "Step 5: Bind to a port and start the server")

        S49.AddNext(S50)
        S50.AddNext(S51)
        S51.AddNext(S52)
        S52.AddNext(S53)
        Class.AddState(S49)
        self.IRIClfList.append(Class)

        # FSM 13: Recognizing Vert.x TCP Client
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Vert.x TCP Client in Java")
        S54 = State(54,
                    "import io.vertx.core.AbstractVerticle|import io.vertx.core.Vertx|import io.vertx.core.buffer.Buffer|import io.vertx.core.net.NetClient|import io.vertx.core.net.NetClientOptions|import io.vertx.core.net.NetSocket",
                    "Step 1: Import necessary Vert.x classes for TCP client, including NetClient for handling connections and NetClientOptions for configuration.")
        S55 = State(55, "new NetClientOptions()",
                    "Step 2: Initialize NetClientOptions to configure TCP client settings, such as reconnect attempts, SSL, and timeouts.")
        S56 = State(56, "vertx.createNetClient()",
                    "Step 3: Create a NetClient instance, which will be used to establish a TCP connection with the server.")
        S57 = State(57, "connect",
                    "Step 4: Connect to the server by specifying the target host and port, and obtain a NetSocket instance upon a successful connection.")
        S58 = State(58, "write|sendFile",
                    "Step 5: Use NetSocket to write data to the server or send files over the TCP connection.")
        S54.AddNext(S55)
        S55.AddNext(S56)
        S56.AddNext(S57)
        S57.AddNext(S58)
        Class.AddState(S54)
        self.IRIClfList.append(Class)

        # FSM 14: Recognizing Vert.x TCP Server
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Vert.x TCP Server in Java")
        S59 = State(59,
                    "import io.vertx.core.AbstractVerticle|import io.vertx.core.Vertx|import io.vertx.core.buffer.Buffer|import io.vertx.core.net.NetServer|import io.vertx.core.net.NetServerOptions",
                    "Step 1: Import necessary Vert.x classes for TCP server, including NetServer for handling incoming connections and NetServerOptions for configuration.")
        S60 = State(60, "new NetServerOptions()",
                    "Step 2: Initialize NetServerOptions to configure server settings such as port, host, SSL, and connection timeout.")
        S61 = State(61, "createNetServer()",
                    "Step 3: Create a NetServer instance using Vert.x, allowing it to accept and manage multiple TCP client connections.")
        S62 = State(62, "connectHandler",
                    "Step 4: Define a connection handler function that will be triggered when a new client connects to the server, providing a NetSocket instance to manage communication.")
        S63 = State(63, "write|sendFile",
                    "Step 5: Use the NetSocket instance to process incoming data from clients, send responses, or transfer files over the TCP connection.")
        S59.AddNext(S60)
        S60.AddNext(S61)
        S61.AddNext(S62)
        S62.AddNext(S63)
        Class.AddState(S59)
        self.IRIClfList.append(Class)

        # FSM 15: Recognizing Vert.x UDP sender
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Vert.x UDP sender in Java")
        S64 = State(64,
                    "import io.vertx.core.AbstractVerticle|import io.vertx.core.Vertx|import io.vertx.core.buffer.Buffer|import io.vertx.core.net.DatagramSocket|import io.vertx.core.net.DatagramSocketOptions",
                    "Step 1: Import necessary Vert.x classes for UDP communication, including DatagramSocket for sending and receiving packets and DatagramSocketOptions for socket configuration.")
        S65 = State(65, "vertx.createDatagramSocket()",
                    "Step 2: Create a DatagramSocket instance using Vert.x, enabling UDP communication with optional configuration via DatagramSocketOptions.")
        S66 = State(66, "send",
                    "Step 3: Send a UDP packet using send(), specifying the target address, port, and data buffer. Optionally, define handlers to track send success or failure.")
        S64.AddNext(S65)
        S65.AddNext(S66)
        Class.AddState(S64)
        self.IRIClfList.append(Class)

        # FSM 16: Recognizing TCP Client-side based on Java.io
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "TCP Client-side Java.io")
        S67 = State(67, "import java.io.*|import java.net.*",
                    "Step 1: Import necessary Java IO and networking classes")
        S68 = State(68, "new Socket()", "Step 2: Create a new Socket to connect to the server")
        S69 = State(69, "getOutputStream()|getInputStream()|BufferedReader|BufferedWriter",
                    "Step 3: Create writers and readers for data exchange, get input and output streams")
        S70 = State(70, "read|readLine|write|flush|nextLine|next", "Step 5: Read data or send data to the server")
        S71 = State(71, "close()", "Step 7: Close the connection")

        S67.AddNext(S68)
        S68.AddNext(S69)
        S69.AddNext(S70)
        S70.AddNext(S71)
        Class.AddState(S67)
        self.IRIClfList.append(Class)
        #
        # FSM 17: Recognizing Http client based on Java.io & HttpURLConnection
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Http client-side based on Java.io & HttpURLConnection")
        S72 = State(72, "import java.io.*|import java.net.URL|import java.net.HttpURLConnection",
                    "Step 1: Import necessary Java IO and networking classes")
        S73 = State(73, "new URL", "Step 2: Get the access URL")
        S74 = State(74, "openConnection", "Step 3: Create an HttpURLConnection object")
        S75 = State(75,
                    "setRequestMethod|setConnectTimeout|setDoOutput|setDoInput|setUseCaches|setInstanceFollowRedirects|setRequestProperty",
                    "Step 4: Set request parameters")
        S76 = State(76, "write|flush|getResponseCode|getInputStream|getOutputStream|readLine|read",
                    "Step 5: Processing Input and Output")
        S77 = State(77, "disconnect", "Step 6: Disconnect")

        S72.AddNext(S73)
        S73.AddNext(S74)
        S74.AddNext(S75)
        S75.AddNext(S76)
        S76.AddNext(S77)
        Class.AddState(S72)
        self.IRIClfList.append(Class)

        # FSM 18: Recognizing Http client based on Java.io & HttpURLConnection
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Http client-side based on HttpClient in java")
        S78 = State(78, "import java.net.http.*|import java.net.URI",
                    "Step 1: Import necessary Java networking classes")
        S79 = State(79, "HttpClient.newBuilder()", "Step 2: Create an HttpClient instance")
        S80 = State(80, "GET|POST|PUT|DELETE", "Step 3: Construct an HTTP request")
        S81 = State(81, "send|sendAsync",
                    "Step 4: Send the request (synchronously or asynchronously) and handle the response")

        S78.AddNext(S79)
        S79.AddNext(S80)
        S80.AddNext(S81)

        Class.AddState(S78)
        self.IRIClfList.append(Class)

        # FSM 19: Netty HTTP Client
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Netty HTTP Client in java")
        S82 = State(82,
                    "import io.netty.bootstrap.Bootstrap|import io.netty.channel.*| import io.netty.handler.codec.http.*",
                    "Step 1: Import required Netty classes")
        S83 = State(83, "new NioEventLoopGroup()", "Step 2: Create EventLoopGroup")
        S84 = State(84, "new Bootstrap()", "Step 3: Create and configure Bootstrap")
        S85 = State(85,
                    "pipeline().addLast|HttpClientCodec|HttpContentDecompressor|HttpObjectAggregator|NettyHttpClientHandler",
                    "Step 4: Set up HTTP pipeline")
        S86 = State(86, "connect", "Step 5: Connect to HTTP server")
        S87 = State(87, "new URI|DefaultFullHttpRequest",
                    "Step 5: Construct HTTP request,use DefaultFullHttpRequest, set GET/POST method, URI, Headers")
        S88 = State(88, "write|flush|writeAndFlush", "Step 6: Sending Requests & Handling Responses")
        S89 = State(89, "close|shutdownGracefully", "Step 7: Close the connection to release resources")

        S82.AddNext(S83)
        S83.AddNext(S84)
        S84.AddNext(S85)
        S85.AddNext(S86)
        S86.AddNext(S87)
        S87.AddNext(S88)
        S88.AddNext(S89)
        Class.AddState(S82)
        self.IRIClfList.append(Class)

        # FSM 20: Netty HTTP Server
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Netty HTTP Server in Java")
        S90 = State(90,
                    "import io.netty.bootstrap.ServerBootstrap|import io.netty.channel.*|import io.netty.handler.codec.http.*",
                    "Step 1: Import required Netty classes, including ServerBootstrap for server setup, Channel for network communication, and HTTP handlers for processing HTTP requests and responses.")
        S91 = State(91, "new NioEventLoopGroup()|new ServerBootstrap()",
                    "Step 2: Create bossGroup to accept incoming connections and workerGroup to handle traffic and process events.")
        S92 = State(92, "NioServerSocketChannel|InetSocketAddress|ChannelInitializer",
                    "Step 3: Configure the server channel using NioServerSocketChannel for non-blocking I/O, set InetSocketAddress for binding, and use ChannelInitializer to define the channel pipeline.")
        S93 = State(93,
                    "HttpRequestDecoder|HttpObjectAggregator|HttpResponseEncoder|HttpContentCompressor|HttpServerCodec|HttpServerExpectContinueHandler|ChunkedWriteHandler|CorsHandler|IdleStateHandler|SslHandler",
                    "Step 4: Set up the HTTP pipeline with HttpRequestDecoder for decoding requests, HttpObjectAggregator for handling full HTTP messages, HttpResponseEncoder for encoding responses, HttpContentCompressor for compression, HttpServerCodec as a combined codec, HttpServerExpectContinueHandler for handling 100 - Continue requests, ChunkedWriteHandler for large data transmission, CorsHandler for cross - origin requests, IdleStateHandler for connection timeout management, and SslHandler for HTTPS support if needed.")
        S94 = State(94, "bind",
                    "Step 5: Bind the server to a specific port and start listening for incoming HTTP connections.")
        S90.AddNext(S91)
        S91.AddNext(S92)
        S92.AddNext(S93)
        S93.AddNext(S94)
        Class.AddState(S90)
        self.IRIClfList.append(Class)

        # FSM 21: Recognizing Http client based on Java.nio
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "NIO HTTP Client in Java")
        S95 = State(95, "import java.nio.*|import java.nio.channels.*|import java.net.*",
                    "Step 1: Import necessary Java NIO and networking classes, including java.nio for buffer operations, java.nio.channels for non-blocking I/O, and java.net for handling network communication.")
        S96 = State(96, "SocketChannel.open()|configureBlocking(false)|Selector.open()",
                    "Step 2: Open a non-blocking SocketChannel and configure it to operate asynchronously. Create a Selector to handle multiple non-blocking connections.")
        S97 = State(97, "selectedKeys()",
                    "Step 3: Register the SocketChannel with the Selector and initiate a connection to the HTTP server. The Selector will monitor connection readiness events.")
        S98 = State(98, "isConnectable()",
                    "Step 4: Once the connection is established, check if the channel is in a connectable state using isConnectable(). Complete the connection if necessary.")
        S95.AddNext(S96)
        S96.AddNext(S97)
        S97.AddNext(S98)
        Class.AddState(S95)
        self.IRIClfList.append(Class)

        # FSM 22: Recognizing Http Server based on Java.nio
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "NIO HTTP Server in Java")
        S99 = State(99, "import java.nio.*|import java.nio.channels.*|import java.net.*",
                    "Step 1: Import necessary Java NIO and networking classes, including java.nio for buffer handling, java.nio.channels for non-blocking IO operations, and java.net for network communication.")
        S100 = State(100, "ServerSocketChannel.open()|bind|configureBlocking(false)|Selector.open()",
                     "Step 2: Open a ServerSocketChannel, bind it to a specific port, and set it to non-blocking mode using configureBlocking(false) to handle connections asynchronously, and Create a Selector instance, which will manage multiple non-blocking channels and handle events efficiently.")
        S101 = State(101, "register",
                     "Step 4: Register the ServerSocketChannel with the Selector, specifying interest in accepting new client connections.")
        S102 = State(102, "selectedKeys()",
                     "Step 5: Retrieve the set of selected keys from the Selector, which indicate channels that are ready for I/O operations such as accepting connections or reading data.")
        S103 = State(103, "isAcceptable()|isReadable()|isWritable()",
                     "Step 6: Handle incoming connections and data processing based on the SelectionKey state. Use isAcceptable() to accept new client connections, isReadable() to read incoming requests, and isWritable() to send responses.")
        S99.AddNext(S100)
        S100.AddNext(S101)
        S101.AddNext(S102)
        S102.AddNext(S103)
        Class.AddState(S99)
        self.IRIClfList.append(Class)

        # FSM 23：Java RESTful API HTTP Client
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Java RESTful API HTTP Client")
        S104 = State(104, "import java.net.http.*|import org.springframework.web.client.RestTemplate|import okhttp3.*",
                     "Step 1: Import required libraries")
        S105 = State(105, "HttpClient.newHttpClient()|new RestTemplate()|new OkHttpClient()",
                     "Step 2: Create HTTP client instance")
        S106 = State(106, "HttpRequest.newBuilder()|new Request.Builder()", "Step 3: Construct HTTP request (GET/POST)")
        S107 = State(107, "setHeader|header()", "Step 4: Set request headers")
        S108 = State(108, "send|sendAsync|execute|exchange", "Step 5: Send HTTP request")
        S109 = State(109, "getBody|body|parse response", "Step 6: Handle response")

        S104.AddNext(S105)
        S105.AddNext(S106)
        S106.AddNext(S107)
        S107.AddNext(S108)
        S108.AddNext(S109)

        Class.AddState(S104)
        self.IRIClfList.append(Class)

        # FSM 24: Recognizing Java GRPC client-side
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "gRPC Client in java")
        S110 = State(110,
                     "import io.grpc.ManagedChannel|import io.grpc.ManagedChannelBuilder|import io.grpc.stub.AbstractStub|import io.grpc.StatusRuntimeException",
                     "Step 1: Import ManagedChannel, ManagedChannelBuilder, AbstractStub for GRPC client, and StatusRuntimeException for error handling")
        S111 = State(111, "ManagedChannelBuilder.forAddress|ManagedChannelBuilder.forTarget",
                     "Step 2: Create ManagedChannel for client and establish connection to the GRPC server")
        S112 = State(112, "newBlockingStub|newStub|asyncStub|StreamObserver",
                     "Step 3: Create a GRPC stub (blocking or async) and invoke remote method via stub")
        S113 = State(113, "shutdown|awaitTermination",
                     "Step 4: Shutdown the ManagedChannel or await termination of GRPC client connection")
        # State transitions for the FSM
        S110.AddNext(S111)
        S111.AddNext(S112)
        S112.AddNext(S113)
        # Add states to the client classifier
        Class.AddState(S110)
        self.IRIClfList.append(Class)

        # FSM 25: Recognizing Java gRPC server-side
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "gRPC Server in java")
        S114 = State(114,
                     "import io.grpc.Server|import io.grpc.ServerBuilder|import io.grpc.BindableService|import io.grpc.stub.StreamObserver|import io.grpc.ServerServiceDefinition",
                     "Step 1: Import Server, ServerBuilder for server creation, BindableService for service binding, StreamObserver for handling responses")
        S115 = State(115, "ServerBuilder.forPort",
                     "Step 2:Create server using ServerBuilder and specify port")
        S116 = State(116, "addService|addMethodHandler|serviceConfiguration",
                     "Add service or method handler to GRPC server, configure service options or middleware")
        S117 = State(117, "start",
                     "Step 4: Start the server")
        S118 = State(118, "shutdown|awaitTermination|gracefulShutdown",
                     "Step 5: Shutdown GRPC server gracefully, or await termination to wait for all ongoing calls to complete.")
        # State transitions for the FSM
        S114.AddNext(S115)
        S115.AddNext(S116)
        S116.AddNext(S117)
        S117.AddNext(S118)
        # Add states to the server classifier
        Class.AddState(S114)
        self.IRIClfList.append(Class)

        # FSM 26: Recognizing Java EE WebSocket Client
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "WebSocket Client based on Java EE")
        S119 = State(119,
                     "import javax.websocket.ContainerProvider|import javax.websocket.WebSocketContainer|import javax.websocket.Session|import javax.websocket.MessageHandler",
                     "Step 1: Import necessary WebSocket client classes")
        S120 = State(120, "Session", "Step 2: Create a session for the WebSocket connection")
        S121 = State(121, "onOpen|onMessage|onClose|onError|sendText|sendBinary|sendObject",
                     "Step 3: Override OnOpen, OnMessage, OnClose, OnError methods, and optionally handle received messages and send messages within these methods")
        S122 = State(122, "getWebSocketContainer", "Step 4: Create a WebSocket container instance in the main function")
        S123 = State(123, "connectToServer|sendText|sendBinary|sendObject",
                     "Step 5: Connect to the WebSocket server in the main function, provide the endpoint, and optionally send messages after the connection is established if needed")
        S119.AddNext(S120)
        S120.AddNext(S121)
        S121.AddNext(S122)
        S122.AddNext(S123)
        Class.AddState(S119)
        self.IRIClfList.append(Class)

        # FSM 27: Recognizing Java EE WebSocket Server
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "WebSocket Server based on Java EE")
        S124 = State(124,
                     "import javax.websocket.server.ServerEndpoint|import javax.websocket.Session|import javax.websocket.OnMessage|import javax.websocket.OnOpen|import javax.websocket.OnClose",
                     "Step 1: Import the necessary WebSocket server classes")
        S125 = State(125, "@ServerEndpoint",
                     "Step 2: Define a WebSocket server endpoint using the @ServerEndpoint annotation")
        S126 = State(126, "Session",
                     "Step 3: Define the WebSocket server endpoint and manage client connections using the Session object")
        S127 = State(127, "onOpen|onMessage|onClose|sendText|sendBinary|sendObject",
                     "Step 4: Implement the methods like onOpen, onMessage, onClose to handle client communication and data exchange")

        S124.AddNext(S125)
        S125.AddNext(S126)
        S126.AddNext(S127)
        Class.AddState(S124)
        self.IRIClfList.append(Class)

        # FSM 28：WebSocket Client Implementation using org.java_websocket
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java",
                              "WebSocket Client Implementation using org.java_websocket")
        S128 = State(128,
                     "import java.net.URI|import org.java_websocket.client.WebSocketClient|import org.java_websocket.handshake.ServerHandshake",
                     "Step 1: Import necessary WebSocket client classes")
        S129 = State(129, "extends WebSocketClient", "Step 2: Define MyWebSocketClient class extending WebSocketClient")
        S130 = State(130, "onOpen|onMessage|onClose|onError", "Step 3: Override WebSocket event - handling methods")
        S128.AddNext(S129)
        S129.AddNext(S130)
        Class.AddState(S128)
        self.IRIClfList.append(Class)

        # FSM 29: WebSocket Server Handler using org.java_websocket
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "WebSocket Server Handler using org.java_websocket")
        S131 = State(131,
                     "import org.java_websocket.server.WebSocketServer|import org.java_websocket.WebSocket|import org.java_websocket.handshake.ClientHandshake",
                     "Step 1: Import necessary classes from org.java_websocket, including WebSocketServer, WebSocket, and ClientHandshake for server implementation.")
        S132 = State(132, "extends WebSocketServer",
                     "Step 2: Extend WebSocketServer class to create a custom WebSocket server, overriding lifecycle methods for handling connections, messages, and disconnections.")
        S133 = State(133, "onOpen|onMessage|onClose|onError",
                     "Step 3: Implement WebSocket lifecycle methods: onOpen for new client connections, onMessage for processing received messages, onClose for handling disconnections, and onError for error handling.")
        # State transitions for the FSM
        S131.AddNext(S132)
        S132.AddNext(S133)
        Class.AddState(S131)
        self.IRIClfList.append(Class)

        # FSM 30：WebSocket Server Initialization using org.java_websocket
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java",
                              "WebSocket Server Initialization using org.java_websocket")
        S134 = State(134, "import org.java_websocket.server.WebSocketServer|import org.java_websocket.Server",
                     "Step 1: Import necessary WebSocketServer and Server classes")
        S135 = State(135, "start()", "Step 3: Start the WebSocket server")
        S136 = State(136, "run()",
                     "Step 4: Run the WebSocket server, it listens for connections and handles incoming requests")
        S137 = State(137, "stop()", "Step 5: Stop the WebSocket server after the work is done")
        # State transitions for the FSM
        S134.AddNext(S135)
        S135.AddNext(S136)
        S136.AddNext(S137)
        Class.AddState(S134)
        self.IRIClfList.append(Class)

        # FSM 31: WebSocket Client using Netty
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "WebSocket Client using Netty in Java")
        S138 = State(138,
                     "import io.netty.bootstrap.Bootstrap|import io.netty.channel.*|import io.netty.handler.codec.http.*|import io.netty.handler.codec.http.websocketx.*",
                     "Step 1: Import necessary classes, including Bootstrap for client setup, Channel for network communication, HTTP handlers for WebSocket upgrade, and WebSocket handlers for processing frames.")
        S139 = State(139, "new NioEventLoopGroup()|new Bootstrap()",
                     "Step 2: Create EventLoopGroup for managing I/O operations asynchronously and initialize a Bootstrap instance to configure the WebSocket client.")
        S140 = State(140, "NioSocketChannel|LoggingHandler|ChannelInitializer",
                     "Step 3: Set up the Netty client pipeline using NioSocketChannel for non-blocking I/O, LoggingHandler for debugging, and ChannelInitializer for configuring the channel handlers.")
        S141 = State(141, "HttpClientCodec|WebSocketClientProtocolHandler|WebSocketFrameDecoder|WebSocketFrameEncoder",
                     "Step 4: Configure the WebSocket client pipeline by adding HttpClientCodec to handle HTTP requests, WebSocketClientProtocolHandler for managing the WebSocket handshake and frame processing, WebSocketFrameDecoder/WebSocketFrameEncoder for decoding and encoding WebSocket frames.")
        S142 = State(142, "connect", "Step 5: Establish connection to the WebSocket server.")
        S143 = State(143, "sync|addListener|syncUninterruptibly|await",
                     "Step 6: Handshake with the WebSocket server and wait for the connection to complete, using sync and addListener methods to monitor connection status.")
        S144 = State(144, "writeAndFlush|write|flush|ChannelFuture|ChannelHandlerContext",
                     "Step 7: Send WebSocket messages using writeAndFlush method or equivalent, sending WebSocket frames to the server.")
        S145 = State(145, "closeFuture().sync|closeFuture().addListener|close|shutdownGracefully|fireChannelInactive",
                     "Step 8: Close the connection, release resources, and handle shutdown gracefully by monitoring closeFuture() and calling shutdownGracefully() on the EventLoopGroup.")
        # Define state transitions
        S138.AddNext(S139)
        S139.AddNext(S140)
        S140.AddNext(S141)
        S141.AddNext(S142)
        S142.AddNext(S143)
        S143.AddNext(S144)
        S144.AddNext(S145)
        # Add states to the classifier
        Class.AddState(S138)
        self.IRIClfList.append(Class)

        # FSM 32：Kafka client Producer
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Kafka client Producer in java")
        S146 = State(146,
                     "import org.apache.kafka.clients.producer.KafkaProducer|import org.apache.kafka.clients.producer.ProducerConfig|import org.apache.kafka.clients.producer.ProducerRecord|import org.apache.kafka.common.serialization.StringSerializer|import java.util.Properties",
                     "Step 1: Import Kafka dependencies and related classes for configuring and creating a Kafka Producer")
        S147 = State(147, "ProducerConfig", "Step 2: Configure Kafka Producer properties")
        S148 = State(148, "new KafkaProducer", "Step 3: Create a Kafka Producer instance using the configuration")
        S149 = State(149, "send|ProducerRecord|flush", "Step 4: Send messages to Kafka")
        S150 = State(150, "close", "Step 5: Close the Kafka Producer")
        # State transitions
        S146.AddNext(S147)
        S147.AddNext(S148)
        S148.AddNext(S149)
        S149.AddNext(S150)
        # Add states to the classifier
        Class.AddState(S146)
        self.IRIClfList.append(Class)

        # FSM 33：Kafka client Consumer
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Kafka client Consumer in java")
        S151 = State(151,
                     "import org.apache.kafka.clients.consumer.ConsumerConfig|import org.apache.kafka.clients.consumer.KafkaConsumer|import org.apache.kafka.common.serialization.StringDeserializer|import java.util.Collections|import java.util.Properties;",
                     "Step 1: Import Kafka dependencies and related classes for configuring and creating a Kafka Consumer")
        S152 = State(152, "ConsumerConfig", "Step 2: Configure Kafka Consumer properties")
        S153 = State(153, "new KafkaConsumer", "Step 3: Create a Kafka Consumer instance using the configuration")
        S154 = State(154, "subscribe|assign|ConsumerRecords|unsubscribe", "Step 4: Subscribe to a Kafka topic")
        S155 = State(155, "poll|commitSync|commitAsync|seek|pause|resume", "Step 5: Consume messages from Kafka")
        S156 = State(156, "close", "Step 6: Close the Kafka Consumer")
        # State transitions
        S151.AddNext(S152)
        S152.AddNext(S153)
        S153.AddNext(S154)
        S154.AddNext(S155)
        S155.AddNext(S156)
        # Add states to the classifier
        Class.AddState(S151)
        self.IRIClfList.append(Class)

        # FSM 34: Create Kafka AdminClient in Java
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Create and Configure Kafka AdminClient in java")
        S157 = State(157, "import org.apache.kafka.clients.admin.*",
                     "Step 1: Import necessary Kafka AdminClient classes for managing Kafka topics and configurations.")
        S158 = State(158, "new Properties|newHashMap",
                     "Step 2: Create a Properties object to store Kafka AdminClient configuration settings.")
        S159 = State(159, "setProperty|put|AdminClientConfig",
                     "Step 3: Set Kafka AdminClient properties such as bootstrap servers and security settings.")
        S160 = State(160, "AdminClient.create",
                     "Step 4: Instantiate Kafka AdminClient using the configured properties.")
        # Define state transitions for Kafka AdminClient FSM
        S157.AddNext(S158)
        S158.AddNext(S159)
        S159.AddNext(S160)
        Class.AddState(S157)
        self.IRIClfList.append(Class)

        # FSM 35: Create Kafka Topic Instance
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Create Kafka topic instance in AdminClient in java")
        S161 = State(161, "import org.apache.kafka.clients.admin.*",
                     "Step 1: Import Kafka AdminClient classes to work with Kafka topics")
        S162 = State(162, "adminClient()", "Step 2: Create an AdminClient instance to interact with Kafka broker")
        S163 = State(163, "new NewTopic",
                     "Step 3: Create a NewTopic object which defines the topic's configuration like name, partitions, and replication factor")
        S164 = State(164, "createTopics",
                     "Step 4: Use AdminClient to create the topic in Kafka using the NewTopic object")
        # Define state transitions
        S161.AddNext(S162)
        S162.AddNext(S163)
        S163.AddNext(S164)
        # Add states to the classifier
        Class.AddState(S161)
        self.IRIClfList.append(Class)

        # FSM 36: View/Delete/Describe Topic in Kafka using AdminClient
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "View/Delete/Describe topic in AdminClient in java")
        S165 = State(165, "import org.apache.kafka.clients.admin.*",
                     "Step 1: Import Kafka AdminClient classes for performing administrative operations on Kafka topics.")
        S166 = State(166, "listTopics|deleteTopics|describeTopics|describeCluster|listConsumerGroups|listOffsets",
                     "Step 3: Use AdminClient methods to perform actions such as listing topics, deleting topics, or describing topics and clusters.")
        S167 = State(167, "get",
                     "Step 4: Retrieve the results of the operation (e.g., list topics, delete topics, or describe topics) using the `get()` method to fetch the response.")
        # Define state transitions
        S165.AddNext(S166)
        S166.AddNext(S167)
        # Add states to the classifier
        Class.AddState(S165)
        self.IRIClfList.append(Class)

        # FSM 37: View Kafka AdminClient Configuration in Java
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "View Kafka AdminClient  Config in java")
        S168 = State(168,
                     "import org.apache.kafka.clients.admin.*|import org.apache.kafka.common.config.ConfigResource",
                     "Step 1: Import required Kafka AdminClient and ConfigResource classes for viewing topic or broker configurations.")
        S169 = State(169, "ConfigResource",
                     "Step 2: Define a ConfigResource for the topic or broker whose configuration needs to be described. This specifies the resource (e.g., topic) whose configuration will be fetched.")
        S170 = State(170, "describeConfigs",
                     "Step 3: Call `describeConfigs` method on AdminClient to retrieve the configuration of the specified topic or broker.")
        S171 = State(171, "get",
                     "Step 4: Use the `get()` method to fetch the configuration details retrieved by `describeConfigs`.")
        # Define state transitions
        S168.AddNext(S169)
        S169.AddNext(S170)
        S170.AddNext(S171)
        # Add states to the classifier
        Class.AddState(S168)
        self.IRIClfList.append(Class)

        # FSM 38: Redis in Java
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "Redis in Java")
        S172 = State(172,
                     "import redis.clients.jedis.*|import io.lettuce.core.*|import org.springframework.data.redis.core.*",
                     "Step 1: Import necessary Redis client libraries (Jedis, Lettuce, Spring Data Redis)")
        S173 = State(173, "new Jedis|new JedisPool|new JedisCluster|RedisClient.create|new RedisTemplate",
                     "Step 2: Create a Redis connection instance")
        S174 = State(174, "auth|getResource|connect|setConnectionFactory",
                     "Step 3: Authenticate (if required) and establish the connection")
        S175 = State(175,
                     "set|get|del|exists|expire|ttl|ftCreate|ftSearch|getDocuments|hset|hget|hmget|hmset|hdel|hlen|hkeys|hvals|lpush|rpush|lpop|rpop|lrange|sadd|srem|smembers|scard|zadd|zrem|zincrby|zscore|zrange|zrevrange|multi|exec|discard|watch|unwatch|pipeline|scriptLoad|eval|evalsha|publish|subscribe|xadd|xread|xgroupCreate|xgroupDestroy|xack",
                     "Step 4: Perform Redis operations (CRUD, transactions, scripting, pub/sub, streams)")
        S176 = State(176, "close|shutdown", "Step 5: Close the Redis connection to release resources")
        # Define state transitions
        S172.AddNext(S173)
        S173.AddNext(S174)
        S174.AddNext(S175)
        S175.AddNext(S176)
        S173.AddNext(S175)
        Class.AddState(S172)
        self.IRIClfList.append(Class)

        # FSM 39: ActiveMQ Producer in Java
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "ActiveMQ Producer in Java")
        S177 = State(177, "import org.apache.activemq.ActiveMQConnectionFactory|import javax.jms.*",
                     "Step 1: Import necessary ActiveMQ and JMS libraries")
        S178 = State(178, "new ActiveMQConnectionFactory", "Step 2: Create a connection factory for the broker")
        S179 = State(179, "createConnection", "Step 3: Create a connection to the ActiveMQ broker")
        S180 = State(180, "start()", "Step 4: Start the connection to begin communication")
        S181 = State(181, "createSession", "Step 5: Create a session for sending and receiving messages")
        S182 = State(182,
                     "createQueue|createTopic|createTemporaryQueue|createTemporaryTopic|createSharedQueue|createSharedTopic",
                     "Step 6: Create a destination queue or topic for the messages")
        S183 = State(183, "createProducer", "Step 7: Create a producer to send messages to the queue or topic")
        S184 = State(184,
                     "createTextMessage|createMapMessage|createObjectMessage|createBytesMessage|createStreamMessage|createMessage|createBytesMessage",
                     "Step 8: Create a message to be sent")
        S185 = State(185, "send|close()",
                     "Step 9: Send the created message to the queue or topic and close the connection to release resources")
        # Define state transitions
        S177.AddNext(S178)
        S178.AddNext(S179)
        S179.AddNext(S180)
        S180.AddNext(S181)
        S181.AddNext(S182)
        S182.AddNext(S183)
        S183.AddNext(S184)
        S184.AddNext(S185)

        Class.AddState(S177)
        self.IRIClfList.append(Class)

        # FSM 40: ActiveMQ Consumer in Java
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "ActiveMQ Consumer in Java")
        S186 = State(186, "import org.apache.activemq.ActiveMQConnectionFactory|import javax.jms.*",
                     "Step 1: Import necessary ActiveMQ and JMS libraries")
        S187 = State(187, "new ActiveMQConnectionFactory", "Step 2: Create a connection factory for the broker")
        S188 = State(188, "createConnection", "Step 3: Create a connection to the ActiveMQ broker")
        S189 = State(189, "start()", "Step 4: Start the connection to begin communication")
        S190 = State(190, "createSession", "Step 5: Create a session for receiving messages")
        S191 = State(191,
                     "createQueue|createTopic|createTemporaryQueue|createTemporaryTopic|createSharedQueue|createSharedTopic",
                     "Step6: Create a destination queue or topic for receiving messages")
        S192 = State(192, "createConsumer", "Step 7: Create a consumer to receive messages from the queue or topic")
        S193 = State(193, "receive|receiveNoWait|close",
                     "Step 8: Receive a message from the queue or topic and then close the connection to release resources")

        # Define state transitions
        S186.AddNext(S187)
        S187.AddNext(S188)
        S188.AddNext(S189)
        S189.AddNext(S190)
        S190.AddNext(S191)
        S191.AddNext(S192)
        S192.AddNext(S193)
        Class.AddState(S186)
        self.IRIClfList.append(Class)

        # FSM 41: RabbitMQ Producer in Java
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "RabbitMQ Producer in Java")
        S194 = State(194, "import com.rabbitmq.client.*",
                     "Step 1: Import the RabbitMQ client library for communication")
        S195 = State(195, "new ConnectionFactory",
                     "Step 2: Create a connection factory to configure RabbitMQ connection settings")
        S196 = State(196, "newConnection()", "Step 3: Establish a connection to the RabbitMQ broker")
        S197 = State(197, "createChannel()", "Step 4: Create a channel for sending messages")
        S198 = State(198, "queueDeclare|exchangeDeclare", "Step 5: Declare a queue or exchange to send messages to")
        S199 = State(199, "basicPublish|basicReturn",
                     "Step 6: Create and send a message to the declared queue or exchange")
        S200 = State(200, "close()", "Step 7: Close the channel and the connection to release resources")
        # Define state transitions
        S194.AddNext(S195)
        S195.AddNext(S196)
        S196.AddNext(S197)
        S197.AddNext(S198)
        S198.AddNext(S199)
        S199.AddNext(S200)
        Class.AddState(S194)
        self.IRIClfList.append(Class)

        # FSM 42: RabbitMQ Consumer in Java
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "RabbitMQ Consumer in Java")
        S201 = State(201, "import com.rabbitmq.client.*",
                     "Step 1: Import the RabbitMQ client library to enable communication with the RabbitMQ broker")
        S202 = State(202, "new ConnectionFactory",
                     "Step 2: Create a ConnectionFactory instance to configure RabbitMQ connection settings, such as host, port, and authentication credentials")
        S203 = State(203,
                     "setHost|setPort|setUsername|setPassword|setVirtualHost|setConnectionTimeout|setRequestedHeartbeat|setAutomaticRecoveryEnabled|setNetworkRecoveryInterval",
                     "Step 3: Configure the ConnectionFactory settings, including host, port, authentication, virtual host, connection timeout, heartbeat interval, and automatic recovery options")
        S204 = State(204, "newConnection()",
                     "Step 4: Establish a connection to the RabbitMQ broker using the configured ConnectionFactory")
        S205 = State(205, "createChannel()",
                     "Step 5: Create a channel to interact with the message broker, including message consumption and acknowledgment handling")
        S206 = State(206, "new DefaultConsumer|handleDelivery",
                     "Step 6: Implement a message consumer using DefaultConsumer and handle incoming messages in the handleDelivery method")
        S207 = State(207, "basicConsume",
                     "Step 7: Start consuming messages from a specific queue, specifying auto-acknowledge or manual acknowledgment mode")
        # Define state transitions
        S201.AddNext(S202)
        S202.AddNext(S203)
        S203.AddNext(S204)
        S204.AddNext(S205)
        S205.AddNext(S206)
        S206.AddNext(S207)
        Class.AddState(S201)
        self.IRIClfList.append(Class)

        # FSM 43: RocketMQ Producer in Java
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "RocketMQ Producer in Java")
        S208 = State(208,
                     "import org.apache.rocketmq.client.producer.*|import org.apache.rocketmq.common.message.Message;",
                     "Step 1: Import RocketMQ producer-related libraries")
        S209 = State(209, "new DefaultMQProducer|new TransactionMQProducer|new OnewayMQProducer",
                     "Step 2: Create a producer instance (Default, Transactional, or One-way producer)")
        S210 = State(210,
                     "setNamesrvAddr|setRetryTimesWhenSendFailed|setRetryTimesWhenSendAsyncFailed|setSendLatencyFaultEnable|setRetryAnotherBrokerWhenNotStoreOK|setCompressMsgBodyOverHowmuch|setMaxMessageSize|setCreateTopicKey|setSendMsgTimeout|setVipChannelEnabled|setInstanceName",
                     "Step 3: Configure the producer settings. Set the NameServer address and configure retry policies, timeout settings, message size limits, and other advanced parameters to optimize performance and reliability.")
        S211 = State(211, "start()", "Step 4: Start the producer to initialize it for sending messages")
        S212 = State(212, "new Message", "Step 5: Create a message to send")
        S213 = State(213, "send|sendOneway|sendMessageInTransaction",
                     "Step 6: Send the message (sync, async, or transactional)")

        # Define state transitions
        S208.AddNext(S209)
        S209.AddNext(S210)
        S210.AddNext(S211)
        S211.AddNext(S212)
        S212.AddNext(S213)

        Class.AddState(S208)
        self.IRIClfList.append(Class)

        # FSM 44: RocketMQ Consumer in Java
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "RocketMQ Consumer in Java")
        S214 = State(214,
                     "import org.apache.rocketmq.client.consumer.*|import org.apache.rocketmq.common.message.Message;",
                     "Step 1: Import necessary RocketMQ consumer-related libraries, including consumer classes and message handling utilities.")
        S215 = State(215, "new DefaultMQPushConsumer|new DefaultMQPullConsumer",
                     "Step 2: Create a consumer instance. Use DefaultMQPushConsumer for push-based consumption or DefaultMQPullConsumer for pull-based consumption.")
        S216 = State(216,
                     "setNamesrvAddr|setConsumeFromWhere|setMessageModel|setMaxReconsumeTimes|setConsumeThreadMin|setConsumeThreadMax|setPullBatchSize|setConsumeTimeout|setInstanceName|setAdjustThreadPool|setUnitName",
                     "Step 3: Configure the consumer settings. Set the NameServer address, define consumption strategy (e.g., ConsumeFromWhere), choose a message model (Clustering or Broadcasting), and specify retry policies. Additionally, configure thread pool size, batch size, timeout settings, instance name, and other performance-related parameters.")
        S217 = State(217, "subscribe",
                     "Step 4: Subscribe to a specific topic and optionally filter messages based on tags.")
        S218 = State(218, "registerMessageListener",
                     "Step 5: Register a message listener (either MessageListenerConcurrently or MessageListenerOrderly) to handle incoming messages asynchronously.")
        S219 = State(219, "start()",
                     "Step 6: Start the consumer to establish connection with the broker and begin consuming messages.")
        # Define state transitions
        S214.AddNext(S215)
        S215.AddNext(S216)
        S216.AddNext(S217)
        S217.AddNext(S218)
        S218.AddNext(S219)

        Class.AddState(S214)
        self.IRIClfList.append(Class)

        # FSM 45: ProcessBuilder in java.io
        Class = ApiClassifier("Java*", LANG_API_IRI, ".java", "ProcessBuilder in java.io")
        S220 = State(220, "import java.io.*",
                     "Step 1: Import necessary Java I/O classes to handle process input, output, and error streams.")
        S221 = State(221, "new ProcessBuilder|redirectErrorStream",
                     "Step 2: Create a new ProcessBuilder instance, configure it with the command to execute, and optionally redirect error streams to standard output.")
        S222 = State(222, "start()",
                     "Step 3: Start the external process using the start() method, which returns a Process instance representing the running process.")
        S223 = State(223, "getOutputStream|getInputStream",
                     "Step 4: Retrieve the process's input and output streams using getOutputStream() for writing to the process and getInputStream() for reading from it.")
        S224 = State(224, "waitFor()",
                     "Step 5: Call waitFor() to block the current thread until the external process terminates, ensuring proper synchronization.")

        # Define state transitions
        S220.AddNext(S221)
        S221.AddNext(S222)
        S222.AddNext(S223)
        S223.AddNext(S224)
        Class.AddState(S220)
        self.IRIClfList.append(Class)

        # ###########################################################
        # Class: Python*
        # ###########################################################
        # Python面向多编程语言交互的进程间通信方法包括：
        # 套接字技术：TCP/UDP/Websocket
        # 内存共享技术
        # 消息队列
        # gRPC
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

        # FSM 3: WebSocket Client-side by using websocket - client in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py",
                              "WebSocket Client-side by using websocket - client in python")
        S10 = State(10, "import websocket|from websocket import WebSocketApp",
                    "Step 1: Import the websocket and WebSocketApp classes from the websocket library")
        S11 = State(11, "on_message|on_error|on_close|on_ping|on_pong|on_open",
                    "Step 2: Define the callback functions for handling WebSocket events (on_message, on_error, on_close, etc.)")
        S12 = State(12, "WebSocketApp",
                    "Step 3: Create an instance of WebSocketApp with the necessary callback functions and URL")
        S13 = State(13, "run_forever()|run_once()",
                    "Step 4: Start the WebSocket client with run_forever() or run_once() to handle the connection")
        # State transitions for the FSM
        S10.AddNext(S11)
        S11.AddNext(S12)
        S12.AddNext(S13)
        # Add state to the server classifier
        Class.AddState(S10)
        self.IRIClfList.append(Class)

        # FSM 4: WebSocket Server - side by using fastapi in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "WebSocket Server - side by using FastAPI in python")
        S14 = State(14, "from fastapi import .*", "Step 1: Import necessary libraries from FastAPI")
        S15 = State(15, "FastAPI()", "Step 2: Create a FastAPI instance to set up the WebSocket server")
        S16 = State(16, "await websocket.accept()", "Step 3: Accept the incoming WebSocket connection from the client")
        S17 = State(17, "receive_text()|receive_bytes()|receive_json()|send_text()|send_bytes()|send_json()",
                    "Step 4: Handle incoming and outgoing WebSocket messages using appropriate methods")
        # State transitions for the FSM
        S14.AddNext(S15)
        S15.AddNext(S16)
        S16.AddNext(S17)
        # Add state to the server classifier
        Class.AddState(S14)
        self.IRIClfList.append(Class)

        # FSM 5: WebSocket Server - side by using Sanic in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "WebSocket Server - side by using Sanic in python")
        S18 = State(18, "from sanic import Sanic|from sanic.response import .*|from sanic.websocket import .*",
                    "Step 1: Import the necessary modules from Sanic, including Sanic for the app, response for sending responses, and websocket for handling WebSocket connections.")
        S19 = State(19, "Sanic", "Step 2: Create a Sanic app instance to initialize the web server.")
        S20 = State(20, "async def",
                    "Step 3: Define an asynchronous function to handle WebSocket connections and manage the communication logic.")
        S21 = State(21, "recv()|send",
                    "Step 4: Use WebSocket's recv() method to receive messages from clients and send() method to send messages back to clients.")
        # State transitions for the FSM
        S18.AddNext(S19)
        S19.AddNext(S20)
        S20.AddNext(S21)
        # Add state to the server classifier
        Class.AddState(S18)
        self.IRIClfList.append(Class)

        # FSM 6: WebSocket Server - side by using Tornado in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "WebSocket Server - side by using Tornado in python")
        S22 = State(22, "import tornado.ioloop|import tornado.web|import tornado.websocket|from tornado import.*",
                    "Step 1: Import necessary Tornado libraries for WebSocket server")
        S23 = State(23, "WebSocketHandler", "Step 2: Define a WebSocketHandler class to handle WebSocket connections")
        S24 = State(24, "open|on_message|on_close|on_error",
                    "Step 3: Implement WebSocketHandler methods such as open, on_message, on_close, and on_error to handle the lifecycle of a WebSocket connection")
        S25 = State(25, "Application",
                    "Step 4: Create an Application instance and add the WebSocketHandler to route WebSocket connections")
        # State transitions for the FSM
        S22.AddNext(S23)
        S23.AddNext(S24)
        S24.AddNext(S25)
        # Add state to the server classifier
        Class.AddState(S22)
        self.IRIClfList.append(Class)

        # FSM 7: WebSocket Client - side by using Tornado in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "WebSocket Client - side by using Tornado in python")
        S26 = State(26, "import tornado.ioloop|import tornado.websocket|from tornado import.*",
                    "Step 1: Import necessary Tornado libraries for WebSocket client")
        S27 = State(27, "WebSocketClientConnection",
                    "Step 2: Create a WebSocketClientConnection to initiate a WebSocket connection to the server")
        S28 = State(28, "open|on_message|on_close|on_error",
                    "Step 3: Implement methods like open, on_message, on_close, and on_error to handle WebSocket connection events and data")
        S29 = State(29, "websocket_connect",
                    "Step 4: Use websocket_connect to establish the connection with the WebSocket server")
        # State transitions for the FSM
        S26.AddNext(S27)
        S27.AddNext(S28)
        S28.AddNext(S29)
        # Add state to the server classifier
        Class.AddState(S26)
        self.IRIClfList.append(Class)

        # FSM 8: WebSocket Server-side based on autobahn+twisted in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py",
                              "WebSocket Server-side based on autobahn+twisted in python")
        S30 = State(30,
                    "from autobahn.twisted.websocket import .*|from autobahn.twisted.websocket import WebSocketServerProtocol|from autobahn.twisted.websocket import WebSocketServerFactory|from twisted.internet import reactor",
                    "Step 1: Import Autobahn and Twisted modules")
        S31 = State(31, "WebSocketServerProtocol", "Step 2: Define the server-side WebSocket protocol class")
        S32 = State(32, "onConnect|onOpen|onMessage|onClose", "Step 3: Implement lifecycle methods of the WebSocket protocol")
        S33 = State(33, "WebSocketServerFactory", "Step 4: Create the WebSocket server factory")
        S34 = State(34, "protocol", "Step 5: Assign the protocol class to the factory")
        S35 = State(35, "listenTCP", "Step 6: Bind the factory to a TCP port using reactor.listenTCP")
        S36 = State(36, "run", "Step 7: Start the reactor loop")
        # State transitions for the FSM
        S30.AddNext(S31)
        S31.AddNext(S32)
        S32.AddNext(S33)
        S33.AddNext(S34)
        S34.AddNext(S35)
        S35.AddNext(S36)
        # Add state to the server classifier
        Class.AddState(S30)
        self.IRIClfList.append(Class)

        # FSM 9: WebSocket Client-side based on autobahn+twisted in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py",
                              "WebSocket Client-side based on autobahn+twisted in python")
        S37 = State(37,
                    "from autobahn.twisted.websocket import .*|from autobahn.twisted.websocket import WebSocketClientProtocol|from autobahn.twisted.websocket import WebSocketClientFactory|from twisted.internet import reactor",
                    "Step 1: Import Autobahn and Twisted modules")
        S38 = State(38, "WebSocketClientProtocol", "Step 2: Define the client-side WebSocket protocol class")
        S39 = State(39, "onOpen|onMessage|onClose", "Step 3: Implement the WebSocket protocol lifecycle methods")
        S40 = State(40, "WebSocketClientFactory", "Step 4: Create the WebSocket client factory")
        S41 = State(41, "protocol", "Step 5: Assign the protocol class to the factory")
        S42 = State(42, "connectTCP", "Step 6: Connect to the server using reactor.connectTCP")
        S43 = State(43, "run", "Step 7: Start the reactor loop")
        # State transitions for the FSM
        S37.AddNext(S38)
        S38.AddNext(S39)
        S39.AddNext(S40)
        S40.AddNext(S41)
        S41.AddNext(S42)
        S42.AddNext(S43)
        # Add state to the server classifier
        Class.AddState(S37)
        self.IRIClfList.append(Class)

        # FSM 10: WebSocket Server-side based on asyncio+autobahn in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py",
                              "Async WebSocket Server-side based on asyncio+autobahn in python")
        S44 = State(44,
                    "from autobahn.asyncio.websocket import .*|from autobahn.asyncio.websocket import import WebSocketServerProtocol|from autobahn.asyncio.websocket import import WebSocketServerFactory",
                    "Step 1: Import Autobahn asyncio-based server components")
        S45 = State(45, "WebSocketServerProtocol", "Step 2: Define the asyncio-based WebSocket protocol class")
        S46 = State(46, "async def onMessage|async def processMessage", "Step 3: Implement async message handling methods")
        S47 = State(47, "WebSocketServerFactory", "Step 4: Create the WebSocket server factory")
        S48 = State(48, "get_event_loop", "Step 5: Obtain the asyncio event loop")
        S49 = State(49, "create_server", "Step 6: Create a WebSocket server coroutine")
        S50 = State(50, "run_until_complete|run_forever", "Step 7: Run the asyncio event loop")
        S51 = State(51, "close", "Step 8: Clean up and close the event loop")
        # State transitions for the FSM
        S44.AddNext(S45)
        S45.AddNext(S46)
        S46.AddNext(S47)
        S47.AddNext(S48)
        S48.AddNext(S49)
        S49.AddNext(S50)
        S50.AddNext(S51)
        # Add state to the server classifier
        Class.AddState(S44)
        self.IRIClfList.append(Class)

        # FSM 11: HTTP Server - side by using http.server in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "HTTP Server - side by using http.server in python")
        S52 = State(52, "from http.server import HTTPServer|from http.server import BaseHTTPRequestHandler",
                    "Step 1: Import HTTPServer and BaseHTTPRequestHandler from the http.server module")
        S53 = State(53, "BaseHTTPRequestHandler",
                    "Step 2: Define a custom request handler class by extending BaseHTTPRequestHandler")
        S54 = State(54, "do_GET|do_POST|do_PUT|do_DELETE|do_HEAD",
                    "Step 3: Override request handling methods such as do_GET or do_POST")
        S55 = State(55, "HTTPServer", "Step 4: Create an HTTPServer instance with the handler class and server address")
        S56 = State(56, "serve_forever()",
                    "Step 5: Start the server to handle requests indefinitely using serve_forever()")
        # State transitions for the FSM
        S52.AddNext(S53)
        S53.AddNext(S54)
        S54.AddNext(S55)
        S55.AddNext(S56)
        # Add state to the server classifier
        Class.AddState(S52)
        self.IRIClfList.append(Class)

        # FSM 12: HTTP Client - side by using http.client in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "HTTP Client - side by using http.client in python")
        S57 = State(57, "from http.client import HTTPConnection|HTTPSConnection",
                    "Step 1: Import HTTPConnection or HTTPSConnection")
        S58 = State(58, "HTTPConnection|HTTPSConnection",
                    "Step 2: Create a connection object with the target server and port")
        S59 = State(59, "request|GET|POST|PUT|DELETE",
                    "Step 3: Send an HTTP request using request(method, url, body, headers)")
        S60 = State(60, "getresponse", "Step 4: Receive and process the HTTP response")
        S61 = State(61, "close", "Step 5: Close the connection")
        # State transitions for the FSM
        S57.AddNext(S58)
        S58.AddNext(S59)
        S59.AddNext(S60)
        S60.AddNext(S61)
        # Add state to the server classifier
        Class.AddState(S57)
        self.IRIClfList.append(Class)

        # FSM 13: HTTP Client-side by using requests in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "HTTP Client-side by using requests in python")
        S62 = State(62, "import requests",
                    "Step 1: Import the requests module to enable HTTP client functionality.")
        S63 = State(63, "requests.get|requests.post|requests.put|requests.delete",
                    "Step 2: Send an HTTP request using the appropriate method such as GET, POST, PUT, or DELETE.")
        S64 = State(64, "response.status_code",
                    "Step 3: Check the HTTP response status code to determine if the request was successful.")
        S65 = State(65, "response.text|response.json|response.content|response.headers|response.cookies",
                    "Step 4: Parse the response data using properties like .text, .json(), .content, .headers, or .cookies.")

        # State transitions for the FSM
        S62.AddNext(S63)
        S63.AddNext(S64)
        S64.AddNext(S65)
        # Add state to the classifier
        Class.AddState(S62)
        self.IRIClfList.append(Class)

        # FSM 14: Synchronous HTTP Client-side by using httpx in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "HTTP Client-side by using httpx in python")
        S66 = State(66, "import httpx", "Step 1: Import the httpx library")
        S67 = State(67, "with httpx.Client", "Step 2: Create a synchronous HTTP client using a context manager")
        S68 = State(68, "get|post|put|delete",
                    "Step 3: Send HTTP requests using supported methods like GET, POST, PUT, DELETE")
        S69 = State(69, "status_code|text|json|content|headers|cookies|raise_for_status",
                    "Step 4: Access response properties such as status code, body content, headers, cookies, or raise exceptions")
        # State transitions for the FSM
        S66.AddNext(S67)
        S67.AddNext(S68)
        S68.AddNext(S69)
        # Add state to the server classifier
        Class.AddState(S66)
        self.IRIClfList.append(Class)

        # FSM 15: Asynchronous HTTP Client-side by using httpx+asyncio in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "HTTP Client-side by using httpx+asyncio in python")
        S70 = State(70, "import httpx|import asyncio", "Step 1: Import httpx and asyncio libraries")
        S71 = State(71, "async with httpx.AsyncClient",
                    "Step 2: Create an asynchronous HTTP client using a context manager")
        S72 = State(72, "get|post|put|delete",
                    "Step 3: Send HTTP requests asynchronously using methods like GET, POST, PUT, DELETE")
        S73 = State(73, "status_code|text|json|content|headers|cookies|raise_for_status",
                    "Step 4: Access response details or raise exceptions on non-success status codes")
        # State transitions for the FSM
        S70.AddNext(S71)
        S71.AddNext(S72)
        S72.AddNext(S73)
        # Add state to the server classifier
        Class.AddState(S70)
        self.IRIClfList.append(Class)

        # FSM 16: HTTP Server - side by using Flask in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "HTTP Server - side by using Flask in python")
        S74 = State(74, "import flask|from flask import Flask|from flask import request|from flask import jsonify",
                    "Step 1: Import the required Flask modules")
        S75 = State(75, "Flask", "Step 2: Instantiate the Flask application object")
        S76 = State(76, "route", "Step 3: Define routes with @app.route decorators")
        S77 = State(77, "get_json|GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS|form|get_data|read|request.form|request.args|request.data|request.files|request.path|request.path|request.headers|request.args|request.get_data",
                    "Step 4: Handle incoming request data using Flask's request object")
        S78 = State(78, "return", "Step 5: Create and return the response")
        # FSM transitions
        S74.AddNext(S75)
        S75.AddNext(S76)
        S76.AddNext(S77)
        S77.AddNext(S78)
        # Add state to the server classifier
        Class.AddState(S74)
        self.IRIClfList.append(Class)

        # FSM 17: HTTP Server - side by using FastAPI in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "HTTP Server - side by using FastAPI in python")
        S79 = State(79, "from fastapi import FastAPI|from fastapi import.*",
                    "Step 1: Import FastAPI and necessary components from the FastAPI module")
        S80 = State(80, "FastAPI",
                    "Step 2: Instantiate the FastAPI application object, which will handle HTTP requests")
        S81 = State(81, "get|post|put|delete",
                    "Step 3: Define route handlers using decorators (e.g., get, post) for each HTTP method")
        S82 = State(82, "BaseModel",
                    "Step 4: Optionally, define request and response models using Pydantic BaseModel for validation")
        S83 = State(83, "Query|Path|Body",
                    "Step 5: Extract query parameters, path variables, and request body using FastAPI's parameter extraction mechanisms")
        S84 = State(84, "return",
                    "Step 6: Return the response from the route handler, typically as JSON or using FastAPI's built - in response classes")
        # State transitions
        S79.AddNext(S80)
        S80.AddNext(S81)
        S81.AddNext(S82)
        S82.AddNext(S83)
        S83.AddNext(S84)
        S81.AddNext(S83)
        # Add state to the server classifier
        Class.AddState(S79)
        self.IRIClfList.append(Class)

        # FSM 18: HTTP Server - side by using Sanic in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "HTTP Server - side by using Sanic in python")
        S96 = State(96, "from sanic import.*|from sanic.response import.*",
                    "Step 1: Import necessary modules from Sanic")
        S97 = State(97, "Sanic", "Step 2: Instantiate the Sanic app object")
        S98 = State(98, "route", "Step 3: Define routes using the @app.route decorator")
        S99 = State(99, "async def", "Step 4: Define asynchronous route handlers")
        S100 = State(100, "text|html|file|stream|redirect|empty|json",
                     "Step 5: Return appropriate response types such as text, HTML, file, stream, redirect, empty, or JSON")
        # State transitions
        S96.AddNext(S97)
        S97.AddNext(S98)
        S98.AddNext(S99)
        S99.AddNext(S100)
        # Add state to the server classifier
        Class.AddState(S96)
        self.IRIClfList.append(Class)

        # FSM 19: HTTP Server - side by using Sanic in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "HTTP Server - side by using Sanic in python")
        S101 = State(101,
                     "from starlette.responses import.*|from starlette.requests import Request|from starlette.applications import Starlette|from starlette.routing import Route|import uvicorn",
                     "Step 1: Import necessary modules from Starlette")
        S102 = State(102, "async def|Request", "Step 2: Define asynchronous route handlers and request objects")
        S103 = State(103,
                     "JSONResponse|PlainTextResponse|HTMLResponse|RedirectResponse|FileResponse|StreamingResponse|UJSONResponse|Response",
                     "Step 3: Return appropriate response types such as JSON, plain text, HTML, redirect, file, streaming, etc.")
        S104 = State(104, "Route", "Step 4: Define routes using the Route object")
        S105 = State(105, "Starlette", "Step 5: Instantiate the Starlette application")
        S106 = State(106, "run", "Step 6: Run the application with uvicorn")
        # State transitions
        S101.AddNext(S102)
        S102.AddNext(S103)
        S103.AddNext(S104)
        S104.AddNext(S105)
        S105.AddNext(S106)
        # Add state to the server classifier
        Class.AddState(S101)
        self.IRIClfList.append(Class)

        # FSM 20: HTTP Server-side based on Tornado in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "HTTP Server-side based on Tornado in python")
        S107 = State(107, "import tornado.ioloop|import tornado.web|from tornado import .*",
                     "Step 1: Import necessary modules from the Tornado framework")
        S108 = State(108, "RequestHandler",
                     "Step 2: Define a request handler class by inheriting from tornado.web.RequestHandler")
        S109 = State(109, "get|post",
                     "Step 3: Implement HTTP request methods such as get() or post() in the handler class")
        S110 = State(110, "Application",
                     "Step 4: Create a tornado.web.Application instance and route handlers to URLs")
        S111 = State(111, "listen",
                     "Step 5: Bind the application to a specific port using the listen() method")
        S112 = State(112, "start",
                     "Step 6: Start the I/O loop with tornado.ioloop.IOLoop.current().start()")
        # State transitions
        S107.AddNext(S108)
        S108.AddNext(S109)
        S109.AddNext(S110)
        S110.AddNext(S111)
        S111.AddNext(S112)
        # Add state to the server classifier
        Class.AddState(S107)
        self.IRIClfList.append(Class)

        # FSM 21: HTTP Client-side based on Tornado in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "HTTP Client-side based on Tornado in python")
        S113 = State(113, "import tornado.ioloop|import tornado.httpclient|from tornado import .*",
                     "Step 1: Import necessary modules from the Tornado framework for HTTP client functionality")
        S114 = State(114, "AsyncHTTPClient",
                     "Step 2: Create an instance of tornado.httpclient.AsyncHTTPClient to manage asynchronous requests")
        S115 = State(115, "fetch",
                     "Step 3: Use the fetch() method to send an asynchronous HTTP request")
        S116 = State(116, "decode()",
                     "Step 4: Decode the response body to retrieve the actual content")
        S117 = State(117, "run_sync",
                     "Step 5: Run the asynchronous fetch function using tornado.ioloop.IOLoop.current().run_sync()")
        # State transitions for the FSM
        S113.AddNext(S114)
        S114.AddNext(S115)
        S115.AddNext(S116)
        S116.AddNext(S117)
        # Add state to the classifier
        Class.AddState(S113)
        self.IRIClfList.append(Class)

        # FSM 22: TCP Server - side by using socket in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "TCP Server - side by using socket in python")
        S118 = State(118, "import socket", "Step 1: Import the socket module")
        S119 = State(119, "SOCK_STREAM", "Step 2: Create a TCP socket object using IPv4")
        S120 = State(120, "bind", "Step 3: Bind the socket to a local IP address and port")
        S121 = State(121, "listen", "Step 4: Start listening for incoming client connections")
        S122 = State(122, "accept()", "Step 5: Accept a connection request from a client")
        S123 = State(123, "recv|send", "Step 6: Receive data from or send data to the client")
        S124 = State(124, "close", "Step 7: Close the connection with the client")
        # State transitions
        S118.AddNext(S119)
        S119.AddNext(S120)
        S120.AddNext(S121)
        S121.AddNext(S122)
        S122.AddNext(S123)
        S123.AddNext(S124)
        # Add state to the server classifier
        Class.AddState(S118)
        self.IRIClfList.append(Class)

        # FSM 23: TCP Client - side by using socket in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "TCP Client - side by using socket in python")
        S125 = State(125, "import socket", "Step 1: Import the socket module")
        S126 = State(126, "SOCK_STREAM", "Step 2: Create a TCP socket object using IPv4")
        S127 = State(127, "connect", "Step 3: Connect the socket to the target server's IP and port")
        S128 = State(128, "send|recv", "Step 4: Send data to or receive data from the server")
        S129 = State(129, "close", "Step 5: Close the connection with the server")
        # State transitions
        S125.AddNext(S126)
        S126.AddNext(S127)
        S127.AddNext(S128)
        S128.AddNext(S129)
        # Add state to the server classifier
        Class.AddState(S125)
        self.IRIClfList.append(Class)

        # FSM 24: TCP Server-side based on twisted in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "TCP Server-side based on twisted in python")
        S130 = State(130,
                     "from twisted.internet.protocol import protocol|from twisted.internet.protocol import Factory|from twisted.internet.protocol import .*|from twisted.internet import reactor",
                     "Step 1: Import necessary Twisted modules for implementing a TCP server")
        S131 = State(131, "Protocol|Factory",
                     "Step 2: Define custom Protocol and Factory classes to handle TCP server behavior")
        S132 = State(132, "connectionMade|connectionLost|dataReceived|buildProtocol",
                     "Step 3: Implement connection lifecycle methods and data handling logic")
        S133 = State(133, "listenTCP",
                     "Step 4: Start listening for TCP connections using reactor.listenTCP with the factory")
        S134 = State(134, "run",
                     "Step 5: Start the Twisted reactor event loop to begin handling events")
        # Transitions
        S130.AddNext(S131)
        S131.AddNext(S132)
        S132.AddNext(S133)
        S133.AddNext(S134)
        Class.AddState(S130)
        self.IRIClfList.append(Class)

        # FSM 25: TCP Client-side based on twisted in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "TCP Client-side based on twisted in python")
        S135 = State(135,
                     "from twisted.internet.protocol import protocol|from twisted.internet.protocol import ClientFactory|from twisted.internet.protocol import .*|from twisted.internet import reactor",
                     "Step 1: Import necessary Twisted modules for implementing a TCP client")
        S136 = State(136, "Protocol|ClientFactory",
                     "Step 2: Define custom Protocol and ClientFactory classes to manage client behavior")
        S137 = State(137,
                     "startedConnecting|connectionLost|dataReceived|buildProtocol|clientConnectionFailed|clientConnectionLost",
                     "Step 3: Implement methods for connection lifecycle and handling received data or connection failures")
        S138 = State(138, "connectTCP", "Step 4: Connect to the server using reactor.connectTCP with a ClientFactory")
        S139 = State(139, "run", "Step 5: Start the Twisted reactor event loop to process client-side events")
        # Transitions
        S135.AddNext(S136)
        S136.AddNext(S137)
        S137.AddNext(S138)
        S138.AddNext(S139)
        Class.AddState(S135)
        self.IRIClfList.append(Class)

        # FSM 26: TCP Server - side by using socketserver in python
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

        # FSM 27: UDP communication by using socket in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "UDP communication by using socket in python")
        S146 = State(146, "import socket|from socket import .*", "Step 1: Import the socket module")
        S147 = State(147, "SOCK_DGRAM", "Step 2: Create a UDP socket")
        S148 = State(148, "bind", "Step 3: Bind the socket to a local IP address and port (server - side only)")
        S149 = State(149, "sendto|recvfrom|recvfrom_into",
                     "Step 4: Send and receive data using appropriate UDP methods")
        S150 = State(150, "close()", "Step 5: Close the socket to release resources")
        # State transitions
        S146.AddNext(S147)
        S147.AddNext(S148)
        S148.AddNext(S149)
        S149.AddNext(S150)
        # Add state to the server classifier
        Class.AddState(S146)
        self.IRIClfList.append(Class)

        # FSM 28: UDP Server - side by using socketserver in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "UDP Server - side by using socketserver in python")
        S151 = State(151, "import socketserver|from socketserver import.*",
                     "Step 1: Import socketserver module and its components.")
        S152 = State(152, "BaseRequestHandler", "Step 2: Define a handler class that inherits from BaseRequestHandler.")
        S153 = State(153, "handle", "Step 3: Implement the handle method to process client requests.")
        S154 = State(154, "recv|send|sendall|write|read",
                     "Step 4: Use methods like recv(), send(), sendall(), write(), or read() to communicate with the client.")
        S155 = State(155, "UDPServer",
                     "Step 5: Create a UDP server instance using UDPServer and bind it to an address.")
        S156 = State(156, "serve_forever()", "Step 6: Call serve_forever() to start the server and keep it running.")
        # State transitions
        S151.AddNext(S152)
        S152.AddNext(S153)
        S153.AddNext(S154)
        S154.AddNext(S155)
        S155.AddNext(S156)
        # Add state to the server classifier
        Class.AddState(S151)
        self.IRIClfList.append(Class)

        # FSM 29: UDP based on twisted in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "UDP based on twisted in python")
        S157 = State(157,
                     "from twisted.internet import protocol|from twisted.internet import reactor|from twisted.internet import .*",
                     "Step 1: Import Twisted networking modules")
        S158 = State(158, "DatagramProtocol", "Step 2: Define the UDP protocol by extending DatagramProtocol")
        S159 = State(159, "startProtocol|stopProtocol|connectionRefused|datagramReceived",
                     "Step 3: Implement key UDP protocol methods")
        S160 = State(160, "listenUDP", "Step 4: Bind the UDP protocol to a port using reactor.listenUDP")
        S161 = State(161, "run", "Step 5: Start the reactor loop")
        # State transitions for the FSM
        S157.AddNext(S158)
        S158.AddNext(S159)
        S159.AddNext(S160)
        S160.AddNext(S161)
        # Add state to the server classifier
        Class.AddState(S157)
        self.IRIClfList.append(Class)

        # FSM 30: gRPC Server - side based on grpcio in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "gRPC Server - side based on grpcio in python")
        S162 = State(162, "import grpc|from concurrent import futures",
                     "Step 1: Import necessary libraries (grpc and futures) for server creation")
        S163 = State(163, "grpc.server|futures.ThreadPoolExecutor",
                     "Step 2: Create a gRPC server with a thread pool executor for concurrency")
        S164 = State(164, "add_insecure_port", "Step 3: Bind the server to a port using add_insecure_port method")
        S165 = State(165, "start()", "Step 4: Start the server to begin listening for incoming gRPC requests")
        # State transitions
        S162.AddNext(S163)
        S163.AddNext(S164)
        S164.AddNext(S165)
        # Add state to the server classifier
        Class.AddState(S162)
        self.IRIClfList.append(Class)

        # FSM 31: DBus Client - side based on dbus(Method invoke) in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py",
                              "DBus Client - side based on dbus(Method invoke) in python")
        S166 = State(166, "import dbus", "Step 1: Import the dbus module to interact with the D - Bus system")
        S167 = State(167, "SessionBus()", "Step 2: Connect to the session bus to access user - level D - Bus services")
        S168 = State(168, "get_object", "Step 3: Obtain a remote object that implements the desired D - Bus interface")
        S169 = State(169, "get_dbus_method",
                     "Step 4: Retrieve a method from the object and call it to interact with the D - Bus service")
        # State transitions
        S166.AddNext(S167)
        S167.AddNext(S168)
        S168.AddNext(S169)
        # Add state to the server classifier
        Class.AddState(S166)
        self.IRIClfList.append(Class)

        # FSM 32: Pipe based on subprocess in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Pipe based on subprocess in python")
        S170 = State(170, "import subprocess", "Step 1: Import the subprocess module to interact with system processes")
        S171 = State(171, "PIPE", "Step 2: Use subprocess.PIPE to create a pipe for communication between processes")
        S172 = State(172, "Popen",
                     "Step 3: Start a new process using subprocess.Popen and connect to the pipe for input/output")
        S173 = State(173, "communicate()",
                     "Step 4: Use the communicate() method to send data to the process and retrieve the output")
        # State transitions
        S170.AddNext(S171)
        S171.AddNext(S172)
        S172.AddNext(S173)
        # Add state to the client classifier
        Class.AddState(S170)
        self.IRIClfList.append(Class)

        # FSM 33: RabbitMQ consumer based on pika in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "RabbitMQ consumer based on pika in python")
        S174 = State(174, "import pika|from pika import .*",
                     "Step 1: Import the pika library to consume messages from RabbitMQ")
        S175 = State(175, "BlockingConnection", "Step 2: Connect to the RabbitMQ server using a blocking connection")
        S176 = State(176, "channel", "Step 3: Open a channel to start message consumption")
        S177 = State(177, "queue_declare", "Step 4: Declare the queue from which messages will be consumed")
        S178 = State(178, "basic_consume", "Step 5: Set up the callback function to handle incoming messages")
        S179 = State(179, "start_consuming", "Step 6: Start consuming messages in a blocking event loop")
        # State transitions
        S174.AddNext(S175)
        S175.AddNext(S176)
        S176.AddNext(S177)
        S177.AddNext(S178)
        S178.AddNext(S179)
        # Add state to the client classifier
        Class.AddState(S174)
        self.IRIClfList.append(Class)

        # FSM 34: Kafka producer in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Kafka producer in python")
        S180 = State(180, "from kafka import KafkaProducer|from kafka import .*|import kafka",
                     "Step 1: Import the Kafka client library and required modules")
        S181 = State(181, "KafkaProducer",
                     "Step 2: Create a KafkaProducer instance with appropriate configurations (e.g., bootstrap_servers)")
        S182 = State(182, "send|flush",
                     "Step 3: Send messages to a specific topic and flush the buffer to ensure delivery")
        S183 = State(183, "close", "Step 4: Close the producer to release resources properly")
        # State transitions
        S180.AddNext(S181)
        S181.AddNext(S182)
        S182.AddNext(S183)
        # Add state to the client classifier
        Class.AddState(S180)
        self.IRIClfList.append(Class)

        # FSM 35: Kafka consumer in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Kafka consumer in python")
        S184 = State(184, "from kafka import KafkaConsumer|from kafka import .*| import kafka",
                     "Step 1: Import the Kafka client library for consumer functionality")
        S185 = State(185, "KafkaConsumer",
                     "Step 2: Create a KafkaConsumer instance, subscribe to one or more topics, and poll for messages")
        S186 = State(186, "close", "Step 3: Close the consumer to properly clean up resources")
        # State transitions
        S184.AddNext(S185)
        S185.AddNext(S186)
        # Add state to the client classifier
        Class.AddState(S184)
        self.IRIClfList.append(Class)

        # FSM 36: Async Kafka consumer based on asyncio+aiokafka in python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Async Kafka consumer in python")
        S187 = State(187,
                     "import asyncio|from aiokafka import AIOKafkaConsumer|from aiokafka import .*|import aiokafka",
                     "Step 1: Import asyncio and aiokafka to enable asynchronous Kafka message consumption")
        S188 = State(188, "AIOKafkaConsumer",
                     "Step 2: Create an AIOKafkaConsumer instance, subscribe to topics, and configure group ID")
        S189 = State(189, "start()",
                     "Step 3: Start the consumer to establish the connection and begin fetching messages")
        S190 = State(190, "stop()", "Step 4: Gracefully stop the consumer and close the connection")
        # State transitions
        S187.AddNext(S188)
        S188.AddNext(S189)
        S189.AddNext(S190)
        # Add state to the client classifier
        Class.AddState(S187)
        self.IRIClfList.append(Class)

        # FSM 37: ActiveMQ Consumer in Python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "ActiveMQ Consumer in Python")
        S191 = State(191, "import stomp|from stomp import .*",
                     "Step 1: Import the stomp.py module for STOMP protocol communication")
        S192 = State(192, "Connection", "Step 2: Create a connection object and define broker address/port")
        S193 = State(193, "set_listener", "Step 3: Set a custom listener to handle incoming messages")
        S194 = State(194, "connect", "Step 4: Establish connection with broker using credentials")
        S195 = State(195, "subscribe", "Step 5: Subscribe to the queue or topic to receive messages")
        # State transitions
        S191.AddNext(S192)
        S192.AddNext(S193)
        S193.AddNext(S194)
        S194.AddNext(S195)
        # Add state to the client classifier
        Class.AddState(S191)
        self.IRIClfList.append(Class)

        # FSM 38: ActiveMQ Producer in Python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "ActiveMQ Producer in Python")
        S196 = State(196,
                     "import stomp|from stomp import .*",
                     "Step 1: Import the stomp.py module for STOMP protocol communication")
        S197 = State(197,
                     "Connection",
                     "Step 2: Create a Connection object and configure the broker (host and port)")
        S198 = State(198,
                     "send",
                     "Step 3: Send a message to the specified destination using the STOMP connection")
        # State transitions
        S196.AddNext(S197)
        S197.AddNext(S198)
        # Add state to the client classifier
        Class.AddState(S196)
        self.IRIClfList.append(Class)

        # FSM 39: Mosquitto Producer based on mqtt in Python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Mosquitto Producer based on mqtt in Python")
        S199 = State(199, "import paho.mqtt.client", "Step 1: Import the Paho MQTT client library")
        S200 = State(200, "Client", "Step 2: Create an MQTT client instance")
        S201 = State(201, "on_connect|connect",
                     "Step 3: Define connection callback and establish connection to the broker")
        S202 = State(202, "publish", "Step 4: Publish a message to a specific topic")
        S203 = State(203, "loop_start()", "Step 5: Start the MQTT loop to handle network traffic asynchronously")
        # State transitions
        S199.AddNext(S200)
        S200.AddNext(S201)
        S201.AddNext(S202)
        S202.AddNext(S203)
        Class.AddState(S199)
        self.IRIClfList.append(Class)

        # FSM 40: Mosquitto Consumer based on mqtt in Python
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "Mosquitto Consumer based on mqtt in Python")
        S204 = State(204, "import paho.mqtt.client", "Step 1: Import the Paho MQTT client library")
        S205 = State(205, "Client", "Step 2: Create an MQTT client instance")
        S206 = State(206, "on_connect|connect",
                     "Step 3: Define connection callback and establish connection to the broker")
        S207 = State(207, "subscribe|on_message",
                     "Step 4: Subscribe to topics and define a callback function to handle incoming messages")
        S208 = State(208, "loop_forever",
                     "Step 5: Start the MQTT loop to handle network traffic and process incoming messages continuously")
        # State transitions
        S204.AddNext(S205)
        S205.AddNext(S206)
        S206.AddNext(S207)
        S207.AddNext(S208)
        Class.AddState(S204)
        self.IRIClfList.append(Class)

        # FSM 41: ZeroMQ Consumer in Python(PUB/SUB)
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "ZeroMQ Consumer in Python(PUB/SUB)")
        S209 = State(209, "import zmq|from zmq import .*", "Step 1: Import the zmq library for ZeroMQ functionalities")
        S210 = State(210, "Context()", "Step 2: Create a ZeroMQ context for managing sockets")
        S211 = State(211, "SUB", "Step 3: Create a SUB socket to subscribe to messages")
        S212 = State(212, "connect", "Step 4: Connect the SUB socket to the publisher's endpoint")
        S213 = State(213,
                     "send|recv|send_multipart|recv_multipart|send_json|recv_json|send_string|recv_string|send_pyobj|recv_pyobj",
                     "Step 5: Receive messages from the publisher using recv methods")
        # State transitions
        S209.AddNext(S210)
        S210.AddNext(S211)
        S211.AddNext(S212)
        S212.AddNext(S213)
        Class.AddState(S209)
        self.IRIClfList.append(Class)

        # FSM 42: ZeroMQ Producer in Python(REQ/REP)
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "ZeroMQ Producer in Python(REQ/REP)")
        S214 = State(214, "import zmq|from zmq import .*", "Step 1: Import the zmq library for ZeroMQ functionalities")
        S215 = State(215, "Context()", "Step 2: Create a ZeroMQ context for managing sockets")
        S216 = State(216, "REQ", "Step 3: Create a REQ socket for sending requests")
        S217 = State(217, "connect", "Step 4: Connect the REQ socket to the server endpoint")
        S218 = State(218,
                     "send|recv|send_multipart|recv_multipart|send_json|recv_json|send_string|recv_string|send_pyobj|recv_pyobj",
                     "Step 5: Send a request and wait for a reply using send/recv methods")
        # State transitions
        S214.AddNext(S215)
        S215.AddNext(S216)
        S216.AddNext(S217)
        S217.AddNext(S218)
        Class.AddState(S214)
        self.IRIClfList.append(Class)

        # FSM 43: ZeroMQ Consumer in Python(REQ/REP)
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "ZeroMQ Consumer in Python(REQ/REP)")
        S219 = State(219, "import zmq|from zmq import .*", "Step 1: Import the zmq library for ZeroMQ functionalities")
        S220 = State(220, "Context()", "Step 2: Create a ZeroMQ context for managing sockets")
        S221 = State(221, "REP", "Step 3: Create a REP socket for responding to requests")
        S222 = State(222, "bind", "Step 4: Bind the REP socket to an endpoint to listen for incoming requests")
        S223 = State(223,
                     "send|recv|send_multipart|recv_multipart|send_json|recv_json|send_string|recv_string|send_pyobj|recv_pyobj",
                     "Step 5: Receive a request and send a reply using send/recv methods")
        # State transitions
        S219.AddNext(S220)
        S220.AddNext(S221)
        S221.AddNext(S222)
        S222.AddNext(S223)
        Class.AddState(S219)
        self.IRIClfList.append(Class)

        # FSM 44: ZeroMQ Producer in Python(PUB/SUB)
        Class = ApiClassifier("Python*", LANG_API_IRI, ".py", "ZeroMQ Producer in Python(PUB/SUB)")
        S224 = State(224, "import zmq|from zmq import .*", "Step 1: Import the zmq library for ZeroMQ functionalities")
        S225 = State(225, "Context()", "Step 2: Create a ZeroMQ context for managing sockets")
        S226 = State(226, "PUB", "Step 3: Create a PUB socket to publish messages")
        S227 = State(227, "bind", "Step 4: Bind the PUB socket to an endpoint to start sending messages")
        S228 = State(228,
                     "send|recv|send_multipart|recv_multipart|send_json|recv_json|send_string|recv_string|send_pyobj|recv_pyobj",
                     "Step 5: Send messages using send/recv methods, typically using send for publishing")
        # State transitions
        S224.AddNext(S225)
        S225.AddNext(S226)
        S226.AddNext(S227)
        S227.AddNext(S228)
        Class.AddState(S224)
        self.IRIClfList.append(Class)


        ############################################################
        # Class: JavaScript*
        ############################################################
        # JavaScript语言面向多编程语言交互的进程间通信方法包括：
        # 套接字技术：TCP/UDP/Websocket/HTTP
        # gRPC
        ############################################################
        # FSM 1: WebSocket Client-side based on browser native API in JavaScript
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js .ts .html",
                              "WebSocket Client-side based on browser native API in JavaScript")
        S0 = State(0, "new WebSocket", "Step 1: Initialize a new WebSocket connection.")
        S1 = State(1, "onopen|onmessage|onerror|onclose",
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
        S3 = State(3, r"require\(['\"](ws)['\"]\)", "Step 1: Require the WebSocket library ('ws').")
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
        S6 = State(6, r"require\(['\"](ws)['\"]\)", "Step 1: Require the WebSocket library ('ws').")
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
        S9 = State(9, r"require\(['\"](http)['\"]\)|require\(['\"](socket.io)['\"]\)",
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
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js .ts .html",
                              "HTTP Server - side based on XMLHttpRequest in JavaScript")
        S13 = State(13, "new XMLHttpRequest()", "Step 1: Create a new XMLHttpRequest object to initiate the request.")
        S14 = State(14, "open",
                    "Step 2: Configure the request with the `open()` method, defining the request type (GET, POST) and the URL.")
        S15 = State(15, "setRequestHeader|responseType",
                    "Step 3: Set the request headers using `setRequestHeader()` for specific content types.")
        S16 = State(16, "onreadystatechange|onload|onerror",
                    "Step 4: Set up response callback to handle asynchronous events")
        S17 = State(17, "send|sendAsBinary", "Step 5: Send the request to the server using the `send()` or `sendAsBinary()` method.")

        # State transitions for the FSM
        S13.AddNext(S14)
        S14.AddNext(S15)
        S15.AddNext(S16)
        S16.AddNext(S17)
        # Add state to the classifier
        Class.AddState(S13)
        self.IRIClfList.append(Class)

        # FSM 6: HTTP Client-side based on Axios
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js .ts .html", "HTTP Client-side based on Axios")
        S18 = State(18, r"require\(['\"](axios)['\"]\)",
                    "Step 1: Import the axios library to enable HTTP client functionality")
        S19 = State(19, "get|post|put|delete",
                    "Step 2: Choose and initiate the HTTP method for the request (GET, POST, etc.)")
        S20 = State(20, "URL|headers|params|data",
                    "Step 3: Configure the request with URL, headers, query parameters, and payload")
        S21 = State(21, "catch", "Step 4: Handle errors using catch block or error callback")
        # State transitions for the FSM
        S18.AddNext(S19)
        S19.AddNext(S20)
        S20.AddNext(S21)
        # Add state to the classifier
        Class.AddState(S18)
        self.IRIClfList.append(Class)

        # FSM 7: HTTP Client - side based on request in javascript
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js .ts .html",
                              "HTTP Client - side based on request in javascript")
        S22 = State(22, r"require\(['\"](request)['\"]\)", "Step 1: Import the request module")
        S23 = State(23, "request|get|post|put|delete", "Step 2: Call request method such as request.get/post/etc")
        S24 = State(24, "url|method|headers|body|json|form|formData",
                    "Step 3: Configure HTTP options like URL, headers, and data")
        S25 = State(25, "callback", "Step 4: Handle the HTTP response via callback")
        # State transitions for the FSM
        S22.AddNext(S23)
        S23.AddNext(S24)
        S24.AddNext(S25)
        # Add state to the classifier
        Class.AddState(S22)
        self.IRIClfList.append(Class)

        # FSM 8: HTTP based on express in javascript
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js .ts .html", "HTTP based on express in javascript")
        S26 = State(26, r"require\(['\"](express)['\"]\)", "Step 1: Import the Express framework module.")
        S27 = State(27, "express()", "Step 2: Create an Express application instance.")
        S28 = State(28, "use", "Step 3: Configure middleware for request processing.")
        S29 = State(29, "get|post|put|delete", "Step 4: Define route handlers for HTTP methods.")
        S30 = State(30, "listen", "Step 5: Start the server and listen on a specified port.")
        # State transitions for the FSM
        S26.AddNext(S27)
        S27.AddNext(S28)
        S28.AddNext(S29)
        S29.AddNext(S30)
        # Add state to the classifier
        Class.AddState(S26)
        self.IRIClfList.append(Class)

        # FSM 9: TCP Server - side based on node.js net
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js .ts .html", "TCP Server - side based on node.js net")
        S31 = State(31, r"require\(['\"](net)['\"]\)", "Step 1: Import the built - in 'net' module.")
        S32 = State(32, "createServer()", "Step 2: Create a TCP server instance.")
        S33 = State(33, "data|end|error",
                    "Step 3: Handle server lifecycle events and client connections.")
        S34 = State(34, "listen", "Step 4: Start listening on a specific port.")

        # State transitions for the FSM
        S31.AddNext(S32)
        S32.AddNext(S33)
        S33.AddNext(S34)
        # Add state to the classifier
        Class.AddState(S31)
        self.IRIClfList.append(Class)

        # FSM 10: UDP based on node.js dgram
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js .ts .html", "UDP based on node.js dgram")
        S35 = State(35, r"require\(['\"](dgram)['\"]\)", "Step 1: Import the built - in 'dgram' module.")
        S36 = State(36, r"createSocket\(['\"](udp4)['\"]\)|createSocket\(['\"](udp6)['\"]\)",
                    "Step 2: Create a UDP socket for IPv4 or IPv6.")
        S37 = State(37, "message|listening|error",
                    "Step 3: Handle socket events such as incoming messages, binding status, and errors.")
        S38 = State(38, "bind", "Step 4: Bind the socket to a local port and optionally a specific address.")
        # State transitions for the FSM
        S35.AddNext(S36)
        S36.AddNext(S37)
        S37.AddNext(S38)
        # Add state to the classifier
        Class.AddState(S35)
        self.IRIClfList.append(Class)

        # FSM 11: Pipe Client-side based on fs+http in JavaScript
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js .ts .html",
                              "Pipe Client-side based on fs+http in JavaScript")
        S39 = State(39, r"require\(['\"](fs)['\"]\)|require\(['\"](http)['\"]\)",
                    "Step 1: Import the necessary modules (`fs` for file operations and `http` for making HTTP requests).")
        S40 = State(40, "createReadStream",
                    "Step 2: Create a readable stream from a file using `fs.createReadStream()`.")
        S41 = State(41, "request", "Step 3: Create an HTTP request using `http.request()` to send the file data.")
        S42 = State(42, "pipe",
                    "Step 4: Use `pipe()` to send the file stream data to the HTTP request's writable stream.")
        # State transitions for the FSM
        S39.AddNext(S40)
        S40.AddNext(S41)
        S41.AddNext(S42)
        # Add state to the classifier
        Class.AddState(S39)
        self.IRIClfList.append(Class)

        # FSM 12: Pipe Server-side based on fs+http in JavaScript
        Class = ApiClassifier("JavaScript*", LANG_API_IRI, ".js .ts .html",
                              "Pipe Server-side based on fs+http in JavaScript")
        S43 = State(43, r"require\(['\"](fs)['\"]\)|require\(['\"](http)['\"]\)",
                    "Step 1: Import the necessary modules (`fs` for file system operations and `http` for creating the server).")
        S44 = State(44, "createServer",
                    "Step 2: Create an HTTP server using `http.createServer()` to handle incoming requests.")
        S45 = State(45, "pipe",
                    "Step 3: Use `pipe()` to pass the request data to a writable stream, such as a file output stream.")
        # State transitions for the FSM
        S43.AddNext(S44)
        S44.AddNext(S45)
        # Add state to the classifier
        Class.AddState(S43)
        self.IRIClfList.append(Class)

        # ###########################################################
        # Class: Go*
        # ###########################################################
        # Go语言面向多编程语言交互的进程间通信方法包括：
        # 套接字技术：TCP/UDP/Websocket
        # 内存共享技术:
        # 消息队列：Redis/Kafka/RabbitMQ/RocketMQ
        # gRPC
        # 文件交互:Json/CSV/XML
        # FSM 1: Simple HTTP GET client using net/http
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go", "Simple HTTP GET client using net/http")
        S0 = State(0, "io/ioutil|net/http", "Step 1: Import necessary packages like net/http and ioutil")
        S1 = State(1, "http.Get|http.Post|http.PostForm|http.Head|http.Delete",
                   "Step 2: Initiate a simple HTTP request (e.g., http.Get)")
        S2 = State(2, "defer .*Body.Close()", "Step 3: Defer closing of response body to prevent resource leaks")
        S3 = State(3, "ioutil.ReadAll", "Step 4: Read the response body using ioutil.ReadAll")
        # State transitions for the FSM
        S0.AddNext(S1)
        S1.AddNext(S2)
        S2.AddNext(S3)
        # Add state to the classifier
        Class.AddState(S0)
        self.IRIClfList.append(Class)

        # FSM 2: Advanced HTTP client with custom http.Client and request headers
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go",
                              "Advanced HTTP client with custom http.Client and request headers")
        S4 = State(4, "io/ioutil|net/http",
                   "Step 1: Import packages like net/http and ioutil for client and I/O operations")
        S5 = State(5, "&http.Client", "Step 2: Create a custom http.Client for request execution")
        S6 = State(6, "NewRequest", "Step 3: Create an HTTP request using http.NewRequest")
        S7 = State(7, "Header.Add", "Step 4 (optional): Add headers to the HTTP request")
        S8 = State(8, ".*Do", "Step 5: Execute the HTTP request using client.Do(req)")
        S9 = State(9, "defer .*Body.Close()", "Step 6: Defer the closing of the response body")
        S10 = State(10, "ioutil.ReadAll", "Step 7: Read the response body")
        # State transitions for the FSM
        S4.AddNext(S5)
        S5.AddNext(S6)
        S6.AddNext(S7)
        S7.AddNext(S8)
        S8.AddNext(S9)
        S9.AddNext(S10)
        S6.AddNext(S8)
        # Add state to the classifier
        Class.AddState(S4)
        self.IRIClfList.append(Class)

        # FSM 3: Basic HTTP server using net/http with HandleFunc and ListenAndServe
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go",
                              "Basic HTTP server using net/http with HandleFunc and ListenAndServe")
        S11 = State(11, "net/http", "Step 1: Import the net/http package to build an HTTP server")
        S12 = State(12, "http.Request|http.ResponseWriter",
                    "Step 2: Define handler functions with http.ResponseWriter and *http.Request parameters")
        S13 = State(13, "http.HandleFunc|http.Handle",
                    "Step 3: Register routes and their handler functions using HandleFunc or Handle")
        S14 = State(14, "http.ListenAndServe",
                    "Step 4: Start the HTTP server by calling ListenAndServe on a specified port")
        # State transitions for the FSM
        S11.AddNext(S12)
        S12.AddNext(S13)
        S13.AddNext(S14)
        # Add state to the classifier
        Class.AddState(S11)
        self.IRIClfList.append(Class)

        # FSM 4: Advanced HTTP server with http.Server and ServeMux for custom configuration
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go", "Advanced HTTP server with http.Server and ServeMux for custom configuration")
        S15 = State(15, "net/http", "Step 1: Import net/http for server and routing logic")
        S16 = State(16, "&http.Server", "Step 2: Create a custom http.Server instance for configuration")
        S17 = State(17, "http.NewServeMux()", "Step 3: Use ServeMux to create a custom multiplexer")
        S18 = State(18, "HandleFunc", "Step 4: Register handlers to ServeMux")
        S19 = State(19, "ListenAndServe", "Step 5: Launch the server with ListenAndServe")
        # State transitions for the FSM
        S15.AddNext(S16)
        S16.AddNext(S17)
        S17.AddNext(S18)
        S18.AddNext(S19)
        # Add state to the classifier
        Class.AddState(S15)
        self.IRIClfList.append(Class)

        # FSM 5: Gin-based HTTP Server in Go
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go", "Gin-based HTTP Server in Go")
        S20 = State(20, "github.com/gin-gonic/gin", "Step 1: Import the Gin package")
        S21 = State(21, "gin.Default()",
                    "Step 2: Initialize the default Gin engine with Logger and Recovery middleware")
        S22 = State(22, "GET|POST|PUT|DELETE",
                    "Step 3: Register HTTP route handlers for different methods (GET, POST, etc.)")
        S23 = State(23, "String|JSON|XML|HTML|PostForm|Param|Query",
                    "Step 4: Handle request data and send responses (e.g., JSON, HTML, form data)")
        S24 = State(24, "Run", "Step 5: Start the Gin server with the specified port")
        # State transitions for the FSM
        S20.AddNext(S21)
        S21.AddNext(S22)
        S22.AddNext(S23)
        S23.AddNext(S24)
        # Add state to the classifier
        Class.AddState(S20)
        self.IRIClfList.append(Class)

        # FSM 6: Echo-based HTTP Server in Go
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go", "Echo-based HTTP Server in Go")
        S25 = State(25, "net/http|github.com/labstack/echo/v4", "Step 1: Import Echo and net/http packages")
        S26 = State(26, "echo.New()", "Step 2: Create a new Echo instance")
        S27 = State(27, "GET|POST|PUT|DELETE", "Step 3: Register route handlers for HTTP methods")
        S28 = State(28, "Start", "Step 4: Start the HTTP server using e.Start()")
        # State transitions for the FSM
        S25.AddNext(S26)
        S26.AddNext(S27)
        S27.AddNext(S28)
        # Add state to the classifier
        Class.AddState(S25)
        self.IRIClfList.append(Class)

        # FSM 7: Fiber-based HTTP Server in Go
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go", "Fiber-based HTTP Server in Go")
        S29 = State(29, "github.com/gofiber/fiber/v2", "Step 1: Import the Fiber framework package")
        S30 = State(30, "fiber.New()", "Step 2: Initialize the Fiber app instance")
        S31 = State(31, "Get|Post|Put|Delete", "Step 3: Define routes and register HTTP handlers")
        S32 = State(32, "Listen", "Step 4: Start the server by calling app.Listen")
        # State transitions
        S29.AddNext(S30)
        S30.AddNext(S31)
        S31.AddNext(S32)
        # Register classifier
        Class.AddState(S29)
        self.IRIClfList.append(Class)

        # FSM 8: Chi-based HTTP Server in Go
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go", "Chi-based HTTP Server in Go")
        S33 = State(33, "github.com/go-chi/chi/v5", "Step 1: Import the Chi router package")
        S34 = State(34, "chi.NewRouter()", "Step 2: Create a new router instance")
        S35 = State(35, "Get|Post|Put|Delete", "Step 3: Define routes and attach handler functions")
        S36 = State(36, "ListenAndServe", "Step 4: Start the HTTP server with the router")
        # State transitions
        S33.AddNext(S34)
        S34.AddNext(S35)
        S35.AddNext(S36)
        # Register classifier
        Class.AddState(S33)
        self.IRIClfList.append(Class)

        # FSM 9: Net-based TCP Server in Go
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go", "Net-based TCP Server in Go")
        S37 = State(37, "net", "Step 1: Import Go's built-in net package for TCP networking")
        S38 = State(38, "net.Listen", "Step 2: Create a TCP listener on a specified port")
        S39 = State(39, "defer.*Close()", "Step 3: Ensure the listener is closed when done")
        S40 = State(40, "Accept()", "Step 4: Accept incoming client connections in a loop")
        S41 = State(41, "Read|Write", "Step 5: Communicate with the client via conn.Read/conn.Write")
        # State transitions
        S37.AddNext(S38)
        S38.AddNext(S39)
        S39.AddNext(S40)
        S40.AddNext(S41)
        # Register classifier
        Class.AddState(S37)
        self.IRIClfList.append(Class)

        # FSM 10: Net-based TCP Client in Go
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go", "Net-based TCP Client in Go")
        S42 = State(42, "net", "Step 1: Import Go's built-in net package for TCP networking")
        S43 = State(43, "net.Dial", "Step 2: Establish a TCP connection to the server")
        S44 = State(44, "defer.*Close()", "Step 3: Ensure the connection is closed when finished")
        S45 = State(45, "Read|Write", "Step 4: Send or receive data over the TCP connection")
        # State transitions
        S42.AddNext(S43)
        S43.AddNext(S44)
        S44.AddNext(S45)
        # Register classifier
        Class.AddState(S42)
        self.IRIClfList.append(Class)

        # FSM 11: net-based UDP Server in Go
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go", "net-based UDP Server in Go")
        S46 = State(46, "net", "Step 1: Import the necessary net package")
        S47 = State(47, "net.ListenPacket", "Step 2: Listen for incoming UDP packets on a specific port")
        S48 = State(48, "defer .*Close()", "Step 3: Ensure that the connection is properly closed after use")
        S49 = State(49, "ReadFrom|Read", "Step 4: Read incoming UDP data from clients")
        S50 = State(50, "WriteTo|Write", "Step 5: Send response data back to the client")
        # State transitions
        S46.AddNext(S47)
        S47.AddNext(S48)
        S48.AddNext(S49)
        S49.AddNext(S50)
        # Register classifier
        Class.AddState(S46)
        self.IRIClfList.append(Class)

        # FSM 12: net-based UDP Server with listenUDP in Go
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go", "net-based UDP Server with listenUDP in Go")
        S51 = State(51, "net", "Step 1: Import the net package for networking functionalities")
        S52 = State(52, "net.ListenUDP", "Step 2: Use net.ListenUDP to bind the server to a specific UDP port")
        S53 = State(53, "defer .*Close()",
                    "Step 3: Defer Close to clean up resources when the server exits")
        S54 = State(54, "ReadFromUDP|WriteToUDP", "Step 4: Read incoming UDP data from clients using ReadFromUDP or Send response data back to clients using WriteToUDP")
        # State transitions
        S51.AddNext(S52)
        S52.AddNext(S53)
        S53.AddNext(S54)
        # Register classifier
        Class.AddState(S51)
        self.IRIClfList.append(Class)

        # FSM 13: net - based UDP Client with DialUDP in Go
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go", "net-based UDP Client with DialUDP in Go")
        S55 = State(55, "net", "Step 1: Import the net package for networking functionalities")
        S56 = State(56, "net.DialUDP", "Step 2: Use net.DialUDP to establish a UDP connection to the server")
        S57 = State(57, "defer .*Close()", "Step 3: Defer Close to release the connection when done")
        S58 = State(58, "Write|ReadFromUDP", "Step 4: Send data to the server using Write or Read the server's response using ReadFromUDP or Read")
        # State transitions
        S55.AddNext(S56)
        S56.AddNext(S57)
        S57.AddNext(S58)
        # Register classifier
        Class.AddState(S55)
        self.IRIClfList.append(Class)

        # FSM 14: gorilla-based websocket server in Go
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go", "gorilla-based websocket server in Go")
        S59 = State(59, "net/http|github.com/gorilla/websocket",
                    "Step 1: Import necessary libraries for HTTP and WebSocket")
        S60 = State(60, "websocket.Upgrader", "Step 2: Create a WebSocket upgrader to handle WebSocket handshake")
        S61 = State(61, "Upgrade", "Step 3: Upgrade the HTTP connection to WebSocket connection using the upgrader")
        S62 = State(62, "defer.*Close()", "Step 4: Close the WebSocket connection after processing")
        S63 = State(63, "ReadMessage|WriteMessage",
                    "Step 5: Read messages from and write messages to the WebSocket connection")
        # State transitions
        S59.AddNext(S60)
        S60.AddNext(S61)
        S61.AddNext(S62)
        S62.AddNext(S63)
        # Register classifier
        Class.AddState(S59)
        self.IRIClfList.append(Class)

        # FSM 15: gorilla-based websocket client in Go
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go", "gorilla-based websocket client in Go")
        S64 = State(64, "github.com/gorilla/websocket", "Step 1: Import the necessary Gorilla WebSocket library")
        S65 = State(65, "websocket.DefaultDialer.Dial",
                    "Step 2: Use Dial function to establish a WebSocket connection with the server")
        S66 = State(66, "defer.*Close()", "Step 3: Ensure the WebSocket connection is properly closed after usage")
        S67 = State(67, "ReadMessage|WriteMessage",
                    "Step 4: Read messages from or send messages to the WebSocket server")
        # State transitions
        S64.AddNext(S65)
        S65.AddNext(S66)
        S66.AddNext(S67)
        # Register classifier
        Class.AddState(S64)
        self.IRIClfList.append(Class)

        # FSM 16: nhooyr.io-based websocket server in Go
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go", "nhooyr.io-based websocket server in Go")
        S68 = State(68, "net/http|nhooyr.io/websocket", "Step 1: Import required packages")
        S69 = State(69, "websocket.Accept", "Step 2: Upgrade HTTP connection to WebSocket")
        S70 = State(70, "defer.*Close", "Step 3: Defer connection closure")
        S71 = State(71, "Read|Write", "Step 4: Handle message reading and writing")
        # State transitions
        S68.AddNext(S69)
        S69.AddNext(S70)
        S70.AddNext(S71)
        # Register classifier
        Class.AddState(S68)
        self.IRIClfList.append(Class)

        # FSM 17: nhooyr.io-based websocket client in Go
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go", "nhooyr.io-based websocket client in Go")
        S72 = State(72, "net/http|nhooyr.io/websocket", "Step 1: Import required packages")
        S73 = State(73, "websocket.Dial", "Step 2: Establish WebSocket connection")
        S74 = State(74, "defer.*Close", "Step 3: Defer connection closure")
        S75 = State(75, "Write|Read", "Step 4: Send and receive WebSocket messages")
        # State transitions
        S72.AddNext(S73)
        S73.AddNext(S74)
        S74.AddNext(S75)
        # Register classifier
        Class.AddState(S72)
        self.IRIClfList.append(Class)

        # FSM 18: os.pipe-based pipe in Go
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go", "os.pipe-based pipe in Go")
        S76 = State(76, "os", "Step 1: Import the 'os' package to support pipe creation and file descriptor handling.")
        S77 = State(77, "os.Pipe()",
                    "Step 2: Use os.Pipe() to create a unidirectional in-memory pipe with reader and writer.")
        S78 = State(78, "defer.*Close",
                    "Step 3: Defer the Close() calls on both reader and writer to release resources properly.")
        S79 = State(79, "Write|Read",
                    "Step 4: Use the writer to send data and the reader to receive data through the pipe.")
        # State transitions
        S76.AddNext(S77)
        S77.AddNext(S78)
        S78.AddNext(S79)
        # Register classifier
        Class.AddState(S76)
        self.IRIClfList.append(Class)

        # FSM 19: Official-based gRPC server in Go
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go", "Official-based gRPC server in Go")
        S80 = State(80, "google.golang.org/grpc", "Step 1: Import gRPC package")
        S81 = State(81, "net.Listen", "Step 2: Set up a network listener")
        S82 = State(82, "grpc.NewServer()", "Step 3: Create a new gRPC server instance")
        S83 = State(83, "Serve", "Step 4: Start the server to listen for incoming requests")
        # State transitions
        S80.AddNext(S81)
        S81.AddNext(S82)
        S82.AddNext(S83)
        # Register classifier
        Class.AddState(S80)
        self.IRIClfList.append(Class)

        # FSM 20: Official-based gRPC client in Go
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go", "Official-based gRPC client in Go")
        S84 = State(84, "google.golang.org/grpc", "Step 1: Import gRPC package")
        S85 = State(85, "grpc.Dial", "Step 2: Establish a connection with the gRPC server")
        S86 = State(86, "defer.*Close", "Step 3: Close the connection when done")
        # State transitions
        S84.AddNext(S85)
        S85.AddNext(S86)
        # Register classifier
        Class.AddState(S84)
        self.IRIClfList.append(Class)

        # FSM 21: Simple Rabbitmq producer in go
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go", "Simple Rabbitmq producer in go")
        S87 = State(87, "github.com/streadway/amqp", "Step 1: Import the streadway/amqp package")
        S88 = State(88, "amqp.Dial", "Step 2: Establish a connection to the RabbitMQ server")
        S89 = State(89, "Channel()", "Step 3: Open a channel from the connection")
        S90 = State(90, "ExchangeDeclare", "Step 4: Declare an exchange (optional depending on use case)")
        S91 = State(91, "QueueDeclare", "Step 5: Declare a queue to publish messages to")
        S92 = State(92, "channel.Publish", "Step 6: Publish a message to the declared queue or exchange")
        # State transitions
        S87.AddNext(S88)
        S88.AddNext(S89)
        S89.AddNext(S90)
        S90.AddNext(S91)
        S91.AddNext(S92)
        S89.AddNext(S91)
        # Register classifier
        Class.AddState(S87)
        self.IRIClfList.append(Class)

        # FSM 22: Simple Rabbitmq consumer in go
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go", "Simple Rabbitmq consumer in go")
        S93 = State(93, "github.com/streadway/amqp", "Step 1: Import the streadway/amqp package")
        S94 = State(94, "amqp.Dial", "Step 2: Connect to the RabbitMQ server")
        S95 = State(95, "Channel()", "Step 3: Create a channel for communication")
        S96 = State(96, "ExchangeDeclare", "Step 4: Declare the exchange to bind the queue (if needed)")
        S97 = State(97, "QueueDeclare", "Step 5: Declare the queue from which to consume messages")
        S98 = State(98, "QueueBind", "Step 6: Bind the queue to the exchange with a routing key")
        S99 = State(99, "channel.Consume", "Step 7: Start consuming messages from the queue")
        # State transitions
        S93.AddNext(S94)
        S94.AddNext(S95)
        S95.AddNext(S96)
        S96.AddNext(S97)
        S97.AddNext(S98)
        S98.AddNext(S99)
        # Register classifier
        Class.AddState(S93)
        self.IRIClfList.append(Class)

        # FSM 23: Kafka producer in Go
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go", "Kafka Sync producer in Go")
        S100 = State(100, "github.com/Shopify/sarama", "Step 1: Import the sarama package")
        S101 = State(101, "sarama.NewConfig()", "Step 2: Create and configure a new sarama.Config instance")
        S102 = State(102, "sarama.NewSyncProducer", "Step 3: Instantiate a synchronous Kafka producer")
        S103 = State(103, "defer.*Close()", "Step 4: Ensure producer resources are closed with defer")
        S104 = State(104, "&sarama.ProducerMessage",
                     "Step 5: Prepare a message to be sent using sarama.ProducerMessage")
        S105 = State(105, "SendMessage", "Step 6: Send the message using the producer's SendMessage method")
        # State transitions
        S100.AddNext(S101)
        S101.AddNext(S102)
        S102.AddNext(S103)
        S103.AddNext(S104)
        S104.AddNext(S105)
        # Register classifier
        Class.AddState(S100)
        self.IRIClfList.append(Class)

        # FSM 24: Kafka consumer in Go
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go", "Kafka consumer in Go")
        S106 = State(106, "github.com/Shopify/sarama", "Step 1: Import the sarama package")
        S107 = State(107, "sarama.NewConfig()", "Step 2: Create a new Kafka consumer using sarama.NewConsumer")
        S108 = State(108, "sarama.NewConsumerGroup", "Step 3: Retrieve the available partitions for a given topic")
        S109 = State(109, "defer.*Close()", "Step 4: Ensure producer resources are closed with defer")
        S110 = State(110, "Consume", "Step 4: Start consuming from a specific partition")
        # State transitions
        S106.AddNext(S107)
        S107.AddNext(S108)
        S108.AddNext(S109)
        S108.AddNext(S110)
        Class.AddState(S106)
        self.IRIClfList.append(Class)

        # FSM 25: Kafka producer in Go
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go", "Kafka Async producer in Go")
        S111 = State(111, "github.com/Shopify/sarama", "Step 1: Import the sarama package")
        S112 = State(112, "sarama.NewConfig()", "Step 2: Create and configure a new sarama.Config instance")
        S113 = State(113, "sarama.NewAsyncProducer", "Step 3: Instantiate an asynchronous Kafka producer")
        S114 = State(114, "defer.*Close()", "Step 4: Ensure producer resources are closed with defer")
        S115 = State(115, "&sarama.ProducerMessage",
                     "Step 5: Prepare a message to be sent using sarama.ProducerMessage")
        S116 = State(116, "Input()", "Step 6: Collect or read user input before sending the message")
        # State transitions
        S111.AddNext(S112)
        S112.AddNext(S113)
        S113.AddNext(S114)
        S114.AddNext(S115)
        S115.AddNext(S116)
        # Register classifier
        Class.AddState(S111)
        self.IRIClfList.append(Class)

        # FSM 26: Redis in Go
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go", "Redis in Go")
        S117 = State(117, "github.com/garyburd/redigo/redis",
                     "Step 1: Import the redigo/redis package for Redis support")
        S118 = State(118, "redis.Dial", "Step 2: Establish a connection to the Redis server using redis.Dial")
        S119 = State(119, "defer.*Close()", "Step 3: Use defer to ensure the Redis connection is properly closed")
        S120 = State(120, "Set|Get|lpop|lpush|HSet|HGet",
                     "Step 4: Execute Redis commands such as Set, Get, lpop, lpush, HSet, and HGet")
        S117.AddNext(S118)
        S118.AddNext(S119)
        S119.AddNext(S120)
        Class.AddState(S117)
        self.IRIClfList.append(Class)

        # FSM 27: RocketMQ producer in Go
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go", "RocketMQ producer in Go")
        S121 = State(121, "github.com/apache/rocketmq-client-go/v2", "Step 1: Import the RocketMQ Go client package")
        S122 = State(122, "rocketmq.NewProducer", "Step 2: Create a new producer with specified configuration options")
        S123 = State(123, "Start", "Step 3: Start the producer before sending messages to brokers")
        S124 = State(124, "SendSync|SendAsync|SendOneWay", "Step 4: Send messages using Sync, Async, or OneWay modes")
        S121.AddNext(S122)
        S122.AddNext(S123)
        S123.AddNext(S124)
        Class.AddState(S121)
        self.IRIClfList.append(Class)

        # FSM 28: RocketMQ consumer in Go"
        Class = ApiClassifier("Go*", LANG_API_IRI, ".go", "RocketMQ consumer in Go")
        S125 = State(125, "github.com/apache/rocketmq-client-go/v2", "Step 1: Import the RocketMQ Go client package")
        S126 = State(126, "rocketmq.NewPushConsumer", "Step 2: Create a new push consumer and set relevant options")
        S127 = State(127, "Subscribe", "Step 3: Subscribe to one or more topics and define a message handler callback")
        S128 = State(128, "Start", "Step 4: Start the consumer to receive and process messages")
        S125.AddNext(S126)
        S126.AddNext(S127)
        S127.AddNext(S128)
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
        # FSM 1: websocket server using stream_socket_server in php
        Class = ApiClassifier("PHP*", LANG_API_IRI, ".php", "Websocket server using stream_socket_server in PHP")
        S0 = State(0, "stream_socket_server", "Step 1: Create a TCP server socket and bind it to an address/port")
        S1 = State(1, "stream_socket_accept", "Step 2: Accept an incoming client connection and validate handshake")
        S2 = State(2, "fread|fwrite", "Step 3: Read client request, perform WebSocket handshake and send response")
        S3 = State(3, "fclose", "Step 4: Close the client connection after communication ends")
        S0.AddNext(S1)
        S1.AddNext(S2)
        S2.AddNext(S3)
        Class.AddState(S0)
        self.IRIClfList.append(Class)

        # FSM 2: websocket client using stream_socket_client in php
        Class = ApiClassifier("PHP*", LANG_API_IRI, ".php", "Websocket client using stream_socket_client in PHP")
        S4 = State(4, "stream_socket_client", "Step 1: Connect to a WebSocket server via TCP and initiate a handshake")
        S5 = State(5, "GET|POST|PUT|DELETE", "Step 2: Send an HTTP request with WebSocket headers to the server")
        S6 = State(6, "fgets", "Step 3: Receive response data from server and process WebSocket handshake")
        S7 = State(7, "fclose", "Step 4: Close the connection after receiving server response")
        S4.AddNext(S5)
        S5.AddNext(S6)
        S6.AddNext(S7)
        Class.AddState(S4)
        self.IRIClfList.append(Class)

        # FSM 3: HTTP client using fsockopen in php
        Class = ApiClassifier("PHP*", LANG_API_IRI, ".php", "HTTP client using fsockopen in PHP")
        S8 = State(8, "fsockopen", "Step 1: Open a TCP connection to the HTTP server and establish the socket")
        S9 = State(9, "GET|POST|PUT|DELETE", "Step 2: Send an HTTP request (e.g., GET/POST) to the server with headers")
        S10 = State(10, "fgets",
                    "Step 3: Read the HTTP response from the server line-by-line, parsing headers and body")
        S11 = State(11, "fclose", "Step 4: Close the socket connection after reading the response")
        S8.AddNext(S9)
        S9.AddNext(S10)
        S10.AddNext(S11)
        Class.AddState(S8)
        self.IRIClfList.append(Class)

        # FSM 4: HTTP client using cURL in PHP
        Class = ApiClassifier("PHP*", LANG_API_IRI, ".php", "HTTP client using cURL in PHP")
        S12 = State(12, "curl_init()", "Step 1: Initialize a new cURL session with curl_init().")
        S13 = State(13, "curl_setopt()",
                    "Step 2: Set options for the cURL session such as URL, method, headers, and payload.")
        S14 = State(14, "curl_exec()", "Step 3: Execute the cURL session and capture the response.")
        S15 = State(15, "curl_errno()|curl_error()", "Step 4: Check for errors in the cURL session.")
        S16 = State(16, "curl_close()", "Step 5: Close the cURL session to free up resources.")
        # Define state transitions
        S12.AddNext(S13)
        S13.AddNext(S14)
        S14.AddNext(S15)
        S15.AddNext(S16)
        S14.AddNext(S16)
        Class.AddState(S12)
        self.IRIClfList.append(Class)

        # FSM 5: HTTP client using Guzzle in PHP
        Class = ApiClassifier("PHP*", LANG_API_IRI, ".php", "HTTP client using Guzzle in PHP")
        S17 = State(17, r"use GuzzleHttp\\Client", "Step 1: Import Guzzle HTTP client library")
        S18 = State(18, "new Client()", "Step 2: Initialize a new Client instance")
        S19 = State(19, "request", "Step 3: Send HTTP request using the Client")
        S20 = State(20, "getBody|getContents|getJson", "Step 4: Retrieve the response body content")
        # Define state transitions
        S17.AddNext(S18)
        S18.AddNext(S19)
        S19.AddNext(S20)
        Class.AddState(S17)
        self.IRIClfList.append(Class)

        # FSM 6: HTTP client using Symfony in PHP
        Class = ApiClassifier("PHP*", LANG_API_IRI, ".php", "HTTP client using Symfony in PHP")
        S21 = State(21, r"use Symfony\\Component\\HttpClient\\HttpClient",
                    "Step 1: Import Symfony HTTP client library to use HTTP client features")
        S22 = State(22, "create",
                    "Step 2: Create a new HttpClient instance to initialize the client for sending requests")
        S23 = State(23, "request",
                    "Step 3: Send an HTTP request (GET/POST) using the HttpClient instance, with headers and body data if necessary")
        S24 = State(24, "getBody|getContents|getJson",
                    "Step 4: Extract response content (body or JSON) from the HTTP request's response object")
        S21.AddNext(S22)
        S22.AddNext(S23)
        S23.AddNext(S24)
        Class.AddState(S21)
        self.IRIClfList.append(Class)

        # FSM 7: http_build_query php
        Class = ApiClassifier("PHP*", LANG_API_IRI, ".php", "http_build_query php")
        S25 = State(25, "http_build_query",
                    "Step 1: Use `http_build_query` to encode the data array into a query string suitable for HTTP requests.")
        S26 = State(26, "POST|GET|DELETE|PUT|HEAD|OPTIONS|PATCH",
                    "Step 2: Choose the HTTP method (e.g., POST, GET) to specify how the data will be sent to the server.")
        S27 = State(27, "stream_context_create",
                    "Step 3: Create a stream context with appropriate options such as HTTP headers and method for the request.")
        S28 = State(28, "file_get_contents",
                    "Step 4: Use `file_get_contents` to send the HTTP request and retrieve the server's response based on the context created.")
        # Define state transitions
        S25.AddNext(S26)
        S26.AddNext(S27)
        S27.AddNext(S28)
        Class.AddState(S25)
        self.IRIClfList.append(Class)

        # FSM 8: TCP server based on socket_* in php
        Class = ApiClassifier("PHP*", LANG_API_IRI, ".php", "TCP server based on socket_* in PHP")
        S29 = State(29, "socket_create", "Step 1: Create a TCP socket using AF_INET and SOCK_STREAM")
        S30 = State(30, "socket_bind", "Step 2: Bind the socket to a local IP address and port")
        S31 = State(31, "socket_listen", "Step 3: Start listening for incoming client connections")
        S32 = State(32, "socket_accept", "Step 4: Accept an incoming client connection")
        S33 = State(33, "socket_read|socket_write", "Step 5: Read data from and write data to the connected client")
        S34 = State(34, "socket_close", "Step 6: Close both client and server sockets to free resources")
        S29.AddNext(S30)
        S30.AddNext(S31)
        S31.AddNext(S32)
        S32.AddNext(S33)
        S33.AddNext(S34)
        Class.AddState(S29)
        self.IRIClfList.append(Class)

        # FSM 9: TCP client based on socket_* in php
        Class = ApiClassifier("PHP*", LANG_API_IRI, ".php", "TCP client based on socket_* in PHP")
        S35 = State(35, "socket_create", "Step 1: Create a TCP socket using AF_INET and SOCK_STREAM")
        S36 = State(36, "socket_connect", "Step 2: Connect to the server using IP address and port")
        S37 = State(37, "socket_write|socket_read", "Step 3: Send data to and receive response from the server")
        S35.AddNext(S36)
        S36.AddNext(S37)
        Class.AddState(S35)
        self.IRIClfList.append(Class)

        # FSM 10: TCP client implementation using ReactPHP in PHP
        Class = ApiClassifier("PHP*", LANG_API_IRI, ".php", "TCP client implementation using ReactPHP in PHP")
        S38 = State(38, r"create",
                    "Step 1: Create the event loop to manage asynchronous operations and handle events.")
        S39 = State(39, r"new React\\Socket\\Connector",
                    "Step 2: Initialize the TCP connector to establish a connection to the server with specified options.")
        S40 = State(40, "connect",
                    "Step 3: Attempt to connect to the server using the provided IP address and port, handling any connection errors.")
        S41 = State(41, "data|close",
                    "Step 4: Define behavior for receiving data from the server and handling connection closure, including any necessary cleanup.")
        S42 = State(42, "run()",
                    "Step 5: Start the event loop to initiate the connection and manage ongoing communication asynchronously.")
        S38.AddNext(S39)
        S39.AddNext(S40)
        S40.AddNext(S41)
        S41.AddNext(S42)
        Class.AddState(S38)
        self.IRIClfList.append(Class)

        # FSM 11: UDP client based on swoole in php
        Class = ApiClassifier("PHP*", LANG_API_IRI, ".php", "UDP client based on swoole in PHP")
        S43 = State(43, r"use Swoole\\Coroutine\\Client",
                    "Step 1: Import the Swoole Coroutine Client class to enable asynchronous UDP communication.")
        S44 = State(44, "new Client",
                    "Step 2: Create a new instance of the `Client` to establish a UDP client that can send and receive messages.")
        S45 = State(45, "connect", "Step 3: Connect to the UDP server by specifying the server's IP address and port.")
        S46 = State(46, "send|recv", "Step 4: Send data to the UDP server and receive responses asynchronously.")
        S47 = State(47, "close", "Step 5: Close the UDP client connection after communication is complete.")
        S43.AddNext(S44)
        S44.AddNext(S45)
        S45.AddNext(S46)
        S46.AddNext(S47)
        Class.AddState(S43)
        self.IRIClfList.append(Class)

        # FSM 12: UDP server based on react in PHP
        Class = ApiClassifier("PHP*", LANG_API_IRI, ".php", "UDP server based on ReactPHP in PHP")
        S48 = State(48, r"create()",
                    "Step 1: Create the event loop to manage asynchronous events and handle incoming UDP packets.")
        S49 = State(49, r"createServer", "Step 2: Create the UDP server to listen for incoming messages from clients.")
        S50 = State(50, "message",
                    "Step 3: Handle incoming messages from clients, process data and send responses if necessary.")
        S51 = State(51, "run",
                    "Step 4: Start the event loop to listen for incoming messages and manage ongoing server operations asynchronously.")
        S48.AddNext(S49)
        S49.AddNext(S50)
        S50.AddNext(S51)
        Class.AddState(S48)
        self.IRIClfList.append(Class)

        # FSM 13: UDP client based on react in PHP
        Class = ApiClassifier("PHP*", LANG_API_IRI, ".php", "UDP client based on ReactPHP in PHP")
        S52 = State(52, r"create()", "Step 1: Create the event loop to manage asynchronous events for the UDP client.")
        S53 = State(53, r"createClient", "Step 2: Create the UDP client to send and receive messages from the server.")
        S54 = State(54, "message",
                    "Step 3: Send messages to the UDP server and handle received messages asynchronously.")
        S55 = State(55, "run",
                    "Step 4: Start the event loop to initiate communication and handle ongoing client operations asynchronously.")
        S52.AddNext(S53)
        S53.AddNext(S54)
        S54.AddNext(S55)
        Class.AddState(S52)
        self.IRIClfList.append(Class)

        # FSM 14: RabbitMQ producer in PHP
        Class = ApiClassifier("PHP*", LANG_API_IRI, ".php", "RabbitMQ producer in PHP")
        S56 = State(56, r"use PhpAmqpLib\\Connection\\AMQPStreamConnection|use PhpAmqpLib\\Message\\AMQPMessage",
                    "Step 1: Import necessary libraries for RabbitMQ connection and message handling")
        S57 = State(57, "new AMQPStreamConnection", "Step 2: Establish a connection to the RabbitMQ server")
        S58 = State(58, "channel()", "Step 3: Create a new channel to send the message")
        S59 = State(59, "queue_declare", "Step 4: Declare the queue where the message will be published")
        S60 = State(60, "new AMQPMessage", "Step 5: Create a new message with the content to be sent")
        S61 = State(61, "basic_publish", "Step 6: Publish the message to the specified queue")
        S62 = State(62, "close()", "Step 7: Close the channel and connection after sending the message")
        S56.AddNext(S57)
        S57.AddNext(S58)
        S58.AddNext(S59)
        S59.AddNext(S60)
        S60.AddNext(S61)
        S61.AddNext(S62)
        Class.AddState(S56)
        self.IRIClfList.append(Class)

        # FSM 15: RabbitMQ consumer in PHP
        Class = ApiClassifier("PHP*", LANG_API_IRI, ".php", "RabbitMQ consumer in PHP")
        S63 = State(63, r"use PhpAmqpLib\\Connection\\AMQPStreamConnection|use PhpAmqpLib\\Message\\AMQPMessage",
                    "Step 1: Import necessary libraries for RabbitMQ connection and message handling")
        S64 = State(64, "new AMQPStreamConnection", "Step 2: Establish a connection to the RabbitMQ server")
        S65 = State(65, "channel()", "Step 3: Create a new channel to consume the message")
        S66 = State(66, "queue_declare", "Step 4: Declare the queue to listen for incoming messages")
        S67 = State(67, "basic_consume", "Step 5: Start consuming messages from the queue")
        S68 = State(68, "close()", "Step 6: Close the channel and connection after processing the messages")
        S63.AddNext(S64)
        S64.AddNext(S65)
        S65.AddNext(S66)
        S66.AddNext(S67)
        S67.AddNext(S68)
        Class.AddState(S63)
        self.IRIClfList.append(Class)

        # FSM 16: Redis in PHP
        Class = ApiClassifier("PHP*", LANG_API_IRI, ".php", "Redis in PHP")
        S69 = State(69, "new Redis()", "Step 2: Create a new Redis instance")
        S70 = State(70, "connect", "Step 3: Connect to the Redis server")
        S71 = State(71,
                    "set|mset|setnx|get|mget|del|delete|getset|append|incr|incrby|decr|decrby|setex|lpush|rpush|lInsert|lpushx|rpushx|lpop|rpop|lrem|ltrim|lset|lindex|lrange|hset|hget|hget|hmget|hgetall|"
                    "hkeys|hvals|hdel|hexists|hincrby|hlen|sadd|srem|smembers|sismember|spop|srandmember|sinter|sunion|sdiff|zAdd|zrem|zscore|zrange|zrevrange|zrangebyscore|zrevrangebyscore|zrank|zrevrank",
                    "Step 4: Perform Redis operations (e.g., Set, Get, List operations, Hash operations)")
        S72 = State(72, "close()", "Step 5: Close the Redis connection")
        # State transitions
        # S162.AddNext(S163)
        S69.AddNext(S70)
        S70.AddNext(S71)
        S71.AddNext(S72)
        # Register classifier
        Class.AddState(S69)
        self.IRIClfList.append(Class)

        # FSM 17: pipe based on proc_open in PHP
        Class = ApiClassifier("PHP*", LANG_API_IRI, ".php", "pipe based on proc_open in PHP")
        S83 = State(83, "proc_open",
                    "Step 1: Use proc_open to start a subprocess and create pipes for stdin, stdout, and stderr")
        S84 = State(84, "stream_get_contents",
                    "Step 2: Read data from the subprocess's stdout or stderr using stream_get_contents")
        S85 = State(85, "fclose", "Step 3: Close all open pipe streams to avoid resource leaks")
        S86 = State(86, "proc_close", "Step 4: Close the subprocess and retrieve its exit code using proc_close")
        # State transitions
        S83.AddNext(S84)
        S84.AddNext(S85)
        S85.AddNext(S86)
        Class.AddState(S83)
        self.IRIClfList.append(Class)

        ############################################################
        # Class: C++*
        ############################################################
        # FSM 1: Http based on libcurl in C++
        Class = ApiClassifier("C++*", LANG_API_IRI, ".cpp", "Http based on libcurl in C++")
        S0 = State(0, "#include <curl/curl.h>", "Step 1: Include necessary libcurl headers.")
        S1 = State(1, "curl_easy_init", "Step 2: Initialize the libcurl session.")
        S2 = State(2, "curl_easy_setopt", "Step 3: Set the URL, request type, and other options.")
        S3 = State(3, "curl_easy_perform", "Step 4: Perform the HTTP request and receive response.")
        S4 = State(4, "curl_easy_cleanup", "Step 5: Clean up and release libcurl resources.")
        S0.AddNext(S1)
        S1.AddNext(S2)
        S2.AddNext(S3)
        S3.AddNext(S4)
        Class.AddState(S0)
        self.IRIClfList.append(Class)

        # FSM 2: Http based on cpp-httplib in C++
        Class = ApiClassifier("C++*", LANG_API_IRI, ".cpp", "Http based on cpp-httplib in C++")
        S5 = State(5, "#include \"httplib.h\"", "Step 1: Include the necessary cpp-httplib header files.")
        S6 = State(6, "Client", "Step 2: Create an instance of the `httplib::Client` class to handle requests.")
        S7 = State(7, "Get|Post", "Step 3: Send a GET or POST request using the Client object to the desired URL.")
        S8 = State(8, "status", "Step 4: Access the `status` field of the response to check the HTTP status code.")
        S9 = State(9, "body",
                   "Step 5: Access the `body` field of the response to read the content returned by the server.")
        S5.AddNext(S6)
        S6.AddNext(S7)
        S7.AddNext(S8)
        S8.AddNext(S9)
        Class.AddState(S5)
        self.IRIClfList.append(Class)

        # FSM 3: TCP Server based on socket+inet in C++
        Class = ApiClassifier("C++*", LANG_API_IRI, ".cpp", "TCP Server based on socket+inet in C++")
        S10 = State(10, "#include <arpa/inet.h>|#include <sys/socket.h>",
                    "Step 1: Include necessary socket and inet headers for TCP socket programming.")
        S11 = State(11, "SOCK_STREAM",
                    "Step 2: Create a socket using `socket()` function with `SOCK_STREAM` type for TCP communication.")
        S12 = State(12, "bind",
                    "Step 3: Bind the socket to a specific IP address and port using the `bind()` function.")
        S13 = State(13, "listen",
                    "Step 4: Set the socket to listen for incoming connection requests using the `listen()` function.")
        S14 = State(14, "accept",
                    "Step 5: Accept an incoming connection request from a client using the `accept()` function.")
        S15 = State(15, "read|send",
                    "Step 6: Read data from the client using `read()` and send data back using `send()` function.")
        S16 = State(16, "close",
                    "Step 7: Close the socket connection after communication is completed using the `close()` function.")
        S10.AddNext(S11)
        S11.AddNext(S12)
        S12.AddNext(S13)
        S13.AddNext(S14)
        S14.AddNext(S15)
        S15.AddNext(S16)
        Class.AddState(S10)
        self.IRIClfList.append(Class)

        # FSM 4: TCP Client based on socket+inet in C++
        Class = ApiClassifier("C++*", LANG_API_IRI, ".cpp", "TCP Client based on socket+inet in C++")
        S17 = State(17, "#include <arpa/inet.h>|#include <sys/socket.h>",
                    "Step 1: Include necessary socket and inet headers for TCP client programming.")
        S18 = State(18, "SOCK_STREAM",
                    "Step 2: Create a socket using `socket()` function with `SOCK_STREAM` type for TCP communication.")
        S19 = State(19, "connect",
                    "Step 3: Connect the socket to a remote server using `connect()` function with the server's IP address and port.")
        S20 = State(20, "send|read",
                    "Step 4: Send data using `send()` and read data from the server using `read()` function.")
        S21 = State(21, "close",
                    "Step 5: Close the socket connection after communication using the `close()` function.")
        S17.AddNext(S18)
        S18.AddNext(S19)
        S19.AddNext(S20)
        S20.AddNext(S21)
        Class.AddState(S17)
        self.IRIClfList.append(Class)

        # FSM 5: TCP Server based on Boost.Asio in C++
        Class = ApiClassifier("C++*", LANG_API_IRI, ".cpp", "TCP Server based on Boost.Asio in C++")
        S22 = State(22, "#include <boost/asio.hpp>",
                    "Step 1: Include Boost.Asio headers to use asynchronous I/O for TCP server.")
        S23 = State(23, "io_context",
                    "Step 2: Create an `io_context` object which provides the core I/O functionality.")
        S24 = State(24, "acceptor",
                    "Step 3: Create a `tcp::acceptor` object (if needed) to accept incoming TCP connections on a specified endpoint.")
        S25 = State(25, "socket",
                    "Step 4: Create a `tcp::socket` object to handle communication with the client after a connection is accepted.")
        S26 = State(26, "accept", "Step 5: Use `acceptor.accept()` to accept an incoming connection from the client.")
        S27 = State(27, "write|read_some",
                    "Step 6: Write data to the socket using `write()` and read data using `read_some()` to process client messages.")
        S28 = State(28, "shutdown|close",
                    "Step 7: Shutdown the connection and close the socket once communication is complete.")
        S22.AddNext(S23)
        S23.AddNext(S24)
        S24.AddNext(S25)
        S25.AddNext(S26)
        S26.AddNext(S27)
        S27.AddNext(S28)
        S23.AddNext(S25)
        Class.AddState(S22)
        self.IRIClfList.append(Class)

        # FSM 6: TCP Client based on Boost.Asio in C++
        Class = ApiClassifier("C++*", LANG_API_IRI, ".cpp", "TCP Client based on Boost.Asio in C++")
        S29 = State(29, "#include <boost/asio.hpp>",
                    "Step 1: Include Boost.Asio headers to enable asynchronous I/O operations for TCP client.")
        S30 = State(30, "io_context",
                    "Step 2: Create an `io_context` object that provides I/O services for handling asynchronous operations.")
        S31 = State(31, "socket", "Step 3: Create a `tcp::socket` object to establish a connection to the server.")
        S32 = State(32, "resolver",
                    "Step 4: Create a `tcp::resolver` object to resolve the server's hostname and port to an endpoint.")
        S33 = State(33, "connect",
                    "Step 5: Use the `resolver.resolve()` function to get a list of endpoints and `connect()` the socket to the server.")
        S34 = State(34, "write|read_some",
                    "Step 6: Write data to the server using `write()` and read data using `read_some()` to handle incoming messages.")
        S35 = State(35, "shutdown|close",
                    "Step 7: Use `shutdown()` and `close()` methods to cleanly terminate the connection and release resources.")
        S29.AddNext(S30)
        S30.AddNext(S31)
        S31.AddNext(S32)
        S32.AddNext(S33)
        S33.AddNext(S34)
        S34.AddNext(S35)
        Class.AddState(S29)
        self.IRIClfList.append(Class)

        # FSM 7: UDP Server based on socket+inet in C++
        Class = ApiClassifier("C++*", LANG_API_IRI, ".cpp", "UDP Server based on socket+inet in C++")
        S36 = State(36, "#include <sys/socket.h>|#include <netinet/in.h>",
                    "Step 1: Include necessary headers for working with UDP sockets (`sys/socket.h` and `netinet/in.h`).")
        S37 = State(37, "SOCK_DGRAM",
                    "Step 2: Create a socket using `SOCK_DGRAM` type to indicate that this is a UDP socket.")
        S38 = State(38, "bind", "Step 3: Bind the socket to a specific address and port using the `bind()` function.")
        S39 = State(39, "recvfrom|sendto",
                    "Step 4: Use `recvfrom()` to receive incoming UDP packets from clients or Use `sendto()` to send data back to the client.")
        S36.AddNext(S37)
        S37.AddNext(S38)
        S38.AddNext(S39)
        Class.AddState(S36)
        self.IRIClfList.append(Class)

        # FSM 8: UDP Server based on Boost.Asio in C++
        Class = ApiClassifier("C++*", LANG_API_IRI, ".cpp", "UDP based on Boost.Asio in C++")
        S40 = State(40, "#include <boost/asio.hpp>",
                    "Step 1: Include the necessary Boost.Asio header for working with UDP sockets.")
        S41 = State(41, "io_context",
                    "Step 2: Create an `io_context` object to manage asynchronous operations for Boost.Asio.")
        S42 = State(42, "socket",
                    "Step 3: Create a `boost::asio::ip::udp::socket` object to represent the UDP server socket.")
        S43 = State(43, "receive_from|send_to",
                    "Step 4: Use the `receive_from` method to asynchronously receive UDP datagrams from clients or use the `send_to` method to send a response back to the client after processing the data.")
        S40.AddNext(S41)
        S41.AddNext(S42)
        S42.AddNext(S43)
        Class.AddState(S40)
        self.IRIClfList.append(Class)

        # FSM 9: Websocket Server based on WebSocket++ in C++
        Class = ApiClassifier("C++*", LANG_API_IRI, ".cpp", "Websocket Server based on WebSocket++ in C++")
        S44 = State(44, "#include <websocketpp/server.hpp>",
                    "Step 1: Include the necessary WebSocket++ headers for server functionality.")
        S45 = State(45, "init_asio", "Step 2: Initialize WebSocket++'s ASIO-based network handling.")
        S46 = State(46, "set_message_handler",
                    "Step 3: Set up a message handler to process incoming messages from clients.")
        S47 = State(47, "listen", "Step 4: Start listening for incoming WebSocket connections on a specified port.")
        S48 = State(48, "start_accept", "Step 5: Start accepting WebSocket connections from clients.")
        S49 = State(49, "run", "Step 6: Run the server event loop to manage the connections and messages.")
        S44.AddNext(S45)
        S45.AddNext(S46)
        S46.AddNext(S47)
        S47.AddNext(S48)
        S48.AddNext(S49)
        Class.AddState(S44)
        self.IRIClfList.append(Class)

        # FSM 10: Pipe based on unistd.h in C++
        Class = ApiClassifier("C++*", LANG_API_IRI, ".cpp", "pipe based on unistd.h in C++")
        S50 = State(50, "#include <unistd.h>",
                    "Step 1: Include the necessary header file for working with pipes in C++. This enables pipe functionality.")
        S51 = State(51, "pipe",
                    "Step 2: Create a pipe using the `pipe` system call, which returns two file descriptors: one for reading and one for writing.")
        S52 = State(52, "fork",
                    "Step 3: Use `fork` to create a child process. The child process can now use the pipe for communication.")
        S53 = State(53, "close",
                    "Step 4: Close the pipe file descriptors in the appropriate process (either parent or child) to prevent resource leakage.")
        S54 = State(54, "read", "Step 5: Read data from the pipe in the appropriate process.")
        S55 = State(55, "write", "Step 6: Write data to the pipe in the appropriate process.")
        S56 = State(56, "close",
                    "Step 7: After the communication is complete, close the pipe file descriptors to clean up.")
        S50.AddNext(S51)
        S51.AddNext(S52)
        S52.AddNext(S53)
        S53.AddNext(S54)
        S53.AddNext(S55)
        S54.AddNext(S56)
        S55.AddNext(S56)
        Class.AddState(S50)
        self.IRIClfList.append(Class)

    def InitFfiClass (self):
        ############################################################
        # Class: C and Python
        ############################################################
        Class = ApiClassifier("Python-C/C++", LANG_API_FFI, ".c .cpp .py", 'ctypes')
        S0 = State(0, "import ctypes|from ctypes import .*","Step 1: Import the ctypes module to interact with shared libraries.")
        S1 = State(1, "CDLL|LoadLibrary","Step 2: Load the shared C library using ctypes.CDLL or ctypes.cdll.LoadLibrary.")
        S0.AddNext(S1)
        Class.AddState(S0)
        self.FFIClfList.append(Class)

        Class = ApiClassifier("Python-C/C++", LANG_API_FFI, ".c .cpp .py", 'cffi')
        S2 = State(2, "from cffi import FFI|from cffi import .*|import cffi","Step 1: Import the cffi module and initialize an FFI object.")
        S3 = State(3, "FFI", "Step 2: Create an FFI instance to declare C types and functions.")
        S4 = State(4, "cdef", "Step 3: Declare C function signatures using cdef.")
        S2.AddNext(S3)
        S3.AddNext(S4)
        Class.AddState(S2)
        self.FFIClfList.append(Class)

        Class = ApiClassifier("C/C++-Python", LANG_API_FFI, ".c .cpp .py", '#include <Python.h>')
        S6 = State(6, "#include <Python.h>","Step 1: Include the Python C API header to enable embedding Python.")
        S7 = State(7, "PyObject|Py_Initialize|PyMethodDef","Step 2: Initialize the Python interpreter, declare method definitions, or define Python object references.")
        S6.AddNext(S7)
        Class.AddState(S6)
        self.FFIClfList.append(Class)







