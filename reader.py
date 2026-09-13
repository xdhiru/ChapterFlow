from http.server import HTTPServer,BaseHTTPRequestHandler
from pathlib import Path
import json,mimetypes,urllib.parse,re,argparse,sys

ROOT=Path(__file__).parent.resolve()
IMAGE_EXTENSIONS={".png",".jpg",".jpeg",".webp",".gif",".bmp"}

def natural_key(path):
    return [int(x) if x.isdigit() else x for x in re.split(r"(\d+)",str(path).lower())]

def folder_sort_key(path):
    return (1,[]) if path.name.lower()=="epilogue" else (0,natural_key(path))

def get_images():
    images=[]
    # Check for direct images in ROOT
    root_files=[p for p in ROOT.iterdir()
                if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]
    if root_files:
        root_files.sort(key=lambda p:(0 if p.stem.lower() in ("[cover]","cover") else 1,natural_key(p.name)))
        group_name = ROOT.name if ROOT.name else "Main"
        for f in root_files:
            images.append({
                "day":group_name,
                "name":f.name,
                "url":"/"+urllib.parse.quote(str(f.relative_to(ROOT)).replace("\\","/"))
            })

    folders=sorted((p for p in ROOT.iterdir() if p.is_dir()),key=folder_sort_key)
    for folder in folders:
        files=[p for p in folder.iterdir()
               if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]
        files.sort(key=lambda p:(0 if p.stem.lower() in ("[cover]","cover") else 1,natural_key(p.name)))
        for f in files:
            images.append({
                "day":folder.name,
                "name":f.name,
                "url":"/"+urllib.parse.quote(str(f.relative_to(ROOT)).replace("\\","/"))
            })
    return images


HTML=r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>ChapterFlow</title>

<style>
*{box-sizing:border-box}

html,body{
    margin:0;
    width:100%;
    height:100%;
    background:#000;
    overflow:hidden;
    font-family:Arial,sans-serif;
    overscroll-behavior:none;
}

body{
    display:flex;
    align-items:center;
    justify-content:center;
}

/* =========================
   Reader & Viewer
   ========================= */

#viewer{
    position:fixed;
    inset:0;
    width:100vw;
    height:100vh;
    overflow:auto;
    display:flex;
    background:#000;
    overscroll-behavior:contain;
    scrollbar-width:thin;
    scrollbar-color:rgba(255,255,255,.25) transparent;
}

#viewer::-webkit-scrollbar{
    width:8px;
    height:8px;
}
#viewer::-webkit-scrollbar-thumb{
    background:rgba(255,255,255,.25);
    border-radius:4px;
}
#viewer::-webkit-scrollbar-thumb:hover{
    background:rgba(255,255,255,.45);
}
#viewer::-webkit-scrollbar-track{
    background:transparent;
}

#image-wrapper{
    margin:auto;
    display:flex;
    align-items:center;
    justify-content:center;
    position:relative;
    min-width:min-content;
    min-height:min-content;
}

#image{
    display:block;
    user-select:none;
    -webkit-user-select:none;
    -webkit-user-drag:none;
    cursor:pointer;
}

/* View Modes */
#viewer.mode-fit-screen{
    overflow:hidden;
}

#viewer.mode-fit-screen #image-wrapper{
    margin:auto;
    width:100vw;
    height:100vh;
}

#viewer.mode-fit-screen #image{
    width:100vw;
    height:100vh;
    max-width:100vw;
    max-height:100vh;
    object-fit:contain;
}

#viewer.mode-fit-width{
    overflow-y:auto;
    overflow-x:hidden;
}

#viewer.mode-fit-width #image-wrapper{
    margin:0 auto;
    width:100%;
    max-width:100vw;
}

#viewer.mode-fit-width #image{
    width:100%;
    max-width:100vw;
    height:auto;
    margin:0 auto;
    object-fit:initial;
}

#viewer.mode-fit-height{
    overflow-x:auto;
    overflow-y:hidden;
}

#viewer.mode-fit-height #image-wrapper{
    margin:auto;
    height:100vh;
}

#viewer.mode-fit-height #image{
    height:100vh;
    width:auto;
    object-fit:contain;
}

#viewer.mode-custom{
    overflow:auto;
}

#viewer.mode-custom #image-wrapper{
    margin:auto;
}

#viewer.mode-custom #image{
    object-fit:initial;
}

#viewer.is-dragging{
    cursor:grab !important;
}
#viewer.is-dragging #image{
    cursor:grabbing !important;
}


/* =========================
   Fullscreen gesture zones
   ========================= */

#fullscreen-gesture{
    display:none;
    position:fixed;
    inset:0;
    z-index:12;
    touch-action:none;
    cursor:pointer;
}

body.fullscreen #fullscreen-gesture{
    display:block;
}


/* =========================
   Normal edge trigger
   ========================= */

#edge{
    position:fixed;
    left:0;
    top:0;
    width:18px;
    height:100vh;
    z-index:20;
}


/* =========================
   Sidebar
   ========================= */

#sidebar{
    position:fixed;
    left:0;
    top:0;
    bottom:0;
    width:300px;
    max-width:85vw;
    background:rgba(18,18,18,.97);
    color:#fff;
    transform:translateX(-100%);
    transition:transform .18s ease;
    z-index:40;
    overflow-y:auto;
    overflow-x:hidden;
    box-shadow:4px 0 20px rgba(0,0,0,.5);
    padding:55px 8px 20px;
    touch-action:pan-y;
}

