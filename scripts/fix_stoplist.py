stop1 = []

with open("./text_files/stoplist_full.txt") as first_file:
    data1 = first_file.readlines()


print(len(data1))

for line in data1:
    if line not in stop1:
        stop1.append(line)

print(len(stop1))

for s in stop1:
    with open("./text_files/stoplist.txt", "a+") as text_file:
        text_file.writelines(s)
