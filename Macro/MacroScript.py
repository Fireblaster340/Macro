import tkinter as tk
from tkinter.messagebox import showinfo, askokcancel, showerror
from tkinter import simpledialog
from tkinter.filedialog import askopenfile
import os
try:
    from pynput.keyboard import Listener as KList, Key, Controller as KCont
except ModuleNotFoundError:
    print("Installing pynput...")
    os.system('pip3 install pynput')
try:
    from pynput.keyboard import Listener as KList, Key, Controller as KCont
    from pynput.mouse import Listener as MList, Button, Controller as MCont
except ModuleNotFoundError:
    showerror("Fatal Error","Fatal Error, pynput library failed to install, try installing manually")
    paused = True
import threading 
import time

root = tk.Tk()
root.title("Macro")
root.geometry("400x400")
root.resizable(False,False)
pause = "']'"
end = "'['"
lastmacro, allkeys, allMouseClicks = [],[],[]
mouseDx, mouseDy = 0,0
SampleRate = 0.01
paused, Looping, startpause, PauseLoop, islistening, showmsg, mrun = False,False,False,False,False,False,False
Running = True
recordedpath = os.path.join(os.path.expanduser("~"),"Desktop","Macro","RecordedMacros")
pathnames = os.path.join(os.path.expanduser("~"),"Desktop","Macro","Pathnames")
mainfile = os.path.join(os.path.expanduser("~"),"Desktop","Macro")
def ReplaceFile(path):
    global paused
    try:
        open(path,"r").close()
    except FileNotFoundError:
        showerror("File Missing","Critical file is missing, creating it")
        try:
            open(path,"w").close()
        except FileNotFoundError:
            showerror("Fatal Error","Fatal Error, path opening has failed. This program is not compatible with your system yet")
            paused = True

def ListenLoop():
    global islistening, lastmacro, SampleRate, startpause, concat
    lastmacro = []
    concat = ""
    root.withdraw()
    root.update()
    if startpause:
        concat = "P"
    while concat == "P":
        if not islistening:
            break
    while islistening:
        concat = ""
        pos = str(MCont().position[0])+" "+str(MCont().position[1])
        concat+=str(mouseDx)+" "+str(mouseDy)+" "
        for k in allkeys:
            concat+=str(k)+" "
        concat += "M "
        for k in allMouseClicks:
            concat+=str(k)+" "
        lastmacro.append(pos+" "+concat)
        if paused:
            while paused:
                if not islistening:
                    break
        else:
            time.sleep(SampleRate)
    path = os.path.join(os.path.expanduser("~"),"Desktop","Macro","TempMacro")
    file = open(path,"w")
    file.writelines(str(SampleRate)+"\n")
    for item in lastmacro:
        file.writelines(item+"\n")
    file.close()
    if askokcancel(title="Save", message="Write to file? The recording is stored temporarily if you cancel"):
        path = NextFreePath(os.path.join(recordedpath,"Recording"))
        try:
            file = open(path,'w')
            file.writelines(str(SampleRate)+"\n")
            for item in lastmacro:
                file.writelines(item+"\n")
            file.close()
            file = open(pathnames,'a')
            file.writelines(path+"\n")
            file.close()
            showinfo("Saved","Saved Successfully! Path: "+path)
        except OSError:
            showerror("Failed","Unexpected error occured during saving, path info: "+path)
 
    root.wm_deiconify()

def NextFreePath(path:str):
    validfound = False
    att = 0     
    while not validfound:
        name = path+str(att)
        try:
            open(os.path.join(path,name),"r").close()
            att+=1
        except (OSError,FileExistsError,FileNotFoundError):
            validfound = True
    return name
def KeyThread():
    global islistening
    try:
        print("Key Starting...")
        with KList(on_press=UpdPress, on_release=UpdRel) as listener:
            print("Key Successfully Running")
            listener.join()
    except Exception:
        root.destroy()
        print("Listeners Failed, restarting... attempting recursive call")
        StartProgram()
        return 0