#sidebar.open{
    transform:translateX(0);
}


/* Fixed sidebar header */

#sidebar-header{
    position:absolute;
    left:0;
    top:0;
    width:100%;
    height:48px;
    display:flex;
    align-items:center;
    background:#121212;
    border-bottom:1px solid rgba(255,255,255,.08);
    z-index:10;
}

#sidebar-close{
    width:44px;
    height:40px;
    margin-left:4px;
    border:0;
    background:transparent;
    color:#ddd;
    font-size:24px;
    line-height:1;
    cursor:pointer;
}

#sidebar-close:hover{
    color:#fff;
    background:#292929;
    border-radius:5px;
}

#sidebar-title{
    font-size:15px;
    font-weight:bold;
    color:#ddd;
    margin-left:4px;
}

#sidebar-direction{
    display:flex;
    flex-direction:column;
    gap:6px;
    padding:9px 10px;
    margin:6px 0 12px;
    background:#1e1e1e;
    border-radius:6px;
    border:1px solid rgba(255,255,255,.08);
}

.dir-label{
    font-size:11px;
    color:#888;
    font-weight:bold;
    text-transform:uppercase;
    letter-spacing:0.5px;
}

.dir-buttons{
    display:flex;
    gap:6px;
}

.dir-btn{
    flex:1;
    text-align:center;
    padding:6px 4px;
    font-size:11px;
    font-weight:600;
    border:1px solid rgba(255,255,255,.12);
    border-radius:4px;
    background:#2a2a2a;
    color:#aaa;
    cursor:pointer;
    transition:all .15s ease;
    white-space:nowrap;
}

.dir-btn:hover{
    color:#fff;
    background:#383838;
}

.dir-btn.active{
    background:#3b5ccc;
    color:#fff;
    border-color:#5c7cfa;
}


/* =========================
   Days
   ========================= */

.day{
    margin-bottom:8px;
}

.day-title{
    font-size:14px;
    font-weight:bold;
    color:#aaa;
    padding:8px 10px;
    position:sticky;
    top:0;
    background:#121212;
    z-index:2;
}


/* =========================
   Pages
   ========================= */

.page{
    display:flex;
    align-items:center;
    width:100%;
    border:0;
    background:transparent;
    color:#bbb;
    padding:7px 10px;
    margin:1px 0;
    border-radius:5px;
    text-align:left;
    cursor:pointer;
    font-size:13px;
}

.page:hover{
    background:#292929;
    color:#fff;
}

.page.current{
    background:#3b5ccc;
    color:#fff;
}

.page-number{
    width:30px;
    flex-shrink:0;
    color:#777;
}

.page.current .page-number{
    color:#dce3ff;
}

.page-name{
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
}

#sidebar-hint{
    color:#666;
    font-size:11px;
    padding:12px 10px 0;
}


/* =========================
   Swipe hint
   ========================= */

#swipe-hint{
    position:fixed;
    left:50%;
    bottom:18px;
    transform:translateX(-50%);
    color:rgba(255,255,255,.35);
    font-size:12px;
    pointer-events:none;
    z-index:10;
    opacity:0;
    transition:opacity .3s;
}

#swipe-hint.show{
    opacity:1;
}


/* =========================
   Zoom Controls Widget
   ========================= */

#zoom-widget{
    position:fixed;
    right:14px;
    bottom:54px;
    display:flex;
    align-items:center;
    background:rgba(26,26,26,.88);
    border:1px solid rgba(255,255,255,.16);
    border-radius:6px;
    padding:3px 4px;
    gap:3px;
    z-index:35;
    backdrop-filter:blur(8px);
    -webkit-backdrop-filter:blur(8px);
    user-select:none;
    -webkit-user-select:none;
    box-shadow:0 4px 16px rgba(0,0,0,.45);
    transition:opacity .25s ease, transform .1s;
}

.zoom-btn{
    border:none;
    background:transparent;
    color:#ccc;
    font-size:14px;
    font-weight:bold;
    padding:4px 8px;
    border-radius:4px;
    cursor:pointer;
    display:inline-flex;
    align-items:center;
    justify-content:center;
    transition:all .15s ease;
    line-height:1;
    font-family:inherit;
}

.zoom-btn:hover{
    background:rgba(255,255,255,.15);
    color:#fff;
}

.zoom-btn:active{
    transform:scale(0.92);
}

.zoom-level-badge{
    font-size:11px;
    font-weight:600;
    min-width:48px;
    padding:4px 6px;
    text-align:center;
    color:#ddd;
    background:rgba(255,255,255,.07);
    border-radius:4px;
    letter-spacing:0.3px;
}

.zoom-level-badge:hover{
    background:rgba(255,255,255,.18);
    color:#fff;
}

#zoom-lock-btn{
    font-size:11px;
    padding:4px 6px;
    opacity:0.65;
}

#zoom-lock-btn.active{
    opacity:1;
    color:#74c0fc;
    background:rgba(59,92,204,.35);
}


/* =========================
   Fullscreen button
   ========================= */

