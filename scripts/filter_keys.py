import os
import sys


minus_words = []

with open("./text_files/stoplist.txt") as stop_file:
    stop_data = stop_file.readlines()

for sd in stop_data:
    if sd.replace("\n", "") not in minus_words:
        minus_words.append(sd.replace("\n", ""))

dup = []

small_files = os.listdir("./small_files")

for file in small_files:
    file_path = "./small_files/" + file
    print(file_path)

    with open(file_path) as text_file:
        for idx, line in enumerate(text_file):
            sys.stdout.write("\r" + str(idx))
            sys.stdout.flush()
            try:
                if all(word not in line for word in minus_words):
                    with open(
                        "./small_files/filtered/"
                        + file.replace(".txt", "")
                        + "_filtered.txt",
                        "a+",
                    ) as results_file:
                        results_file.writelines(line)
                    dup.append(line)
                    if len(dup) > 1000:
                        dup = []
            except KeyboardInterrupt:
                print("Interrupted!")
                # Удаляем файл, если фильтрация не завершилась.
                # Завершаем скрипт.
                os.system(
                    "rm ./small_files/filtered/"
                    + file.replace(".txt", "")
                    + "_filtered.txt",
                )
                quit()

    # После фильтрации удаляем файл.
    os.system("rm " + file_path)
