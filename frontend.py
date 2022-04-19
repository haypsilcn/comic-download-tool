import time
from tkinter import ttk
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import tkinter.font as font
from validators import ValidationFailure
import validators
import scraping
import os.path
import webbrowser


################################################################################################
# Preparations
################################################################################################
def setFontSize(size):
    return font.Font(size=size)


def validateFolder():
    path = folder.get(1.0, END).replace("\n", "")
    return os.path.exists(path)


def disableButton(disable: bool):
    if disable:
        downloadAllButton["state"] = DISABLED
        downloadSelectedButton["state"] = DISABLED
        clearButton["state"] = DISABLED
        quitButton["state"] = DISABLED
    else:
        downloadAllButton["state"] = NORMAL
        downloadSelectedButton["state"] = NORMAL
        clearButton["state"] = NORMAL
        quitButton["state"] = NORMAL

# false to download all, true to download selected chap
def download(selected: bool, path):
    if not validateFolder():
        messagebox.showerror("Invalid path", "Directory is not exist. Please check again")
    else:
        progressbar["value"] = 0
        disableButton(True)
        listBox["state"] = DISABLED
        directoryButton["state"] = DISABLED
        scraping.errorMsg.clear()
        if selected:
            try:
                scraping.download(selectedChapter, path, progressbar, window, statusLabel)
            except:
                messagebox.showerror("Invalid selected item", "Please select a chapter")
        else:
            for chapterNr in chapterList.keys():
                scraping.download(chapterNr, path, progressbar, window, statusLabel)

        statusLabel["text"] = "Downloading finish!"

        listBox["state"] = NORMAL
        directoryButton["state"] = NORMAL
        disableButton(False)

        if len(scraping.errorMsg) != 0:
            messagebox.showinfo("Progress status", str(scraping.errorMsg).removeprefix("[").
                                removesuffix("]").replace("'", "").replace(", ", "\n"))


################################################################################################
# commands
################################################################################################
def setFolder():
    path = filedialog.askdirectory()
    folder.config(state=NORMAL)
    folder.delete(1.0, END)
    folder.insert(1.0, path)
    folder.config(state=DISABLED)

    if len(path) != 0 and validateLinkButton["state"] == DISABLED:
        downloadAllButton["state"] = NORMAL
        downloadSelectedButton["state"] = NORMAL
    elif len(path) == 0:
        downloadAllButton["state"] = DISABLED
        downloadSelectedButton["state"] = DISABLED

def doubleClick(event):
    if len(scraping.listChapter) != 0:
        index = listBox.curselection()
        selected = listBox.get(index)
        webbrowser.open(chapterList.get(selected), new=2, autoraise=False)

def singleClick(event):
    if len(scraping.listChapter) != 0:
        index = listBox.curselection()
        global selectedChapter
        selectedChapter = listBox.get(index)

def validateLink():
    url.set(url.get().replace(" ", ""))  # remove all leading and trailing spaces and multiple space in between
    result = validators.url(url.get())

    if len(url.get()) == 0:
        messagebox.showerror("Empty URL", "Please insert an URL")
    elif isinstance(result, ValidationFailure):
        messagebox.showerror("Invalid URL", "URL is invalid. Please check again")
    else:
        global chapterList
        chapterList = scraping.getChapterLinkList(url.get())
        if len(chapterList) == 0:
            messagebox.showerror("Error", "Cannot get any chapters from link. Please check again")
        else:
            listBox.delete(0, END)
            progressbar["maximum"] = len(chapterList)
            statusLabel["text"] = "Loading all chapters..."
            disableButton(True)
            for chapter in chapterList.keys():
                listBox.insert(END, chapter)
                progressbar["value"] += 1
                window.update_idletasks()  # update progress value in window
                time.sleep(0.0001)

            statusLabel["text"] = "All  chapters loaded!"
            urlEntry["state"] = "disabled"
            validateLinkButton["state"] = DISABLED
            clearButton["state"] = NORMAL
            quitButton["state"] = NORMAL
            if validateFolder():
                downloadAllButton["state"] = NORMAL
                downloadSelectedButton["state"] = NORMAL

def downloadAll():
    path = folder.get(1.0, END).replace("\n", "")
    download(False, path)