def UpdPress(Key):
    global paused, islistening, PauseLoop, Looping, Running, concat, begin
    if islistening:
        if Key not in allkeys:
            if str(Key) not in [pause,end]:
                if not paused:
                    allkeys.append(Key)
            elif str(Key) == end:
                ToggleListen()
            else:
                if concat == "P":
                    concat = ""
                else:
                    paused = not paused
    else:
        if str(Key) == pause:
            PauseLoop = not PauseLoop
        if str(Key) == end:
            Running = False
            if Looping:
                Looping = False
                time.sleep(0.1)
                Looping = True
            else:
                Looping = False
def UpdRel(Key):
    if Key in allkeys and not paused:
        allkeys.remove(Key)

def MouseThread():
    global islistening, mrun
    try:
        print("Mouse Starting...")
        with MList(on_click=UpdClick, on_scroll=UpdScroll) as listenerm:
            print("Mouse Running Successfully")
            mrun = True
            listenerm.join()
    except Exception:
        root.destroy()
        print("Listeners Failed, restarting... attempting recursive call")
        StartProgram()
        return 0

def UpdClick(x,y,Button,Pressed):
    global allMouseClicks
    if not paused:
        if Pressed:
            if Button not in allMouseClicks:
                allMouseClicks.append(Button)
        else:
            if Button in allMouseClicks:
                allMouseClicks.remove(Button)


def UpdScroll(x,y,dx,dy):
    global mouseDx, mouseDy
    if not paused:
        mouseDx = dx
        mouseDy = dy

def ClearAll():
    for widget in root.winfo_children():
        widget.destroy()
def Home():
    ClearAll()
    root.geometry("400x400")
    title = tk.Label(root, text="Macro Cool", font=("TkDefaultFont",30))
    title.pack(padx=0,pady=0)
    sub1 = tk.Label(root, text=("Press the button to listen for macro, pause keybind="+str(pause)),wraplength=400)
    sub1.pack(padx=0,pady=5)
    listenoption = tk.Button(root, text="Listen for macro", command=ListenPage)
    listenoption.pack(padx=0,pady=5)
    sub2 = tk.Label(root, text="Press the button to view the saved macros")
    sub2.pack(padx=0,pady=5)
    replayfiles = tk.Button(root, text="Replay Files", command=ReplayFiles)
    replayfiles.pack(padx=0,pady=5)
    settings = tk.Button(root,text="Settings",command=Settings)
    settings.pack(padx=0,pady=20)
    extra = tk.Button(root,text="Note",command=lambda:showinfo("Extra information","Some limitations of this macro: very rapid inputs are not captured if you keep the sample rate low. Certain keys, such as the side mouse buttons may not work. After some testing, I believe that toggling caps lock during any point of running the macro will shut it down with an illegal instruction error. Holding keys down does not work in text editors. Also some gestures such as swiping across desktops wont work."))
    extra.pack(pady=20)

def Settings():
    global SmplRt, PauseEnt, Total
    ClearAll()
    root.geometry("400x600")
    Total = ComputeSize()
    STitle = tk.Label(root, text="Settings", font=("TkDefaultFont",30))
    STitle.pack(padx=0,pady=0)
    SampleTxt = tk.Label(root,text="Change sample rate, default = 0.01 (100 times per second)")
    SampleTxt.pack(padx=0,pady=5)
    SmplRt = tk.Entry(root)
    SmplRt.pack(padx=0,pady=6)
    Submit = tk.Button(root, text="Submit", command=SubmitSample)
    Submit.pack(padx=0,pady=3)
    SmplRt.focus()
    Loop = tk.Label(root,text="Loop macro replay?")
    Loop.pack(pady=5)
    LoopChk = tk.Checkbutton(root,command=LoopOn)
    LoopChk.pack(pady=3)
    if Looping:
        LoopChk.select()
    ErrorShow = tk.Label(root,text="Show Error Messages?")
    ErrorShow.pack(pady=5)
    ErrorChk = tk.Checkbutton(root,command=MsgOn)
    ErrorChk.pack(pady=3)
    if showmsg:
        ErrorChk.select()
    PauseTxt = tk.Label(root, text="Change Pause Keybind")
    PauseTxt.pack(pady=5)
    PauseEnt = tk.Entry(root)
    PauseEnt.pack(pady=3)
    PauseB = tk.Button(root, text="Submit",command=PauseSet)
    PauseB.pack(pady=3)
    StorageUsed = tk.Label(root, text=f"Storage Used: {Total}")
    StorageUsed.pack(pady=8)
    CreateHome()
