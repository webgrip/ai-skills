const toggle=document.querySelector("[data-menu]");toggle?.addEventListener("click",()=>document.body.classList.toggle("menu-open"));
addEventListener("pagehide",()=>navigator.sendBeacon?.("/rum",JSON.stringify({t:performance.now()})));