def downloadSelected():
    path = folder.get(1.0, END).replace("\n", "")
    download(True, path)

def clear():
    if listBox.size() != 0:
        chapterList.clear()
    urlEntry["state"] = NORMAL
    validateLinkButton["state"] = NORMAL
    downloadAllButton["state"] = DISABLED
    downloadSelectedButton["state"] = DISABLED
    url.set("")
    listBox.delete(0, END)
    progressbar["value"] = 0
    statusLabel["text"] = ""
    scraping.clear()


def quitProgram():
    msg = messagebox.askokcancel("Close program", "Close the program?")
    if msg:
        window.destroy()


################################################################################################
# Set up GUI
################################################################################################
window = Tk()
window.title("Comic Download Tool")
window.geometry("960x540")
window.resizable(False, False)

# url
urlLabel = Label(window, text="URL", height=2, width=7, font=setFontSize(13))
urlLabel.grid(row=0, column=0)
url = StringVar()
urlEntry = Entry(window, width=60, textvariable=url, font=setFontSize(15))
urlEntry.grid(row=0, column=1)

# folder
folderLabel = Label(window, text="Directory", height=2, width=8, font=setFontSize(13))
folderLabel.grid(row=1, column=0)
folder = Text(window, width=60, height=1, font=setFontSize(15), )
folder.grid(row=1, column=1)
folder.config(state=DISABLED, wrap=NONE)  # set read-only mode and single line


progressLabel = Label(window, text="Status progress", height=2, width=15, font=setFontSize(13))
progressLabel.grid(row=2, column=2)

statusLabel = Label(window, text="", height=2, width=22, font=setFontSize(13))
statusLabel.grid(row=4, column=2)
progressbar = ttk.Progressbar(window, orient=HORIZONTAL, mode="determinate", length=210)
progressbar.grid(column=2, row=3)

# listbox
frame = Frame(window)
frame.grid(row=2, column=0, rowspan=20, columnspan=2, pady=20)

scrollBar = Scrollbar(frame, orient=VERTICAL, width=20)
slideBar = Scrollbar(frame, orient=HORIZONTAL, width=20)

listBox = Listbox(frame, height=16,
                  yscrollcommand=scrollBar.set,
                  xscrollcommand=slideBar.set,
                  width=60, font=setFontSize(15),
                  borderwidth=3)
listBox.bind("<Double-1>", doubleClick)  # double-click mode
listBox.bind("<<ListboxSelect>>", singleClick)  # single-click mode
scrollBar.config(command=listBox.yview)  # create a scrollbar widget and set its command to the list box widget
slideBar.config(command=listBox.xview)
slideBar.pack(side=BOTTOM, fill=X, expand=True, pady=10)
listBox.pack(side=LEFT, fill=BOTH, expand=True, padx=15)
scrollBar.pack(side=RIGHT, fill=Y, expand=True)

# buttons
directoryButton = Button(window, text="Choose directory",
                         width=15, font=setFontSize(13),
                         command=setFolder, borderwidth=4)
validateLinkButton = Button(window, text="Validate link",
                            width=15, font=setFontSize(13),
                            borderwidth=4, command=validateLink)
downloadAllButton = Button(window, text="Download all",
                           width=20, pady=10, font=setFontSize(13),
                           state=DISABLED, borderwidth=4,
                           command=downloadAll)
downloadSelectedButton = Button(window, text="Download selected",
                                width=20, pady=10,
                                font=setFontSize(13), borderwidth=4,
                                state=DISABLED, command=downloadSelected)
clearButton = Button(window, text="Clear",
                     width=20, pady=10,
                     font=setFontSize(13), borderwidth=4,
                     command=clear)
quitButton = Button(window, text="Quit",
                    width=20, pady=10,
                    font=setFontSize(13), borderwidth=4,
                    command=quitProgram)

validateLinkButton.grid(row=0, column=2)
directoryButton.grid(row=1, column=2)
downloadAllButton.grid(row=9, column=2)
downloadSelectedButton.grid(row=10, column=2)
clearButton.grid(row=11, column=2)
quitButton.grid(row=12, column=2)
window.mainloop()