def PauseSet():
    global PauseEnt, pause
    if PauseEnt.get() == "[":
        showerror("Unable to set keybind","Pause keybind interferes with stop keybind")
        return 0
    if "Key" in str(pause):
        pause = getattr(Key,(PauseEnt.get()).split(".")[1])
    else:
         pause = "'"+PauseEnt.get()+"'"
def LoopOn():
    global Looping
    Looping = not Looping
def MsgOn():
    global showmsg
    showmsg = not showmsg
def SubmitSample():
    global SmplRt, SampleRate
    try:
        if float(SmplRt.get()) < 0.005:
            if not askokcancel("Warning","Warning: This sample rate often causes insane lag"):
                return 0
        SampleRate = float(SmplRt.get())
        showinfo("Success!","Successfully changed settings")
    except ValueError:
        showerror("Error","Incorrect data type, expected float/int")

def ListenPage():
    global begin, startpause
    ClearAll()
    listentxt = tk.Label(root,text="Macro Listener",font=("TkDefaultFont",30))
    listentxt.pack(padx=0,pady=0)
    info = tk.Label(root,text="Listens to inputs and stores it as a text file",font=("TkDefaultFont",18))
    info.pack()
    pauserem = tk.Label(root,text="Pause key="+pause+", End Key='['",font=("TkDefaultFont",15))
    pauserem.pack(padx=0,pady=5)
    begin = tk.Button(root, text="Start listening", command=ToggleListen)
    begin.pack(padx=0,pady=5)
    spause = tk.Label(root, text="Start on pause?")
    spause.pack(pady=10)
    spausecheck = tk.Checkbutton(root, command=ToggleStart)
    spausecheck.pack(pady=5)
    if startpause:
        spausecheck.select()
    CreateHome()
def RemoveBreak(String):
    return String[:-1]
def ConvertSize(size:int):
    if size == 0:
        return "0B"
    convbyte = ["B","KB","MB","GB","TB","PB","XB","ZB","YB","BB","GPB","HB"]
    for i in range(len(convbyte)):
        if 1024**int(i) > int(size):
            size = size/(1024**(i-1))
            break
    return f"{size:.1f}"+convbyte[i-1]

def AddSize(path):
    return path+" - "+ConvertSize(os.path.getsize(path))
def ToggleStart():
    global startpause
    startpause = not startpause
def ReplayFiles():
    global drop, var, Running, paused, Looping, speed, savedcontents
    ClearAll()  
    root.geometry("400x600")
    title = tk.Label(root, text="File Replayer", font=("TkDefaultFont",30))
    title.pack()
    info = tk.Label(root, text="Select a file name from the drop down menu to run")
    info.pack()
    var = tk.StringVar(root)
    var.set("Select File")
    file = open(pathnames,"r")
    contents = list(map(RemoveBreak, file.readlines()))
    savedcontents = contents
    try:
        contents = list(map(AddSize, contents))
    except FileNotFoundError:
        showerror("Error","PathNames file is inconsistent with files, fixing...")
        for item in contents:
            try:
                file = open(item,"r")
            except FileNotFoundError:
                file = open(pathnames,"r")
                filepaths = list(map(RemoveBreak,file.readlines()))
                file.close()
                file = open(pathnames,"w")
                file.write("")
                for i in filepaths:
                    if item != i:
                        file.writelines(i+"\n")
            file.close()
        showinfo("Fixed","Inconsistency was corrected. If the error persists, manually match the recording file names with the names in pathnames")
        Home()
        return 0
    if len(contents) == 0:
        contents = ["No saves... yet..."]
    drop = tk.OptionMenu(root,var,*contents)
    drop.pack(pady=5)
    spinfo = tk.Label(root,text="Replay Speed (percent of original)")
    spinfo.pack(pady=5)
    speed = tk.Scale(root,from_=20,to=1000,orient="horizontal")
    speed.set(100)
    speed.pack(pady=5)
    select = tk.Button(root,text="Run File",command=RunMacro)
    select.pack(pady=5)
    delete = tk.Button(root,text="Delete",command=lambda:Delete(var.get()))
    delete.pack(pady=5)
    temp = tk.Button(root,text="Replay last recording",command=lambda:RunMacro(True))
    temp.pack(pady=5)
    rename = tk.Button(root,text="Rename file",command=Rename)
    rename.pack(pady=5)
    importing = tk.Button(root,text="Import File",command=FileImport)
    importing.pack(pady=5)
    advanced = tk.Button(root,text="Advanced options",command=Advanced)
    advanced.pack(pady=6)
    root.update()
    CreateHome()

