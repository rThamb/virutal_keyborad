import tkinter as tk
from tkinter import filedialog
import time
import threading 
import cv2
import numpy as np

import requests
import io
import json

class Menubar:

    def __init__(self, parent):
        font_specs = ("ubuntu", 10)

        menubar = tk.Menu(parent.master, font=font_specs)
        parent.master.config(menu=menubar)

        file_dropdown = tk.Menu(menubar, font=font_specs, tearoff=0)
        file_dropdown.add_command(label="New File", command=parent.new_file)
        file_dropdown.add_command(label="Open File", command=parent.open_file)
        file_dropdown.add_command(label="Save", command=parent.save)
        file_dropdown.add_command(label="Save As", command=parent.save_as)
        file_dropdown.add_separator()
        file_dropdown.add_command(label="Exit", command=parent.master.destroy)

        menubar.add_cascade(label="File", menu=file_dropdown)


class PyText:
 
    inputText = ''
    global runCamera 
    global writeCharacter
    free = 1
    global t2

    def __init__(self, master):
        master.title("Untitled - PyText")
        master.geometry("1200x700")
        font_specs = ("ubuntu", 18)
        self.master = master
        self.filename = None
        self.textarea = tk.Text(master, font=font_specs)
        self.scroll = tk.Scrollbar(master, command=self.textarea.yview)
        self.textarea.configure(yscrollcommand=self.scroll.set)
        self.textarea.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.menubar = Menubar(self)
        self.count = 0
        self.update_label()
        t1 = threading.Thread(target=runCamera, args=(self,)) 
        t1.start()
    
    def writeCharacter(self , letter):
        self.inputText = '--' + self.inputText + letter
        #self.inputText = self.inputText
        print("hi there")
        time.sleep(2)
        self.free = 1

    def update_label(self):
        if self.count < 3:
            self.textarea.delete(1.0, tk.END)
            self.textarea.insert(1.0, self.inputText)
            self.textarea.after(1000, self.update_label) # call this method again in 1,000 milliseconds
        print (self.count)

    def set_window_title(self, name=None):
        if name:
            self.master.title(name + " -PyText")
        else:
            self.master.title("Untitled - PyText")

    def new_file(self):
        self.textarea.delete(1.0, tk.END)
        self.filename = None
        self.set_window_title()

    def open_file(self):
        self.filename = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("All Files", "*.*"),
                       ("Text Files", "*.txt"),
                       ("Python Scripts", "*.py"),
                       ("Markdown Documents", "*.md"),
                       ("JavaScript Files", "*.js"),
                       ("HTML Documents", "*.html"),
                       ("PDF Files", "*.pdf"),
                       ("CSS Documents", "*.css")]
        )
        if self.filename:
            self.textarea.delete(1.0, tk.END)
            with open(self.filename, "r") as f:
                self.textarea.insert(1.0, f.read())
            self.set_window_title(self.filename)

    def save(self):
        if self.filename:
            try:
                textarea_content = self.textarea.get(1.0, tk.END)
                with open(self.filename, "w") as f:
                    f.write(textarea_content)
            except Exception as e:
                print(e)
        else:
            self.save_as()

    def save_as(self):
        try:
            new_file = filedialog.asksaveasfilename(
                initialfile="Untitled.txt",
                defaultextension=".txt",
                filetypes=[("All Files", "*.*"),
                           ("Text Files", "*.txt"),
                           ("Python Scripts", "*.py"),
                           ("Markdown Documents", "*.md"),
                           ("JavaScript Files", "*.js"),
                           ("HTML Documents", "*.html"),
                           ("PDF Files", "*.pdf"),
                           ("CSS Documents", "*.css")])
            textarea_content = self.textarea.get(1.0, tk.END)
            with open(new_file, "w") as f:
                f.write(textarea_content)
                self.filename = new_file
                self.set_window_title(self.filename)
        except Exception as e:
            print(e)


    def runCamera(self):
        cap = cv2.VideoCapture(0)

        while True:
            _, frame = cap.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred_frame = cv2.GaussianBlur(frame, (5, 5), 0)

            #laplacian = cv2.Laplacian(blurred_frame, cv2.CV_64F)
            canny = cv2.Canny(blurred_frame, 100, 150)

            if self.free == 1:
                self.free = 0

                # Take picture here
                cv2.imwrite(filename='saved_img.jpg', img=frame)
                # webcam.release()
                img_new = cv2.imread('saved_img.jpg', cv2.IMREAD_GRAYSCALE)
                img_new = cv2.imshow("Captured Image", img_new)
                # cv2.waitKey(1650)

                # #POST request
                path = 'saved_img.jpg'

                multipart_form_data = {'file': open(path, 'rb')}
                data = {'OCREngine': 2}
                headers = {'apikey' : "1a509a5fae88957" }

                print("Sending post")
                result = requests.post('https://api.ocr.space/parse/image', files=multipart_form_data, data=data,headers=headers)

                # #print text
                json_data = json.loads(result.content.decode())
                letter = json_data["ParsedResults"][0]["ParsedText"]

                #end 
                print(letter)

                t2 = threading.Thread(target=writeCharacter, args=(self,letter,)) 
                t2.start() 
                

            cv2.imshow("Canny", canny)


            key = cv2.waitKey(1)
            if key == 27:
                break

        cap.release()
        cv2.destroyAllWindows()



if __name__ == "__main__":
    master = tk.Tk()
    pt = PyText(master)
    master.mainloop()
