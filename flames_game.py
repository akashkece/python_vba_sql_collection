from collections import Counter as C

def main():
    def proper_format(input_string):
        if len(input_string) > 0:
            return [
                i for i in input_string.lower() if i in "abcdefghijklmnopqrstuvwxyz"
            ]
        else:
            print("You have to provide both names")
            exit()


    def count_unique(x, y):
        return len(list(((C(x) - C(y)) + (C(y) - C(x))).elements()))

    given_name1 = input("Enter your name: ")
    given_name2 = input("Enter your crush name: ")
    
    name1 = proper_format(given_name1)
    name2 = proper_format(given_name2)

    print("\n\n","-" * 40)
    print(f"Hi {given_name1}!. Let's see your luck with {given_name2}.\n")

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

    def flames_custom_result(i):
        if i == "f":
            print(f"Wow!\n{given_name2} is going to be very good friend with {given_name1}.\nBut it will not go any further between the two.\n", "-" * 40)    
        if i == "l":
            print(
                f"Oh my my! \nIt is a Match. \nIt is a Lovely Match. \n**********\n{given_name2} actually loves {given_name1}. \n***********\nLuck You!\n", "-" * 40
            )
        if i == "a":
            print(f"Good News!\n{given_name2} shows affection with {given_name1}.\nBut this is all.\n", "-" * 40)    
        if i == "m":
            print(
                f"Oh my my! \nIt is a Match. \nIt is a Perfect Match. \n**********\n{given_name2} is going to marry {given_name1}. \n***********\nYou are so lucky!\n", "-" * 40
            )
        if i == "e":
            print(f"Whaaat! \n{given_name2} is enemy of {given_name1}.\nStay Away, Do not complain later that I didn't warn you.\n", "-" * 40)
        if i == "s":
            print(f"Cute!\n{given_name2} is actually sibling of {given_name1}.\nWhat? You were not expecting this?\n", "-" * 40)               

    flames_custom_result(flames(count_unique(name1, name2)))
    value = input("If you want to run this again, type yes: ")
    if value == "yes" or value == "Yes" or value == "YES":
        main()


if __name__ == "__main__":
    main()
	
	
