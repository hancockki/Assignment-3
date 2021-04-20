#Try these in a Python shell
sym_table = {}
sym_table["i"] = ["int", None]
sym_table["var1"] = ["float", None]

sym_table["i"][1] = 50
sym_table["var1"][1] = 10.75
sym_table
#{'i': ['int', 50], 'var1': ['float', 10.75]}


if "j" in sym_table:
    print("Yes, j has been defined.")
else:
    print("No, j has not been defined.")

sym_table.pop("i")
#['int', 50]
sym_table
#{'var1': ['float', 10.75]}