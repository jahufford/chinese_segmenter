""" Gui program that segments Chinese text into words. Uses the pkuseg toolkit.

PKUSEG: A Toolkit for Multi-Domain Chinese Word Segmentation. Luo, Ruixuan and Xu, Jingjing and Zhang, Yi and Zhang, Zhiyuan and Ren, Xuancheng and Sun, Xu
https://arxiv.org/abs/1906.11455

https://github.com/lancopku/pkuseg-python/tree/master/pkuseg
https://github.com/lancopku/pkuseg-python/blob/master/readme/readme_english.md
"""


import PySimpleGUI as sg
import pkuseg
from functools import reduce


segmenter = pkuseg.pkuseg(model_name="default")

# sg.theme('DarkTeal10')   # Add a touch of color

model_options = ["default", "web", "news", "medicine", "tourism"]

model_options = sg.Combo( values=model_options, default_value=model_options[0], key="-MODEL-")
left_column = [
     [sg.Text('Enter Chinese text to segment into words'),
     sg.Stretch(),
     sg.Text("Model"),
     model_options,
     sg.Button('Segment', key="-SEGMENT-BTN-")],
     [sg.Multiline(key="-ORIG-TEXT-",size=(80,50),expand_x=True, expand_y=True)]
 ]
right_column = [
            [sg.Text('Segmented text')],
            [sg.Multiline('',key="-OUTPUT-", size=(80,50),expand_x=True,expand_y=True)],
]

menu_def = [['&File','E&xit'],["&Help","&Help"]]
layout = [  
        [sg.Menu(menu_def, tearoff=False, pad=(200,1))],
        [sg.Column(left_column),
        sg.VSeperator(),
        sg.Column(right_column)]
]
help_text = """Paste the Chinese text to segment into words in the left text box.
You can either press enter or click the Segment button and the segmented output appears in the right text box.
The segmented output is already highlighted so you can you easily press ctrl-c to copy it.

You can choose to use a different pre-trained model by making a selection under the Model combobox"""

# Create the Window
window = sg.Window('Chinese Language Segmenter', layout, resizable=True, return_keyboard_events=True, finalize=True)

model_options.bind("<<ComboboxSelected>>","") # need to know when the model selection changes

import code

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event in [sg.WIN_CLOSED, "Exit"] : # if user closes window or clicks cancel
        break
    elif event == "Help":
        sg.Window('Chinese Language Segmenter', [[sg.T(help_text)], [sg.OK(s=10)]], disable_close=False).read(close=True)
    elif event == "-MODEL-":
        # model changed, update the segmenter
        segmenter = pkuseg.pkuseg(model_name=values["-MODEL-"])
    elif event in ["-SEGMENT-BTN-", "KP_Enter:104", "Return:36"]:
        # do some cleanup on the input string
        paragraphs = [para for para in values["-ORIG-TEXT-"].strip().split("\n") if para!=""]
        segged_list = [segmenter.cut(para) for para in paragraphs] # gives us a list of lists, cut() takes a string and returns a list
        
        #segmented_paragraphs = "\n\n".join([reduce(lambda sum, word: sum+word+" " if word not in [",","，"] else sum.strip()+word+" ", seg_para,"").strip() for seg_para in segged_list]).strip()
        # the following is equivalent to the commented line above, but the above line is pretty gnarly, reduce inside a comprehension then fed to join()...
 
        # take each segmented list join them into a string, then join the list of strings into one string
        paragraphs = "\n\n".join([" ".join(seg_para) for seg_para in segged_list]).strip() 
        # because of " ".join() there's spaces before commas, so let's remove those
        paragraphs = reduce(lambda sum,char: sum+char if char not in [",","，"] else sum.strip()+char,paragraphs,"")

        item = window["-OUTPUT-"]
        item.update(paragraphs)
        # set the focus to the output widget and select the text to make copy/paste easy
        item.set_focus()
        item.Widget.tag_add('sel',1.0,float(len(paragraphs)))

window.close()