#fullscreen-btn{
    position:fixed;
    right:14px;
    bottom:14px;
    padding:8px 12px;
    background:rgba(30,30,30,.85);
    color:#ddd;
    border:1px solid rgba(255,255,255,.15);
    border-radius:6px;
    font-size:12px;
    cursor:pointer;
    z-index:35;
    user-select:none;
    -webkit-user-select:none;
    backdrop-filter:blur(8px);
    -webkit-backdrop-filter:blur(8px);
    transition:background .15s, opacity .25s ease, transform .1s;
}

#fullscreen-btn:hover{
    background:rgba(50,50,50,.95);
    color:#fff;
}


/* =========================
   Fullscreen UI hiding
   ========================= */

body.fullscreen-ui-hidden #fullscreen-btn,
body.fullscreen-ui-hidden #zoom-widget{
    opacity:0;
    pointer-events:none;
}

body.fullscreen-ui-hidden #sidebar{
    pointer-events:none;
}


/* =========================
   Mobile
   ========================= */

@media(max-width:600px){

    #edge{
        width:12px;
    }

    #sidebar{
        width:280px;
        padding-top:55px;
    }

    .page{
        padding:9px 10px;
        font-size:13px;
    }

    #swipe-hint{
        display:block;
    }

    #zoom-widget{
        right:10px;
        bottom:46px;
        padding:2px 3px;
        gap:2px;
    }

    .zoom-btn{
        padding:3px 6px;
        font-size:12px;
    }

    .zoom-level-badge{
        min-width:42px;
        font-size:10px;
        padding:3px 4px;
    }

    #fullscreen-btn{
        right:10px;
        bottom:10px;
        font-size:11px;
        padding:7px 11px;
    }
}

@media(min-width:601px){
    #swipe-hint{
        display:none;
    }
}
</style>
</head>

<body>

<div id="viewer" class="mode-fit-screen">
    <div id="image-wrapper">
        <img id="image" draggable="false">
    </div>
</div>

<div id="fullscreen-gesture"></div>

<div id="edge"></div>

<div id="swipe-hint">
    ← Swipe to navigate →
</div>

<div id="zoom-widget">
    <button id="zoom-out-btn" class="zoom-btn" type="button" title="Zoom Out (-)">−</button>
    <button id="zoom-level-btn" class="zoom-btn zoom-level-badge" type="button" title="Zoom Level / Mode (Click to cycle)">Fit S</button>
    <button id="zoom-in-btn" class="zoom-btn" type="button" title="Zoom In (+)">+</button>
    <button id="zoom-lock-btn" class="zoom-btn active" type="button" title="Maintain Zoom across pages: ON">🔒</button>
</div>

<button id="fullscreen-btn">
    Go Fullscreen
</button>


<div id="sidebar">

    <div id="sidebar-header">
        <button id="sidebar-close" aria-label="Close sidebar">×</button>
        <div id="sidebar-title">ChapterFlow</div>
    </div>

    <div id="sidebar-direction">
        <span class="dir-label">Reading Direction</span>
        <div class="dir-buttons">
            <button id="dir-ltr" class="dir-btn" type="button" title="Standard: Left to Right (Notes, Books & Documents)">Left to Right</button>
            <button id="dir-rtl" class="dir-btn" type="button" title="Manga & Comics: Right to Left">Right to Left</button>
        </div>
    </div>

    <div id="tree"></div>

    <div id="sidebar-hint">
        ← / → to navigate
    </div>

</div>


<script>

let images=[];
let index=0;
let closeTimer=null;
let hideUITimer=null;

const image=document.getElementById("image");
const viewer=document.getElementById("viewer");
const imageWrapper=document.getElementById("image-wrapper");
const sidebar=document.getElementById("sidebar");
const edge=document.getElementById("edge");
const tree=document.getElementById("tree");
const swipeHint=document.getElementById("swipe-hint");
const fullscreenBtn=document.getElementById("fullscreen-btn");
const fullscreenGesture=document.getElementById("fullscreen-gesture");
const sidebarClose=document.getElementById("sidebar-close");
const dirLtrBtn=document.getElementById("dir-ltr");
const dirRtlBtn=document.getElementById("dir-rtl");
const zoomWidget=document.getElementById("zoom-widget");
const zoomOutBtn=document.getElementById("zoom-out-btn");
const zoomLevelBtn=document.getElementById("zoom-level-btn");
const zoomInBtn=document.getElementById("zoom-in-btn");
const zoomLockBtn=document.getElementById("zoom-lock-btn");

let readingDirection=localStorage.getItem("chapterflow_dir")||"ltr";

function setReadingDirection(dir){
    readingDirection=dir;
    localStorage.setItem("chapterflow_dir",dir);
    if(dirLtrBtn) dirLtrBtn.classList.toggle("active",dir==="ltr");
    if(dirRtlBtn) dirRtlBtn.classList.toggle("active",dir==="rtl");
}

if(dirLtrBtn) dirLtrBtn.onclick=()=>setReadingDirection("ltr");
if(dirRtlBtn) dirRtlBtn.onclick=()=>setReadingDirection("rtl");
setReadingDirection(readingDirection);


/* =========================
   Zoom & View Modes
   ========================= */

