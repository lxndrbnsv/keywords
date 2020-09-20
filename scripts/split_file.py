lines_per_file = 100000
smallfile = None
with open("./text_files/keys.txt") as bigfile:
    for lineno, line in enumerate(bigfile):
        if lineno % lines_per_file == 0:
            if smallfile:
                smallfile.close()
            small_filename = "./small_files/small_file_{}.txt".format(
                lineno + lines_per_file
            )
            smallfile = open(small_filename, "w")
        smallfile.write(line)
    if smallfile:
        smallfile.close()
