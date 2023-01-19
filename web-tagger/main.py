import os, csv, json

from js import window, document, Blob
from pyodide.http import pyfetch
from pyodide import create_proxy
from pyodide.ffi.wrappers import set_timeout

from tree_labeller.create_task import create_task
from tree_labeller.label import label

LABELS = None
TASKS = None
ALREADY_DONE_TASKS = None
ITERATION = 1
INDEX = 0

def qs(selector):
    return document.querySelector(selector)

def el(tag, id=None, class_=None, text=None):
    e = document.createElement(tag)
    if id: e.id = e
    if class_: e.className = class_
    if text: e.innerText = text
    return e


def display_progress(text):
    qs('#loadingLabel').innerText = text
    qs('#loadingSpinner').classList.remove('d-none')

def hide_progress():
    qs('#loadingSpinner').classList.add('d-none')


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
    btn = el('button', text=label, class_=f"{className} m-1")
    btn.value = value
    btn.addEventListener("click", set_task_label_proxy)
    return btn


def display_task():
    task = TASKS[INDEX]
    qs('#taskForm').classList.remove('d-none')
    qs('#stats_progress_Task').innerText = f"{INDEX+1} / {len(TASKS)}"
    qs('#taskName').innerText = task['name']
    qs('#taskCategory').innerText = task['category'].replace(">", " » ")

    # Display Task Params
    params = ""
    for k, v in task.items():
        if k in ('label', 'category', 'name', 'id'): continue
        params += f'<li class="list-group-item text-muted">{k}: {v}</li>'
    qs('#taskParams').innerHTML = params

    # # Display Task Buttons
    predicted = set(task['label'].split('|'))
    predicted.discard('')
    other = (set(LABELS)|{'?','!'}) - predicted
    print(">>>>>>>>>>", predicted, other)

    qs('#taskButtons').innerHTML = ""
    for title, labels in [("Predicted", sorted(predicted)), ("Other", sorted(other))]:
        e = el("div", class_="text-center mb-3 mt-4")
        e.appendChild(el("h3", class_="d-inline me-2 align-middle", text=f"{title}:"))
        for value in labels:
            cls = 'primary' if title == 'Predicted' else 'secondary'
            if value == '?':
                label = 'Skip'
                cls = 'warning'
            elif value == '!':
                label = 'Reject'
                cls = 'warning'
            else:
                label = value.capitalize()

            btn = create_label_button(label, value, f'btn btn-{cls}' + ('' if title == 'Predicted' else ' btn-sm'))
            e.appendChild(btn)

        qs('#taskButtons').appendChild(e)


def set_statistics(stats):
    container = document.getElementById('statistics')
    container.innerHTML = ""

    for name, props in stats.items():
        h5 = document.createElement('h5')
        h5.innerText = name
        h5.className = 'text-light'
        container.appendChild(h5)
        dl = document.createElement('dl')
        dl.className = "row opacity-50 mb-3"
        html = ''
        for k, v in props.items():
            html += f'<dt class="col-sm-8">{k}:</dt><dd class="col-sm-4" id="stats_{name}_{k}">{v}</dd>'
        dl.innerHTML = html
        container.appendChild(dl)


def check_progress():
    with open(f"output/{ITERATION}-stats.json") as file:
        stats = json.load(file)
        print(stats)

        set_statistics({
            "progress": {
                "Iteration": ITERATION,
                "Task": "∞"
            },
            "labels": {
                "Provided": f"{stats['manual_labels']['n_allowed_labels']}",
                "Missing": f"{100*stats['progress.py']['missing']:.1f}%",
                "Covered": f"{100*stats['progress.py']['allowed_labels']:.1f}%",
            },
            "predictions": {
                "Univocal labels": f"{100*stats['progress.py']['univocal']:.1f}%",
                "Ambiguous labels": f"{100*stats['progress.py']['ambiguous']:.1f}%"
            }
        })
    

def load_tasks():
    global TASKS, INDEX, ALREADY_DONE_TASKS
    INDEX = 0
    print(">> Loading labels from:", f"output/{ITERATION}-to-verify.tsv")
    display_progress("Loading Tasks")

    label(dir="output/", sample=10)
    check_progress()

    if not os.path.exists(f"output/{ITERATION}-to-verify.tsv"):
        hide_progress()
        qs('#taskForm').classList.add('d-none')
        qs('#successForm').classList.remove('d-none')
        return 

    if os.path.exists(f"output/{ITERATION}-mapping.tsv"):
        qs('#downloadMapping').disabled = ''
    
    if os.path.exists(f"output/{ITERATION}-good.tsv"):
        qs('#downloadPredictedLabels').disabled = ''

    with open(f"output/{ITERATION}-to-verify.tsv") as file:
        tsv = csv.DictReader(file, delimiter="\t")
        TASKS = []
        ALREADY_DONE_TASKS = []
        for record in tsv:
            if record['label'] != '' and '|' not in record['label']:
                ALREADY_DONE_TASKS.append(record)
            else:
                TASKS.append(record)

    hide_progress()
    display_task()


def download_file(path, fname):
    if not os.path.exists(path):
        return 

    with open(path, encoding='utf-8') as file:
        content = file.read()

    blob = Blob.new([content], {type : 'application/text'})
    url = window.URL.createObjectURL(blob) 

    downloadLink = document.createElement("a");
    downloadLink.href = url;
    downloadLink.download = fname;
    document.body.appendChild(downloadLink);
    downloadLink.click();


def download_mapping(event):
    download_file(f"output/{ITERATION}-mapping.tsv", "mapping.tsv")


def download_predicted_labels(event):
    download_file(f"output/{ITERATION}-good.tsv", "predicted-labels.tsv")


async def create_task_fn(*args):
    global LABELS
    url = document.getElementById('input-url').value
    LABELS = document.getElementById('input-labels').value.split("|")

    print(">>", url, LABELS)

    response = await pyfetch(url=url, method="GET")
    with open("tree.yaml", "wb") as f:
        f.write(await response.bytes())

    print(os.getcwd(), os.path.exists("tree.yaml"), os.path.getsize("tree.yaml"))

    document.getElementById('input-form').classList.add('d-none')
    display_progress("Creating Task")

    def task():
        create_task(dir="output/", tree="tree.yaml", allowed_labels=LABELS)
        set_timeout(load_tasks, 100)
    
    set_timeout(task, 100)

qs("#createTaskBtn").addEventListener("click", create_proxy(create_task_fn))
qs("#downloadMapping").addEventListener('click', create_proxy(download_mapping))
qs("#downloadPredictedLabels").addEventListener('click', create_proxy(download_predicted_labels))