let viewMode=localStorage.getItem("chapterflow_view_mode")||"fit-screen";
let zoomScale=parseFloat(localStorage.getItem("chapterflow_zoom_scale"))||1.0;
let maintainZoom=localStorage.getItem("chapterflow_maintain_zoom")!=="false";
let scrollTargetOnLoad=null;
let dragDistance=0;
let isPanning=false;
let panStartX=0;
let panStartY=0;
let panScrollLeft=0;
let panScrollTop=0;

function updateZoomUI(){
    if(!zoomLevelBtn)return;
    if(viewMode==="fit-screen"){
        zoomLevelBtn.textContent="Fit S";
        zoomLevelBtn.title="Mode: Fit Screen. Click to toggle Fit Width";
    }else if(viewMode==="fit-width"){
        zoomLevelBtn.textContent="Fit W";
        zoomLevelBtn.title="Mode: Fit Width (Vertical Scroll). Click to toggle 100%";
    }else{
        zoomLevelBtn.textContent=Math.round(zoomScale*100)+"%";
        zoomLevelBtn.title=`Zoom: ${Math.round(zoomScale*100)}%. Click to toggle Fit Screen`;
    }

    if(zoomLockBtn){
        zoomLockBtn.classList.toggle("active",maintainZoom);
        zoomLockBtn.title=maintainZoom?"Maintain Zoom across pages: ON":"Maintain Zoom across pages: OFF";
    }
}

function applyZoom(){
    viewer.className="mode-"+viewMode;

    if(viewMode==="fit-screen"||viewMode==="fit-width"||viewMode==="fit-height"){
        image.style.width="";
        image.style.maxWidth="";
        image.style.height="";
        image.style.maxHeight="";
    }else if(viewMode==="custom"){
        const baseWidth=image.naturalWidth||window.innerWidth;
        image.style.width=Math.round(baseWidth*zoomScale)+"px";
        image.style.maxWidth="none";
        image.style.height="auto";
        image.style.maxHeight="none";
    }

    updateZoomUI();

    if(maintainZoom){
        localStorage.setItem("chapterflow_view_mode",viewMode);
        localStorage.setItem("chapterflow_zoom_scale",zoomScale.toString());
    }
    localStorage.setItem("chapterflow_maintain_zoom",maintainZoom.toString());
}

function setViewMode(mode){
    viewMode=mode;
    applyZoom();
}

function cycleZoomMode(){
    if(viewMode==="fit-screen"){
        setViewMode("fit-width");
    }else if(viewMode==="fit-width"){
        zoomScale=1.0;
        setViewMode("custom");
    }else if(viewMode==="custom" && zoomScale<1.4){
        zoomScale=1.5;
        setViewMode("custom");
    }else{
        setViewMode("fit-screen");
    }
}

function zoomIn(){
    if(viewMode==="fit-screen"||viewMode==="fit-width"){
        const renderedRatio=image.clientWidth/(image.naturalWidth||image.clientWidth||1);
        zoomScale=Math.min(5.0,Math.round((Math.max(1.0,renderedRatio)*1.25)*10)/10);
        setViewMode("custom");
    }else{
        zoomScale=Math.min(5.0,Math.round((zoomScale+0.2)*100)/100);
        applyZoom();
    }
}

function zoomOut(){
    if(viewMode==="fit-screen"){
        zoomScale=0.75;
        setViewMode("custom");
    }else if(viewMode==="fit-width"){
        setViewMode("fit-screen");
    }else{
        if(zoomScale<=0.45){
            setViewMode("fit-screen");
        }else{
            zoomScale=Math.max(0.25,Math.round((zoomScale-0.2)*100)/100);
            applyZoom();
        }
    }
}

function zoomAtPoint(clientX,clientY,factor){
    const rect=image.getBoundingClientRect();
    const offsetX=clientX-rect.left;
    const offsetY=clientY-rect.top;
    const ratioX=rect.width>0?offsetX/rect.width:0.5;
    const ratioY=rect.height>0?offsetY/rect.height:0.5;

    if(viewMode!=="custom"){
        const renderedRatio=image.clientWidth/(image.naturalWidth||image.clientWidth||1);
        zoomScale=Math.max(0.25,Math.min(5.0,renderedRatio*factor));
        viewMode="custom";
    }else{
        zoomScale=Math.max(0.25,Math.min(5.0,zoomScale*factor));
    }

    applyZoom();

    requestAnimationFrame(()=>{
        const newRect=image.getBoundingClientRect();
        viewer.scrollLeft=(newRect.width*ratioX)-(clientX-viewer.getBoundingClientRect().left);
        viewer.scrollTop=(newRect.height*ratioY)-(clientY-viewer.getBoundingClientRect().top);
    });
}

function toggleMaintainZoom(){
    maintainZoom=!maintainZoom;
    updateZoomUI();
    localStorage.setItem("chapterflow_maintain_zoom",maintainZoom.toString());
}

image.onload=()=>{
    // Auto-detect long vertical strip on initial view if no saved preference
    if(!localStorage.getItem("chapterflow_view_mode")){
        if(image.naturalHeight/image.naturalWidth>1.8){
            viewMode="fit-width";
            applyZoom();
        }
    }

    if(viewMode==="custom"){
        applyZoom();
    }

    if(scrollTargetOnLoad==="bottom"){
        viewer.scrollTop=viewer.scrollHeight;
        scrollTargetOnLoad=null;
    }else if(scrollTargetOnLoad==="top"){
        viewer.scrollTop=0;
        scrollTargetOnLoad=null;
    }
};