def Advanced():
    ClearAll()
    root.geometry("400x500")
    advtitle = tk.Label(root, text="Advanced Options", font=("TkDefaultFont",30))
    advtitle.pack()
    mergebutton = tk.Button(root, text="Merge Files", command=MergePage)
    mergebutton.pack(pady=6)
    back = tk.Button(root,text="Back",command=ReplayFiles)
    back.pack() #I can't help but comment at how W this line is
def MergePage():
    global savedcontents, root
    ClearAll()
    root.geometry("400x400")
    title = tk.Label(root,text="Merge Files",font=("TkDefaultFont",30))
    title.pack()
    info = tk.Label(root,text="Merging chains together 2 files that will play directly after another.",wraplength=400)
    info.pack()
    name1 = tk.Label(root,text="First file",font=("TkDefaultFont",20))
    name1.pack()
    var1 = tk.StringVar(root)
    item1 = tk.OptionMenu(root,var1,*savedcontents)
    item1.pack(pady=5)
    name2 = tk.Label(root,text="Second file",font=("TkDefaultFont",20))
    name2.pack()
    var2 = tk.StringVar(root)
    item2 = tk.OptionMenu(root,var2,*savedcontents)
    item2.pack(pady=5)
    mergebutton = tk.Button(root,text="Merge Files",command=lambda:Merge(var1.get(),var2.get()))
    mergebutton.pack(pady=5)
    advback = tk.Button(root,text="Back",command=Advanced)
    advback.pack()
    
def Merge(path1:str="Empty",path2:str="Empty"):
    if path1 == "Empty" or path2 == "Empty":
        showerror("Error", "Input something as a file path")
        return 0
    try:
        concat = ""
        file = open(path1,"r")
        contents1 = list(map(RemoveBreak,file.readlines()))
        file.close()
        file = open(path2,"r")
        contents2 = list(map(RemoveBreak,file.readlines()))
        file.close()
        srate = "0.01"
        if askokcancel("Sample Rate","Use weighted average of sample rate?"):
            srate = str((float(contents1[0])*len(contents1)+float(contents2[0])*len(contents2))/(len(contents1)+len(contents2)))
        else:
            if askokcancel("Use file 1 sample rate?"):
                srate = contents1[0]
            else:
                srate = contents2[0]
        contents1=contents1[1:]
        contents2=contents2[1:]
        concat = srate+"\n"
        for i in contents1:
            concat+=i+"\n"
        for i in contents2:
            concat+=i+"\n"
        mergedpath = os.path.join(recordedpath,NextFreePath(os.path.join(recordedpath,"Merge")))
        file = open(mergedpath,"w")
        file.writelines(concat)
        file.close()
        file = open(pathnames,"a")
        file.writelines(mergedpath+"\n")
    except (FileNotFoundError,OSError):
        showerror("Failed","An unexpected error occurred, failed to merge")
        return 0
    showinfo("Success!","Merging completed successfully and saved!")
