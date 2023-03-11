const THEMES = [
    "cerulean", "cosmo", "cyborg", "darkly", "flatly", "journal", "litera", "lumen", "lux",
    "materia", "minty", "morph", "pulse", "quartz", "sandstone", "simplex", "sketchy", "slate",
    "solar", "spacelab", "superhero", "united", "vapor", "yeti", "zephyr"
];

function toggleMenu() {
    document.getElementById('sidebarMenu').classList.toggle('minimized');
    document.getElementById('sm2').classList.toggle('minimized');
    document.getElementById('toggle-button').classList.toggle('swap-x');
}

function preloadSmallSample() {
    document.querySelector('#input-url').value = 'https://pawelkubiak.me/tree-labeller/demo/small.yaml'
    document.querySelector('#input-labels').value = 'Paper|Glass|Plastic|Metal|Organic|Mixed'
}

function preloadLargeSample() {
    document.querySelector('#input-url').value = 'https://raw.githubusercontent.com/dzieciou/tree-labeller/master/demo/marketpoint/frisco.yaml'
    document.querySelector('#input-labels').value = 'Alcohols|Beers|Vegetables'
}

function setTheme(){
    let theme = document.querySelector('#themesList').value;
    document.getElementById('theme').href = `https://cdnjs.cloudflare.com/ajax/libs/bootswatch/5.2.3/${theme}/bootstrap.min.css`
    localStorage.setItem('theme', theme);
}

for(let item of THEMES) {
    let option = document.createElement('option');
    option.value = option.innerText = item;
    document.querySelector('#themesList').appendChild(option);
}

document.querySelector('#themesList').value = localStorage.getItem('theme') || "united";
setTheme();