/* =========================
   Load
   ========================= */

async function load(){

    images=await fetch("/images").then(r=>r.json());

    const p=parseInt(
        new URLSearchParams(location.search).get("page")
    );

    index=Number.isFinite(p)?p:0;

    index=Math.max(
        0,
        Math.min(index,images.length-1)
    );

    buildTree();
    show();
}


/* =========================
   Sidebar tree
   ========================= */

function buildTree(){

    tree.innerHTML="";

    let currentDay=null;
    let dayElement=null;
    let pageNumber=0;

    images.forEach((item,i)=>{

        if(item.day!==currentDay){

            currentDay=item.day;

            dayElement=document.createElement("div");
            dayElement.className="day";

            const title=document.createElement("div");

            title.className="day-title";
            title.textContent=item.day;

            dayElement.appendChild(title);
            tree.appendChild(dayElement);

            pageNumber=0;
        }

        const button=document.createElement("button");

        button.className="page";
        button.dataset.index=i;

        const number=document.createElement("span");

        number.className="page-number";
        number.textContent=pageNumber+1;

        const name=document.createElement("span");

        name.className="page-name";
        name.textContent=item.name;

        button.append(number,name);

        button.onclick=()=>{

            index=i;
            show();
            closeSidebar();

        };

        dayElement.appendChild(button);

        pageNumber++;
    });
}


/* =========================
   Show page
   ========================= */

function preloadNearby(){
    const ahead=2;
    const behind=1;
    for(let i=1;i<=ahead;i++){
        if(index+i<images.length){
            const img=new Image();
            img.src=images[index+i].url;
        }
    }
    for(let i=1;i<=behind;i++){
        if(index-i>=0){
            const img=new Image();
            img.src=images[index-i].url;
        }
    }
}

function show(){

    if(!images.length)return;

    image.src=images[index].url;

    history.replaceState(
        null,
        "",
        "?page="+index
    );

    updateSidebar();
    preloadNearby();

    if(!maintainZoom){
        viewMode="fit-screen";
    }
    applyZoom();
}


/* =========================
   Sidebar current page
   ========================= */

function updateSidebar(){

    document
        .querySelectorAll(".page")
        .forEach(b=>b.classList.remove("current"));

    const current=document.querySelector(
        `.page[data-index="${index}"]`
    );

    if(current){

        current.classList.add("current");

        if(sidebar.classList.contains("open")){

            current.scrollIntoView({
                block:"nearest"
            });

        }
    }
}


/* =========================
   Navigation
   ========================= */

function next(){

    if(index<images.length-1){

        index++;
        scrollTargetOnLoad="top";
        show();
        viewer.scrollTop=0;
        viewer.scrollLeft=0;

    }
}

function previous(){

    if(index>0){

        index--;
        scrollTargetOnLoad=(viewMode==="fit-width"||viewMode==="custom")?"bottom":"top";
        show();
        if(viewMode==="fit-width"||viewMode==="custom"){
            requestAnimationFrame(()=>{
                viewer.scrollTop=viewer.scrollHeight;
            });
        }else{
            viewer.scrollTop=0;
            viewer.scrollLeft=0;
        }

    }
}


/* =========================
   Fullscreen
   ========================= */

function isFullscreen(){

    return !!document.fullscreenElement;
}

async function toggleFullscreen(){

    try{

        if(!isFullscreen()){

            await document.documentElement.requestFullscreen?.();

        }else{

            await document.exitFullscreen?.();

        }

    }catch(err){

        console.log("Fullscreen error:",err);

    }
}


/* =========================
   Fullscreen UI
   ========================= */

function revealFullscreenUI(){

    if(!isFullscreen())return;

    document.body.classList.remove(
        "fullscreen-ui-hidden"
    );

    clearTimeout(hideUITimer);

    /*
       Keep UI visible for 4 seconds.
    */
    hideUITimer=setTimeout(()=>{

        if(
            isFullscreen() &&
            !sidebar.classList.contains("open")
        ){

            document.body.classList.add(
                "fullscreen-ui-hidden"
            );

        }

    },4000);
}

function hideFullscreenUI(){

    if(
        isFullscreen() &&
        !sidebar.classList.contains("open")
    ){

        document.body.classList.add(
            "fullscreen-ui-hidden"
        );

    }
}


/* =========================
   Fullscreen state
   ========================= */

function updateFullscreenBtnText(){
    if(isFullscreen()){
        fullscreenBtn.textContent="Exit Fullscreen";
    }else{
        fullscreenBtn.textContent="Go Fullscreen";
    }
}

function onFullscreenChange(){

    if(isFullscreen()){

        document.body.classList.add("fullscreen");

        document.body.classList.add(
            "fullscreen-ui-hidden"
        );

    }else{

        document.body.classList.remove("fullscreen");

        document.body.classList.remove(
            "fullscreen-ui-hidden"
        );

        closeSidebar();

    }

    updateFullscreenBtnText();
}

document.addEventListener("fullscreenchange",onFullscreenChange);
document.addEventListener("webkitfullscreenchange",onFullscreenChange);


/* =========================
   Keyboard
   ========================= */

