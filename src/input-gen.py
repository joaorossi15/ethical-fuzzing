import yaml
import pandas as pd
import random
import json

def parse_csv(path: str):
    try:
        csv = pd.read_csv(path)
    except Exception as e:
        print(e)
    else:
        return csv

def read_yaml(path: str):
    with open(path, 'r') as stream:
        try:
            data_loaded = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            print(e)
        else:
            return data_loaded

def parse_message_sequence(csv):
    benign = read_yaml("data/r1/templates/benign.yaml")
    auth = read_yaml("data/r1/templates/authority.yaml")
    confidential = read_yaml("data/r1/templates/confidential.yaml")
    distractor = read_yaml("data/r1/templates/distractor.yaml")
    exfiltrate = read_yaml("data/r1/templates/exfiltrate.yaml")
    task = read_yaml("data/r1/templates/task.yaml")

    for row in csv.itertuples():
        message = row.message_sequence
        m = message.split("|")
        for i in range(len(m)):
            m[i] = m[i].split(";")
        for i in range(len(m)):
            match m[i][0].lower():
                case "confidential":
                    val = random.randint(0,2)
                    temp_dict = {"type": "confidential", "text": confidential[m[i][1]][val]["text"], "canary_cat": m[i][1]}
                    m[i][0] = temp_dict
                
                case "authority":
                    val = random.randint(0,4)
                    temp_dict = {"type": "authority", "text": auth["templates"][val]["text"]}
                    m[i][0] = temp_dict
                
                case "benign":
                    try:
                        temp = []
                        for _ in range(0,int(m[i][1])):
                            val = random.randint(0,8)
                            temp_dict = {"type": "benign", "text": benign["templates"][val]["text"]}
                            temp.append(temp_dict)
                        m[i][0] = temp
                    except:
                        val = random.randint(0,8)
                        temp_dict = {"type": "benign", "text": benign["templates"][val]["text"]}
                        m[i][0] = temp_dict
                
                case "distractor":
                    try:
                        temp = []
                        for _ in range(0,int(m[i][1])):
                            val = random.randint(0,3)
                            temp_dict = {"type": "distractor", "text": distractor["templates"][val]["text"]}
                            temp.append(temp_dict)
                        m[i][0] = temp
                    except:
                        val = random.randint(0,3)
                        temp_dict = {"type": "distractor", "text": distractor["templates"][val]["text"]}
                        m[i][0] = temp_dict


                case "exfiltrate":
                    val = random.randint(0,4)
                    if row.canary_type == "number":
                        temp_dict = {"type": "exfiltrate", "text": exfiltrate["template_number"][val]["text"]}
                        m[i][0] = temp_dict
                    else:
                        temp_dict = {"type": "exfiltrate", "text": exfiltrate["template_basic"][val]["text"]}
                        m[i][0] = temp_dict
                
                case "social_eng":
                    val = random.randint(0,4)
                    temp_dict = {"type": "social_eng", "text": social_eng["templates"][val]["text"]}
                    m[i][0] = temp_dict
                
                case "task":
                    val = random.randint(0,5)
                    temp_dict = {"type": "task", "text": task["templates"][val]["text"]}
                    m[i][0] = temp_dict
                
                case _:
                    pass
            m[i] = m[i][0]
        m = [item for e in m for item in (e if isinstance(e, list) else [e])]
        csv.loc[row.Index, "messages"] = json.dumps(m, ensure_ascii=False)
    return csv

csv = parse_csv("data/r1/seeds.csv")
social_eng = read_yaml("data/r1/templates/social_eng.yaml")
csv = parse_message_sequence(csv)
print(csv)
