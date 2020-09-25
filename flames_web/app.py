from flask import Flask, render_template, request
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

    return flames(count_unique(name1, name2))


app = Flask(__name__)


@app.route("/")
def start():
    return render_template("start.html")


@app.route("/predict", methods=["POST"])
def predict():
    name1 = "no name given"
    name2 = "no name given"

    if request.method == "POST":
        name1 = request.form["yourname"]
        name2 = request.form["yourcrushname"]

    if name1 == "no name given" or name2 == "no name given":
        return render_template("name_blank.html")

    result = cal(name1, name2)
    if result == "f":
        return render_template("friend.html")
    elif result == "l":
        return render_template("love.html")
    elif result == "a":
        return render_template("affection.html")
    elif result == "m":
        return render_template("marriage.html")
    elif result == "e":
        return render_template("enemy.html")
    elif result == "s":
        return render_template("sibling.html")


if __name__ == "__main__":
    app.run(debug=True)