document.addEventListener("keydown",e=>{

    if(e.key==="+"||e.key==="="){
        e.preventDefault();
        zoomIn();
        return;
    }

    if(e.key==="-"||e.key==="_"){
        e.preventDefault();
        zoomOut();
        return;
    }

    if(e.key==="0"){
        e.preventDefault();
        setViewMode("fit-screen");
        return;
    }

    if(e.key.toLowerCase()==="w"){
        e.preventDefault();
        cycleZoomMode();
        return;
    }

    if(e.key.toLowerCase()==="l"){
        e.preventDefault();
        toggleMaintainZoom();
        return;
    }

    if(e.key==="ArrowDown"){
        if(viewer.scrollHeight>viewer.clientHeight){
            viewer.scrollBy({top:120,behavior:"smooth"});
            e.preventDefault();
            return;
        }
    }

    if(e.key==="ArrowUp"){
        if(viewer.scrollHeight>viewer.clientHeight){
            viewer.scrollBy({top:-120,behavior:"smooth"});
            e.preventDefault();
            return;
        }
    }

    if(e.key==="PageDown"||e.key===" "){
        e.preventDefault();
        if(viewer.scrollHeight>viewer.clientHeight && viewer.scrollTop+viewer.clientHeight<viewer.scrollHeight-15){
            viewer.scrollBy({top:viewer.clientHeight*0.85,behavior:"smooth"});
        }else{
            next();
        }
        return;
    }

    if(e.key==="PageUp"){
        e.preventDefault();
        if(viewer.scrollHeight>viewer.clientHeight && viewer.scrollTop>15){
            viewer.scrollBy({top:-viewer.clientHeight*0.85,behavior:"smooth"});
        }else{
            previous();
        }
        return;
    }

    if(e.key==="ArrowRight"){
        e.preventDefault();
        next();
        return;
    }

    if(e.key==="ArrowLeft"){
        e.preventDefault();
        previous();
        return;
    }

    if(e.key==="Home"){
        index=0;
        show();
        return;
    }

    if(e.key==="End"){
        index=images.length-1;
        show();
        return;
    }

    if(e.key.toLowerCase()==="f"){
        e.preventDefault();
        toggleFullscreen();
        return;
    }

});


/* ==================================================
   FULLSCREEN TOUCH GESTURES
   ==================================================

   LEFT 35%  = next (tap or swipe right)
   MIDDLE 30% = tap to reveal UI/sidebar
   RIGHT 35% = previous (tap or swipe left)
   ================================================== */

let fsStartX=0;
let fsStartY=0;
let fsLastY=0;
let fsTracking=false;
let lastTouchTime=0;

const SWIPE_THRESHOLD=50;
const VERTICAL_LIMIT=100;

fullscreenGesture.addEventListener(
    "touchstart",
    e=>{

        lastTouchTime=Date.now();
        if(!isFullscreen())return;

        const t=e.changedTouches[0];

        fsStartX=t.clientX;
        fsStartY=t.clientY;
        fsLastY=t.clientY;
        fsTracking=true;

    },
    {passive:false}
);


fullscreenGesture.addEventListener(
    "touchmove",
    e=>{

        if(!isFullscreen()||!fsTracking)return;

        const t=e.changedTouches[0];
        const dx=t.clientX-fsStartX;
        const dy=t.clientY-fsStartY;

        // Allow vertical drag scrolling on tall pages in fullscreen
        if(Math.abs(dy)>Math.abs(dx) && viewer.scrollHeight>viewer.clientHeight){
            viewer.scrollTop -= (t.clientY - fsLastY);
            fsLastY = t.clientY;
            e.preventDefault();
            return;
        }

        fsLastY = t.clientY;
        e.preventDefault();

    },
    {passive:false}
);


fullscreenGesture.addEventListener(
    "touchend",
    e=>{

        lastTouchTime=Date.now();
        if(!isFullscreen()||!fsTracking)return;

        const t=e.changedTouches[0];

        const dx=t.clientX-fsStartX;
        const dy=t.clientY-fsStartY;

        const width=window.innerWidth;
        const x=fsStartX;

        fsTracking=false;

        // If user scrolled vertically in fullscreen, don't trigger horizontal navigation
        if(Math.abs(dy)>=VERTICAL_LIMIT && viewer.scrollHeight>viewer.clientHeight){
            return;
        }

        const isMiddle=
            x>=width*.35 &&
            x<=width*.65;

        /*
           ==========================
           MIDDLE 30%
           ==========================
           Tap = reveal controls/sidebar
        */
        if(isMiddle){

            if(
                Math.abs(dx)<SWIPE_THRESHOLD &&
                Math.abs(dy)<VERTICAL_LIMIT
            ){

                revealFullscreenUI();
                openSidebar();

            }

            return;
        }


        /*
           ==========================
           OUTER 70% (LEFT 35% + RIGHT 35%)
           ==========================
           LTR (Notes/Books):
             - Swipe LEFT  → next, Swipe RIGHT → previous
             - Tap Right   → next, Tap Left    → previous
           RTL (Manga):
             - Swipe RIGHT → next, Swipe LEFT  → previous
             - Tap Left    → next, Tap Right   → previous
        */

        const isLeftZone = x < width * 0.35;
        const isRightZone = x > width * 0.65;

        // Clear horizontal swipe?
        if(
            Math.abs(dx)>=SWIPE_THRESHOLD &&
            Math.abs(dy)<=VERTICAL_LIMIT &&
            Math.abs(dy)<=Math.abs(dx)
        ){

            const isSwipeNext = (readingDirection === "ltr") ? (dx < 0) : (dx > 0);
            if(isSwipeNext)
                next();
            else
                previous();

            return;
        }

        // Tap (small movement) in outer zones
        if(
            Math.abs(dx)<SWIPE_THRESHOLD &&
            Math.abs(dy)<VERTICAL_LIMIT
        ){

            const isNextTap = (readingDirection === "ltr") ? isRightZone : isLeftZone;
            if(isNextTap){
                next();
            }else{
                previous();
            }

            return;
        }

    },
    {passive:false}
);


