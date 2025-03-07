from __future__ import division
import itertools
import random
from copy import deepcopy
from PIL import Image
import sqlite3
import ImageEdit
import io


def exam(topic, mark, subjectId, info):
    fields = ["Topic", "Marks"]ge

    print(topic, mark, subjectId)
    

    if info == "1":
        info_print = True
    else:
        info_print = False

    try:
        if len(topic) == 0:
            print("topic error")
            raise ValueError
        mark = int(mark) if mark != "" else mark

    except:
        print("error_exam")
        return

    mark_choice = mark
    query = ""
    if topic != None and topic != "":
        topic_mod = topic.copy()
        for h in range(len(topic_mod)):
            topic_mod[h] = f"'{topic_mod[h]}'"
        y = ", ".join(topic_mod)
        if query != "":
            y = f" AND Topic IN ({y})"
        else:
            y = f"Topic IN ({y})"

        query = query + y

    print("SQL Query: ", query)
    print("Validation Successfull")

    table_name = "Questions"
    if subjectId == "0606":
        table_name = "QuestionsAdd"

    db_dir = '/tmp/my-database.db'
    with sqlite3.connect(db_dir) as connection:
        print("SQLite connection successful")
        # Image, Topic, Marks
        command = f"SELECT Image, Topic, Marks, Year, Month, Paper, Variant FROM {table_name} WHERE {query}"
        cursor = connection.execute(command)
        data = cursor.fetchall()

    random.shuffle(data)

    data_topic = [[] for i in topic]

    for record in data:
        record = list(record)
        if record[4] == "m":
            month = "March"
        elif record[4] == "s":
            month = "May/June"
        elif record[4] == "w":
            month = "October/November"
        else:
            month = ""
        info_str = f"{month} {record[3]}/{record[5]}{record[6]}"
        record = record[:3]
        record.append(info_str)
        record = tuple(record)
        for j in range(len(topic)):
            if record[1] == topic[j]:
                data_topic[j].append(record)

    # For testing purposes as image data clutters the terminal
    """
    for i in range(len(data_topic)):
        for j in range(len(data_topic[i])):
            data_topic[i][j] = data_topic[i][j][1:]
    """

    def mins(list):
        min_set = {}
        for topic in data_topic:
            topic_name = topic[0][1]
            min_topic = [topic[i][2] for i in range(len(topic))]
            min_value = min(min_topic)
            min_set[topic_name] = min_value
        return min_set

    def subset_sum(list, target, combinations=[], index=0, sums=[]):
        x = list[index]
        x_marks = x[2]
        comb_copy = deepcopy(combinations)
        for i in range(len(comb_copy)):
            # [3,4,6]
            k = [mark[2] for mark in comb_copy[i]]
            k.append(x_marks)
            if sum(k) in sums:
                continue
            if 0 < sum(k) <= target:
                comb_copy[i].append(x)
                sums.append(sum(k))
        if index == 0 and x_marks <= target:
            comb_copy.append([x])
            sums.append(x_marks)
        comb_copy = [elem for elem in comb_copy if elem not in combinations]
        combinations.extend(comb_copy)
        index += 1
        if index == len(list):
            return combinations
        subset_sum(list, target, combinations, index, sums)
        return combinations

    min_set = mins(data_topic)
    # Call the function for each topic
    combinations = []
    for w in range(len(data_topic)):
        min_topic = min_set[data_topic[w][0][1]]
        min_value = sum(list(min_set.values())) - min_topic
        target = mark_choice - min_value
        if len(data_topic) > 7 and mark_choice > 120:
            target //= 3
        elif len(data_topic) > 4 and table_name == "Questions":
            target //= 3

        x = subset_sum(data_topic[w], target, combinations=[], sums=[])
        combinations.append(x)

    info_str_data = []  # This will store just the info_str for each question

    # 8 nested loops that run all different possibilities to add up to chosen sum
    skip = 0
    brk = False
    for topic in combinations:
        random.shuffle(topic)
    random.shuffle(combinations)
    for i in range(len(combinations)):
        for x in itertools.product(range(len(combinations[i])), repeat=len(combinations)):
            x = x[::-1]
            x = list(x)
            for k in range(len(x)):
                if x[k] >= len(combinations[k]):
                    x[k] = len(combinations[k]) - 1
            mark_sum = 0
            for t in range(len(combinations)):
                for ques in combinations[t][x[t]]:
                    mark_sum += ques[2]
            if mark_sum == mark_choice:
                img_list = []
                d = []
                for r in range(len(combinations)):
                    for ques in combinations[r][x[r]]:
                        img_list.append(ques[0])
                        d.append(ques[1:])
                        info_str_data.append(ques[3])

                print("Paper creation successful")

                brk = True
            if brk:
                break
        if brk:
            break

    for i in range(len(img_list)):
        img_list[i] = Image.open(io.BytesIO(img_list[i]))

    img_list.sort(key=lambda x: x.size[1])

    img_list = ImageEdit.add_numbers(img_list, info_str_data, info_print)
    abc = ImageEdit.new_img(img_list)
    final = []
    for image in abc:
        if image.height < 2000:
            final.append(ImageEdit.a4(image, 100, 0, 2000 - image.height, 0, (255, 255, 255)))
        else:
            final.append(image)

    print("Dimension adjustment successful")

    im1 = final[0]
    p = ImageEdit.add_tag(final)

    print("Tag addition successful")

    if p == None:
        return "Error"
    return p