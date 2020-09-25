import PySimpleGUI as sg
from collections import Counter as C


def cal(name1, name2):
    def proper_format(input_string):
        if len(input_string) > 0:
            return [
                i for i in input_string.lower() if i in "abcdefghijklmnopqrstuvwxyz"
            ]
        else:
            exit()

    def count_unique(x, y):
        return len(list(((C(x) - C(y)) + (C(y) - C(x))).elements()))

    name1 = proper_format(name1)
    name2 = proper_format(name2)

    unique_number = count_unique(name1, name2)

    def flames(n):

        flames_string = [i for i in "flames"]

        while len(flames_string) > 1:
            length_flames_string = len(flames_string)
            if length_flames_string < unique_number:
                temp_length = unique_number % length_flames_string
                if temp_length == 0:
                    l1 = length_flames_string
                else:
                    l1 = temp_length
            else:
                l1 = unique_number
            flames_string.pop(l1 - 1)
            temp = [i for i in flames_string]
            flames_string.clear()
            if (l1 - 1) == 0 or (l1 - 1) == len(temp):
                flames_string = temp
            else:
                for i in range((l1 - 1), len(temp)):
                    flames_string.append(temp[i])
                for i in range(0, (l1 - 1)):
                    flames_string.append(temp[i])
        return str(flames_string[0])

    def flames_format(str):
        if str == "f":
            return "You two will be good friends"
        elif str == "l":
            return "Your crush loves you. Run to him"
        elif str == "a":
            return "Your crush shows affection with you"
        elif str == "m":
            return "You two are going to marry"
        elif str == "e":
            return "You two are enemy for each other"
        elif str == "s":
            return "You two are siblings with each other"
        else:
            return "There was an error in getting relationship! So it can be anything"

    return flames_format(flames(count_unique(name1, name2)))


sg.change_look_and_feel("ddd")  # Add a little color to your windows
# All the stuff inside your window. This is the PSG magic code compactor...
layout = [
    [sg.Text("This is FLAMES game to know your luck with your crush")],
    [sg.Text("Your name"), sg.InputText(key="name1", default_text="your name")],
    [
        sg.Text("Your crush name"),
        sg.InputText(key="name2", default_text="your crush name"),
    ],
    [
        sg.Button("Find out the relation"),
        sg.Cancel(button_text="Exit"),
        sg.Button("Clear the values"),
    ],
    [sg.Text("\t\t\t\t\t\t\tCreated By Akash")],
]

# Create the Window
window = sg.Window("FLAMES GAME", layout)
# Event Loop to process "events"
while True:
    event, values = window.read()
    if event == "EXIT" or event is None:
        break  # exit button clicked
    elif event == "Find out the relation":
        if (
            values["name1"] == "your name"
            or values["name2"] == "your crush name"
            or values["name1"] == ""
            or values["name2"] == ""
        ):
            sg.popup("Enter names to predict relationship or click Exit")
        else:
            sg.popup(cal(values["name1"], values["name2"]))
    elif event == "Clear the values":
        window["name1"].update("")
        window["name2"].update("")
    else:
        break


window.close()