fullscreenGesture.addEventListener(
    "touchcancel",
    ()=>{
        fsTracking=false;
    },
    {passive:true}
);


/* ==================================================
   DRAG-TO-PAN, WHEEL ZOOM & CLICK NAVIGATION
   ================================================== */

viewer.addEventListener("mousedown", e => {
    if(e.button !== 0) return;
    if(e.target.closest("#sidebar, #fullscreen-btn, #zoom-widget, #sidebar-close, #edge")) return;

    isPanning = true;
    dragDistance = 0;
    panStartX = e.clientX;
    panStartY = e.clientY;
    panScrollLeft = viewer.scrollLeft;
    panScrollTop = viewer.scrollTop;
});

window.addEventListener("mousemove", e => {
    if(isFullscreen()){
        revealFullscreenUI();
    }

    if(!isPanning) return;
    const dx = e.clientX - panStartX;
    const dy = e.clientY - panStartY;
    dragDistance = Math.hypot(dx, dy);

    if(dragDistance > 6){
        viewer.classList.add("is-dragging");
        viewer.scrollLeft = panScrollLeft - dx;
        viewer.scrollTop = panScrollTop - dy;
    }
});

window.addEventListener("mouseup", () => {
    if(isPanning){
        isPanning = false;
        viewer.classList.remove("is-dragging");
    }
});

viewer.addEventListener("wheel", e => {
    if(e.ctrlKey || e.metaKey){
        e.preventDefault();
        const factor = e.deltaY < 0 ? 1.15 : 0.87;
        zoomAtPoint(e.clientX, e.clientY, factor);
    }
}, {passive: false});

image.addEventListener("dblclick", e => {
    e.preventDefault();
    e.stopPropagation();
    if(viewMode === "fit-screen"){
        setViewMode("fit-width");
    } else {
        setViewMode("fit-screen");
    }
});

if(zoomOutBtn) zoomOutBtn.onclick = (e) => { e.stopPropagation(); zoomOut(); };
if(zoomInBtn) zoomInBtn.onclick = (e) => { e.stopPropagation(); zoomIn(); };
if(zoomLevelBtn) zoomLevelBtn.onclick = (e) => { e.stopPropagation(); cycleZoomMode(); };
if(zoomLockBtn) zoomLockBtn.onclick = (e) => { e.stopPropagation(); toggleMaintainZoom(); };

document.addEventListener("click", e => {

    if(dragDistance > 6){
        dragDistance = 0;
        return;
    }

    // Prevent double-triggering from touch events that already ran
    if(Date.now()-lastTouchTime<600)return;

    // Ignore clicks on UI elements (sidebar, close button, fullscreen button, zoom widget, edge trigger)
    if(e.target.closest("#sidebar, #fullscreen-btn, #zoom-widget, #sidebar-close, #edge"))return;

    // If sidebar is open, click outside closes it
    if(sidebar.classList.contains("open")){
        closeSidebar();
        return;
    }

    const width=window.innerWidth;
    const x=e.clientX;

    const isNext = (readingDirection === "ltr") ? (x > width * 0.65) : (x < width * 0.35);
    const isPrev = (readingDirection === "ltr") ? (x < width * 0.35) : (x > width * 0.65);

    if(isNext){
        next();
    }else if(isPrev){
        previous();
    }else{
        if(isFullscreen()){
            revealFullscreenUI();
        }
        openSidebar();
    }

});


/* =========================
   Sidebar
   ========================= */

function openSidebar(){

    clearTimeout(closeTimer);

    sidebar.classList.add("open");

    updateSidebar();

    if(isFullscreen()){

        document.body.classList.remove(
            "fullscreen-ui-hidden"
        );

        clearTimeout(hideUITimer);

    }
}

function closeSidebar(){

    sidebar.classList.remove("open");

    if(isFullscreen()){

        clearTimeout(hideUITimer);

        hideUITimer=setTimeout(
            hideFullscreenUI,
            2500
        );

    }
}

function delayedClose(){

    closeTimer=setTimeout(
        closeSidebar,
        300
    );
}


/*
   Desktop mouse edge behavior.
*/

edge.addEventListener(
    "mouseenter",
    ()=>{

        if(!isFullscreen())
            openSidebar();

    }
);

sidebar.addEventListener(
    "mouseenter",
    ()=>{
        clearTimeout(closeTimer);
    }
);

sidebar.addEventListener(
    "mouseleave",
    delayedClose
);


