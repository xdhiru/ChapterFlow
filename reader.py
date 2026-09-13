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
   Reader
   ========================= */

#image{
    width:100vw;
    height:100vh;
    object-fit:contain;
    display:block;
    user-select:none;
    -webkit-user-select:none;
    -webkit-user-drag:none;
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
}

#fullscreen-btn:hover{
    background:rgba(50,50,50,.95);
    color:#fff;
}


/* =========================
   Fullscreen UI hiding
   ========================= */

body.fullscreen-ui-hidden #fullscreen-btn{
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

<img id="image" draggable="false">

<div id="fullscreen-gesture"></div>

<div id="edge"></div>

<div id="swipe-hint">
    ← Swipe to navigate →
</div>

<button id="fullscreen-btn">
    Go Fullscreen
</button>


<div id="sidebar">

    <div id="sidebar-header">
        <button id="sidebar-close" aria-label="Close sidebar">×</button>
        <div id="sidebar-title">Reading Order</div>
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
const sidebar=document.getElementById("sidebar");
const edge=document.getElementById("edge");
const tree=document.getElementById("tree");
const swipeHint=document.getElementById("swipe-hint");
const fullscreenBtn=document.getElementById("fullscreen-btn");
const fullscreenGesture=document.getElementById("fullscreen-gesture");
const sidebarClose=document.getElementById("sidebar-close");


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

function show(){

    if(!images.length)return;

    image.src=images[index].url;

    history.replaceState(
        null,
        "",
        "?page="+index
    );

    updateSidebar();
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
        show();

    }
}

function previous(){

    if(index>0){

        index--;
        show();

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

document.addEventListener(
    "fullscreenchange",
    ()=>{

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

    }
);


/* =========================
   Keyboard
   ========================= */

document.addEventListener("keydown",e=>{

    if(
        e.key==="ArrowRight" ||
        e.key===" " ||
        e.key==="PageDown"
    ){

        e.preventDefault();
        next();

    }

    if(
        e.key==="ArrowLeft" ||
        e.key==="PageUp"
    ){

        e.preventDefault();
        previous();

    }

    if(e.key==="Home"){

        index=0;
        show();

    }

    if(e.key==="End"){

        index=images.length-1;
        show();

    }

    if(e.key.toLowerCase()==="f"){

        e.preventDefault();
        toggleFullscreen();

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
let fsTracking=false;

const SWIPE_THRESHOLD=50;
const VERTICAL_LIMIT=100;

fullscreenGesture.addEventListener(
    "touchstart",
    e=>{

        if(!isFullscreen())return;

        const t=e.changedTouches[0];

        fsStartX=t.clientX;
        fsStartY=t.clientY;
        fsTracking=true;

    },
    {passive:false}
);


fullscreenGesture.addEventListener(
    "touchmove",
    e=>{

        if(!isFullscreen()||!fsTracking)return;

        /*
           Prevent browser horizontal gesture handling.
           Vertical page movement is irrelevant in fullscreen.
        */
        e.preventDefault();

    },
    {passive:false}
);


fullscreenGesture.addEventListener(
    "touchend",
    e=>{

        if(!isFullscreen()||!fsTracking)return;

        const t=e.changedTouches[0];

        const dx=t.clientX-fsStartX;
        const dy=t.clientY-fsStartY;

        const width=window.innerWidth;
        const x=fsStartX;

        fsTracking=false;

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
           - Swipe RIGHT  → next
           - Swipe LEFT   → previous
           - Tap left 35% → next
           - Tap right 35% → previous
        */

        const isLeftZone = x < width * 0.35;
        const isRightZone = x > width * 0.65;

        // Clear horizontal swipe?
        if(
            Math.abs(dx)>=SWIPE_THRESHOLD &&
            Math.abs(dy)<=VERTICAL_LIMIT &&
            Math.abs(dy)<=Math.abs(dx)
        ){

            // Swipe RIGHT → next, Swipe LEFT → previous
            if(dx>0)
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

            if(isLeftZone){
                // Tap on left 35% → next
                next();
            }else if(isRightZone){
                // Tap on right 35% → previous
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
        description="Lightweight local manga and comic chapter reader."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=None,
        help="Directory containing chapter folders (default: script directory)"
    )
    parser.add_argument(
        "-d", "--dir",
        dest="dir_opt",
        default=None,
        help="Directory containing chapter folders (alternative to positional argument)"
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

    print("=" * 44)
    print("  ChapterFlow - Local Manga & Comic Reader")
    print(f"  Reading from: {ROOT}")
    print(f"  Server URL:   http://{url_host}:{args.port}")
    if args.bind == "0.0.0.0":
        print("  LAN Access:   Available on your local IP")
    print("  Press Ctrl+C to stop.")
    print("=" * 44)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping ChapterFlow. Goodbye!")
        server.server_close()