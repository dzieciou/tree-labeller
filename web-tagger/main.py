import os, csv, json

from js import window, document, Blob
from pyodide.http import pyfetch
from pyodide import create_proxy

from tree_labeller.create_task import create_task
from tree_labeller.label import label

LABELS = None
TASKS = None
ALREADY_DONE_TASKS = None
ITERATION = 1
INDEX = 0

def save_results():
    global ITERATION
    with open(f"output/{ITERATION}-to-verify.tsv", "w") as file:
        writer = csv.DictWriter(file, fieldnames=list(TASKS[0].keys()), delimiter="\t")
        writer.writeheader()
        print(TASKS, ALREADY_DONE_TASKS)
        for record in TASKS:
            writer.writerow(record)
        for record in ALREADY_DONE_TASKS:
            writer.writerow(record)
    ITERATION += 1
    load_tasks()

def set_task_label(label):
    global INDEX
    TASKS[INDEX]['label'] = label
    INDEX += 1

    if INDEX < len(TASKS):
        display_task()
    else:
        save_results()

def set_task_label_fn(event):
    set_task_label(event.target.value)

set_task_label_proxy = create_proxy(set_task_label_fn)


def create_label_button(label, value, className):
    btn = document.createElement('button')
    btn.innerText = label
    btn.value = value
    btn.className = className + ' m-1'
    btn.addEventListener("click", set_task_label_proxy)
    document.getElementById('actions').appendChild(btn)


def display_task():
    task = TASKS[INDEX]
    document.getElementById('title').innerText = f"Task {INDEX+1} / {len(TASKS)}; Iteration #{ITERATION}"
    document.getElementById('task').classList.remove('d-none')
    document.getElementById('progress').classList.remove('d-none')

    params = ''
    
    for k, v in task.items():
        # if k == 'label': continue
        params += f"<li>{k}: {v}</li>"
    document.getElementById('params').innerHTML = params

    if task['label'] == '':
        labels = LABELS
    else:
        labels = task['label'].split('|')
    
    if len(labels) == 1:
        return set_task_label(labels[0])

    document.getElementById('actions').innerHTML = ''
    for label in labels:
        create_label_button(label, label, 'btn btn-success')
    
    create_label_button('Skip', '?', 'btn btn-warning')
    create_label_button('Reject', '!', 'btn btn-warning')


def check_progress():
    with open(f"output/{ITERATION}-stats.json") as file:
        stats = json.load(file)
        progress = stats['progress.py']
        output = '; '.join(f"<b>{k}:</b> {round(v,2) if isinstance(v,float) else v}" for k, v in progress.items())
        document.getElementById('progress').innerHTML = output

        print(stats)
    

def load_tasks():
    global TASKS, INDEX, ALREADY_DONE_TASKS
    INDEX = 0
    print(">> Loading labels from:", f"output/{ITERATION}-to-verify.tsv")

    label(dir="output/", sample=10)
    check_progress()

    if not os.path.exists(f"output/{ITERATION}-to-verify.tsv"):
        document.getElementById('task').innerHTML = '<h1>You are done 👏</h1>'
        return 

    with open(f"output/{ITERATION}-to-verify.tsv") as file:
        tsv = csv.DictReader(file, delimiter="\t")
        TASKS = []
        ALREADY_DONE_TASKS = []
        for record in tsv:
            if record['label'] != '' and '|' not in record['label']:
                ALREADY_DONE_TASKS.append(record)
            else:
                TASKS.append(record)
    display_task()


def download_mapping(event):
    with open(f"output/{ITERATION}-mapping.tsv", encoding='utf-8') as file:
        content = file.read()

    blob = Blob.new([content], {type : 'application/text'})
    url = window.URL.createObjectURL(blob) 
    window.location.assign(url)

download_mapping_proxy = create_proxy(download_mapping)

async def create_task_fn(*args):
    global LABELS
    print('hello', args)
    url = document.getElementById('input-url').value
    LABELS = document.getElementById('input-labels').value.split(",")

    print(">>", url, LABELS)

    response = await pyfetch(url=url, method="GET")
    with open("tree.yaml", "wb") as f:
        f.write(await response.bytes())

    print(os.getcwd(), os.path.exists("tree.yaml"), os.path.getsize("tree.yaml"))

    create_task(dir="output/", tree="tree.yaml", allowed_labels=LABELS)
    document.getElementById('input-form').classList.add('d-none')
    load_tasks()

function_proxy = create_proxy(create_task_fn)
document.getElementById("input-button").addEventListener("click", function_proxy)
document.getElementById("download").addEventListener('click', download_mapping_proxy)