def FileImport():
    if not askokcancel("Confirm","The file that you select will be moved to RecordedMacros folder, proceed?"):
        return 0
    filename = askopenfile(filetypes=[("Plain text files","*.txt")])
    if filename is None:
        return 0 
    if not filename.name.endswith(".txt"):
        if not askokcancel("Extension","This file does not have a .txt extension, if you would like to import anyways then press OK"):
            return 0
    if filename is None:
        return 0

    new = recordedpath+(filename.name).split("/" if "/" in filename.name else "\\")[-1]
    try:
        os.rename(filename.name,new)
    except PermissionError:
        showerror("Error","Could not import file, missing permissions")
        showinfo("Rare Notice!","Just saying, that was a very rare error lol. I did not know that was an exception till like just now haha.")
        return 0
    file = open(pathnames,'a')
    file.writelines(new+"\n")
    file.close()
    Home()
def Rename():
    global var
    if var.get().split()[0] in ["No", "Select"]:
        showerror("No Selection","You have not selected any path for renaming")
        return 0
    root.withdraw()
    newname = simpledialog.askstring("Rename","What would you like to rename this file to?")
    if newname == None:
        return 0
    newpath = os.path.join(recordedpath,newname)
    os.rename(var.get().split()[0],newpath)
    file = open(pathnames,"r")
    allpaths = list(map(RemoveBreak,file.readlines()))
    file.close()
    file = open(pathnames,"w")
    file.write("")
    for i in allpaths:
        if var.get().split()[0] == i:
            file.writelines(newpath+"\n")
        else:
            file.writelines(i+"\n")   
    file.close() 
    root.wm_deiconify()
    Home()    
 

def Delete(path:str):
    if path == "No saves... yet..." or path == "Select File":
        showerror("No Selection","You have not selected any path for deletion")
        return 0
    if not askokcancel("Sure","Are you sure you want to delete this file? You cannot retrieve it once deleted"):
        return 0
    path = path.split()[0]
    os.remove(path)
    file = open(pathnames,"r")
    files = list(map(RemoveBreak,file.readlines()))
    file.close()
    file = open(pathnames,"w")
    file.write("")
    for i in files:
        if path != i:
            file.writelines(i+"\n")
    file.close()
    Home()

def ParseLine(line:str):
    global showmsg
    line = line.split()
    try:
        position = tuple(map(float, line[:2]))
        scrolldelta = tuple(map(float, line[2:4]))
        mouseinputs = []
        keyinputs = []
        currpos = 5
        for x in line[4:]:
            if x == "M":
                break
            currpos+=1 
            keyinputs.append(x)
        mouseinputs = line[currpos:]
    except (IndexError, ValueError):
        if showmsg:
            showerror("File Issue", "Failed to execute line, execution will not stop")
            showmsg = False
        return ((0,0),(0,0),[],[])
    return (position, scrolldelta, mouseinputs, keyinputs) 
 
def RunMacro(Temp=False):
    global var, Looping, Running, PauseLoop, speed, root
    frames = []
    Unparsed = []
    Running = True
    PauseLoop = False
    try:
        if not Temp and (var.get() == "No saves... yet..." or var.get() == "Select File"):
            showerror("Error", "Attempted to open no files. First try saving some files or selecting one to open")
            return None
        if Temp:
            file = open(os.path.join(os.path.expanduser("~"),"Desktop","Macro","TempMacro"),"r")
            Unparsed = file.readlines()
            if Unparsed == []:
                showerror("Error","No temporary recording available")
                return None
        else:
            file = open(var.get().split(" ")[0],"r")
            Unparsed = file.readlines()
    except NotADirectoryError:
        showerror("Error","Hello! This is a free open source macro! Its not amazing but it works! Attempted to open file that doesn't exist. Most likely cause is pathnames file is inconsistent, update it manually by adding the path of the missing file(s) and going to the next line. Soon, I will add automatic correction. Sometimes, I don't know when, there will be an error caught during execution of a recording. If this happens, you can continue execution of the macro, however it will contain missing parts. You can toggle this message in settings, once you've chosen to proceed despite the error, the message will never appear.")
        return None
    for item in map(RemoveBreak,Unparsed):
        frames.append(item)
    try:
        wait = float(frames.pop(0))
    except (ValueError, TypeError, IndexError):
        showerror("Error","Invalid Sample Rate Found, Defaulting to 0.01")
    wait = 0.01
    wait /= speed.get()
    wait *= 100
    root.withdraw()
    root.update()
    Execute(frames,wait)
    while Looping: 
        Execute(frames,wait)
    root.wm_deiconify()
