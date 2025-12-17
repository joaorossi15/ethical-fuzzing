import yaml
import pandas as pd
import random

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
                    m[i][0] = confidential[m[i][1]][val]["text"]
                    m[i][0] = ";".join(m[i])
                
                case "authority":
                    val = random.randint(0,4)
                    m[i][0] = auth["templates"][val]["text"]
                
                case "benign":
                    try:
                        temp = []
                        for _ in range(0,int(m[i][1])):
                            val = random.randint(0,8)
                            temp.append(benign["templates"][val]["text"])
                        m[i][0] = "|".join(temp)
                    except:
                        val = random.randint(0,8)
                        m[i][0] = benign["templates"][val]["text"]
                
                case "distractor":
                    try:
                        temp = []
                        for j in range(0,int(m[i][1])):
                            val = random.randint(0,3)
                            temp[j] = distractor["templates"][val]["text"]
                        m[i][0] = "|".join(temp)
                    except:
                        val = random.randint(0,3)
                        m[i][0] = distractor["templates"][val]["text"]


                case "exfiltrate":
                    val = random.randint(0,4)
                    if row.canary_type == "number":
                        m[i][0] = exfiltrate["template_number"][val]["text"]
                    else:
                        m[i][0] = exfiltrate["template_basic"][val]["text"]
                
                case "social_eng":
                    val = random.randint(0,4)
                    m[i][0] = social_eng["templates"][val]["text"]
                
                case "task":
                    val = random.randint(0,5)
                    m[i][0] = task["templates"][val]["text"]
                
                case _:
                    pass
            m[i] = m[i][0]
        m = "|".join(m)
        csv.loc[row.Index, "message_sequence"] = m
        print(m)

csv = parse_csv("data/r1/seeds.csv")
social_eng = read_yaml("data/r1/templates/social_eng.yaml")
parse_message_sequence(csv)