/*
   Explicit top-left sidebar button.
*/

sidebarClose.addEventListener(
    "click",
    e=>{

        e.stopPropagation();
        closeSidebar();

    }
);


/* =========================
   Non-fullscreen left-edge swipe
   ========================= */

let edgeStartX=0;
let edgeStartY=0;

document.addEventListener(
    "touchstart",
    e=>{

        if(isFullscreen())return;

        const t=e.changedTouches[0];

        if(
            !sidebar.classList.contains("open") &&
            t.clientX<=25
        ){

            edgeStartX=t.clientX;
            edgeStartY=t.clientY;

        }

    },
    {passive:true}
);


document.addEventListener(
    "touchend",
    e=>{

        if(
            isFullscreen() ||
            sidebar.classList.contains("open")
        )return;

        const t=e.changedTouches[0];

        const dx=t.clientX-edgeStartX;
        const dy=t.clientY-edgeStartY;

        if(
            edgeStartX<=25 &&
            dx>60 &&
            Math.abs(dy)<100
        ){

            openSidebar();

        }

    },
    {passive:true}
);


/* =========================
   Sidebar swipe close
   ========================= */

let sidebarStartX=0;
let sidebarStartY=0;

sidebar.addEventListener(
    "touchstart",
    e=>{

        const t=e.changedTouches[0];

        sidebarStartX=t.clientX;
        sidebarStartY=t.clientY;

    },
    {passive:true}
);

sidebar.addEventListener(
    "touchend",
    e=>{

        const t=e.changedTouches[0];

        const dx=t.clientX-sidebarStartX;
        const dy=t.clientY-sidebarStartY;

        if(
            dx<-60 &&
            Math.abs(dy)<100
        ){

            closeSidebar();

        }

    },
    {passive:true}
);


/* =========================
   Swipe hint
   ========================= */

function showSwipeHint(){

    if(window.innerWidth<=600){

        swipeHint.textContent = (readingDirection === "ltr")
            ? "← Swipe left for next page"
            : "Swipe right for next page →";

        swipeHint.classList.add("show");

        setTimeout(
            ()=>swipeHint.classList.remove("show"),
            2500
        );

    }
}


fullscreenBtn.addEventListener(
    "click",
    toggleFullscreen
);


/* =========================
   Start
   ========================= */

load();

setTimeout(
    showSwipeHint,
    800
);

</script>

</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):

        path=urllib.parse.unquote(self.path)

        if path=="/" or path.startswith("/?"):

            data=HTML.encode()

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8"
            )
            self.send_header(
                "Content-Length",
                len(data)
            )
            self.end_headers()

            self.wfile.write(data)
            return


        if path=="/images":

            data=json.dumps(
                get_images()
            ).encode()

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/json"
            )
            self.send_header(
                "Content-Length",
                len(data)
            )
            self.end_headers()

            self.wfile.write(data)
            return


        file=(ROOT/path.lstrip("/")).resolve()

        try:
            file.relative_to(ROOT)
        except ValueError:
            self.send_error(403)
            return

        if file.is_file():

            mime=(
                mimetypes.guess_type(file.name)[0]
                or "application/octet-stream"
            )

            self.send_response(200)
            self.send_header(
                "Content-Type",
                mime
            )
            self.send_header(
                "Cache-Control",
                "public, max-age=3600"
            )
            self.end_headers()

            with open(file,"rb") as f:
                self.wfile.write(f.read())

            return

        self.send_error(404)


    def log_message(self,format,*args):
        pass


if __name__=="__main__":

    parser = argparse.ArgumentParser(
        prog="ChapterFlow",
        description="Lightweight local reader for chaptered folders — study notes, documents, book scans, and comics."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=None,
        help="Directory containing chapter or note folders (default: script directory)"
    )
    parser.add_argument(
        "-d", "--dir",
        dest="dir_opt",
        default=None,
        help="Directory containing chapter or note folders (alternative to positional argument)"
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=8000,
        help="Port to run the server on (default: 8000)"
    )
    parser.add_argument(
        "-b", "--bind",
        default="localhost",
        help="Address to bind to (default: localhost, use 0.0.0.0 for LAN/mobile access)"
    )

    args = parser.parse_args()

    chosen_dir = args.dir_opt or args.directory or Path(__file__).parent.resolve()
    ROOT = Path(chosen_dir).resolve()

    if not ROOT.is_dir():
        print(f"Error: Directory does not exist: {ROOT}", file=sys.stderr)
        sys.exit(1)

    try:
        server = HTTPServer((args.bind, args.port), Handler)
    except OSError as e:
        print(f"Error: Could not bind to {args.bind}:{args.port} ({e})", file=sys.stderr)
        sys.exit(1)

    url_host = "localhost" if args.bind in ("0.0.0.0", "") else args.bind

    print("=" * 48)
    print("  ChapterFlow - Local Image & Chapter Reader")
    print("  (Study Notes, Docs, Book Scans & Comics)")
    print(f"  Reading from: {ROOT}")
    print(f"  Server URL:   http://{url_host}:{args.port}")
    if args.bind == "0.0.0.0":
        print("  LAN Access:   Available on your local IP")
    print("  Press Ctrl+C to stop.")
    print("=" * 48)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping ChapterFlow. Goodbye!")
        server.server_close()