def Execute(frames, wait):
    global PauseLoop, Looping, Running, showmsg, root
    mouse = MCont()
    keyboard = KCont()
    currkeys = []
    currmouse = []
    validkeys = []
    validmouse = []
    for item in frames:
        try:
            parsed = ParseLine(item)
            mouse.position = parsed[0]
            mouse.scroll(dx=parsed[1][0],dy=parsed[1][1])
            for k in range(len(validmouse)):
                validmouse[k] = False
            if len(parsed[2]) != 0:
                for i in parsed[2]:
                    i = str(i).split(".")[1]
                    i = getattr(Button, i)
                    if i not in currmouse:
                        currmouse.append(i)
                        validmouse.append(True)
                        mouse.press(i)
                    else:
                        validmouse[currmouse.index(i)] = True
            torem = []
            for k in range(len(validmouse)):
                if not validmouse[k]:
                    mouse.release(currmouse[k])
                    torem.append(k)
            for x in torem:
                validmouse.pop(x)
                currmouse.pop(x)
                
            for k in range(len(validkeys)):
                validkeys[k] = False
            if len(parsed[3]) != 0:
                for i in parsed[3]:
                    if "Key" in i:
                        i = str(i).split(".")[1]
                        i = getattr(Key, i)
                    else:
                        i = i[1]
                    if i not in currkeys:
                        currkeys.append(i)
                        validkeys.append(True)
                        keyboard.press(i)
                    else:
                        validkeys[currkeys.index(i)] = True
            torem = []
            for k in range(len(validkeys)):
                if not validkeys[k]:
                    keyboard.release(currkeys[k])
                    torem.append(k)
            for x in torem:
                currkeys.pop(x)
                validkeys.pop(x)
            time.sleep(float(wait))
            if not Running:
                break
            while PauseLoop:
                pass
        except IndexError:
            if showmsg:
                if not askokcancel("Error","Error was caught, proceed with Macro? (Parts of macro will be missing)"):
                    showmsg = False
                    break
        except ValueError:
            if showmsg:
                if not askokcancel("Fatal Error", "Fatal error with file, macro likely will not work, proceed anyways?"):
                    showmsg = False
                    break
    for i in currmouse:
        mouse.release(i)
    for i in currkeys:
        keyboard.release(i)
def CreateHome():
    global home
    home = tk.Button(root,text="Home",command=Home)
    home.pack(padx=0,pady=30)
def ToggleListen():
    global begin, islistening
    if not islistening:
        begin.config(text="Stop listening")
        islistening = True
        time.sleep(0.1)
        Loop = threading.Thread(target=ListenLoop,args=())
        Loop.start()
    else:
        begin.config(text="Start listening")
        islistening = False

def ComputeSize():
    Total = 0
    try:
        file = open(os.path.join(mainfile,"Pathnames"))
        for i in list(map(RemoveBreak, file.readlines())):
            Total += os.path.getsize(i)
        Total += os.path.getsize(os.path.join(mainfile,"MacroScript.py"))
    except FileNotFoundError:
        showerror("File Missing","Detected a nonexistent file, open the replay files page to autocorrect")
        return 0
    Total = ConvertSize(Total)
    return Total
def StartProgram():
    global KT, MT, Total
    Home()
    print("Starting threads")
    MT = threading.Thread(target=MouseThread,args=())
    MT.start()
    while not mrun:
        pass
    KT = threading.Thread(target=KeyThread,args=())
    KT.start()
    Total = 0
    try:
        os.remove(os.path.join(recordedpath,"Placeholder"))
        showinfo("Thanks","Hi there! Thanks for downloading my macro, feel free to send any suggestions my way! Auto removed placeholder file.")
    except FileNotFoundError:
        pass
    ReplaceFile(os.path.join(mainfile,"Pathnames"))
    ReplaceFile(os.path.join(mainfile,"TempMacro"))
    Total = ComputeSize()
    root.mainloop()
    
if not paused:
    StartProgram()   
quit(0)
