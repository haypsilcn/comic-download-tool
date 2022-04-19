import time
import requests
from bs4 import BeautifulSoup
import pathlib
import os.path
import shutil
from tkinter import messagebox
from tkinter import ttk
from tkinter import *

listChapter = []
listChapterLink = []
errorMsg = []

def clear():
    listChapter.clear()
    listChapterLink.clear()
    errorMsg.clear()

def validateFolder(path, chapterNr):
    path = path + "/" + chapterNr
    if not os.path.exists(path):
        pathlib.Path(path).mkdir()
        return True
    else:
        msg = messagebox.askokcancel("Folder found",
                                     "Folder " + chapterNr + " is already exist.\nDo you want to replace it?")
        if msg:
            shutil.rmtree(path)
            pathlib.Path(path).mkdir()
            return True
        else:
            return False

def connectLink(url=""):
    request = requests.get(url)
    return request.content

def getChapterLinkList(url):
    clear()
    content = connectLink(url)
    soup = BeautifulSoup(content, "html.parser")
    allChapters = soup.find_all("div", {"class": "works-chapter-item"})
    for chapter in allChapters:
        chapterLink = chapter.find("a", {"target": "_self"})
        listChapterLink.append(chapterLink.get("href"))
        listChapter.append(chapterLink.text)
    return dict(zip(listChapter, listChapterLink))

def getChapterDict():
    return dict(zip(listChapter, listChapterLink))

def download(chapterNr, path, progressbar: ttk.Progressbar, window: Tk, statusLabel: Label):
    chapterDict = getChapterDict()
    chapterLink = chapterDict.get(chapterNr)

    content = connectLink(chapterLink)
    soup = BeautifulSoup(content, "html.parser")
    allImage = soup.find_all("div", {"class": "page-chapter"})

    progressbar["maximum"] = len(allImage)
    progressbar["value"] = 0
    index = 0
    statusLabel["text"] = "Downloading " + chapterNr + "...\nPlease be patient"

    if validateFolder(path, chapterNr):
        for image in allImage:
            try:
                imgSrc = image.find("img").get("src")
                getSrc = requests.get(imgSrc)
                if getSrc.status_code == 200:
                    with open(path + "/" + chapterNr + "/" + str(index) + ".jpg", "wb") as file:
                        file.write(getSrc.content)
                    index += 1
                    progressbar["value"] += 1
                    window.update_idletasks()
                    time.sleep(0.001)
                else:
                    imgBackUp = image.find("img").get("data-cdn")
                    getBackUp = requests.get(imgBackUp)
                    if getBackUp.status_code == 200:
                        with open(path + "/" + chapterNr + "/" + str(index) + ".jpg", "wb") as file:
                            file.write(getBackUp.content)
                        index += 1
                        progressbar["value"] += 1
                        window.update_idletasks()
                        time.sleep(0.001)
                    else:
                        errorMsg.append("Download progress for " + chapterNr + " corrupted due to link error")
                        progressbar["value"] += 1
                        window.update_idletasks()
                        time.sleep(0.001)
                        break
            except:
                errorMsg.append("Download progress for " + chapterNr + " corrupted due to link error")
                progressbar["value"] += 1
                window.update_idletasks()
                time.sleep(0.001)
                break
    else:
        errorMsg.append(chapterNr + " is already downloaded before")
