(function(){
  "use strict";
  var docEl=document.documentElement, body=document.body;

  // progress bar + back-to-top
  var prog=document.getElementById('prog');
  var top=document.getElementById('top');
  function onScroll(){
    var h=docEl.scrollHeight-docEl.clientHeight;
    var sc=docEl.scrollTop||body.scrollTop;
    if(prog) prog.style.width=(h>0?sc/h*100:0)+'%';
    if(top){ if(sc>600) top.classList.add('show'); else top.classList.remove('show'); }
  }
  window.addEventListener('scroll',onScroll,{passive:true});
  if(top) top.addEventListener('click',function(){window.scrollTo({top:0,behavior:'smooth'});});

  // copy buttons
  document.querySelectorAll('.copy').forEach(function(btn){
    btn.addEventListener('click',function(){
      var box=btn.closest('.msg');
      var txt=box?box.querySelector('.copytext'):null;
      var val=txt?txt.innerText:'';
      function ok(){btn.textContent='Copied';btn.classList.add('done');setTimeout(function(){btn.textContent='Copy';btn.classList.remove('done');},1600);}
      if(navigator.clipboard&&navigator.clipboard.writeText){
        navigator.clipboard.writeText(val).then(ok).catch(function(){fallback(val,ok);});
      }else{fallback(val,ok);}
    });
  });
  function fallback(val,ok){
    try{var ta=document.createElement('textarea');ta.value=val;document.body.appendChild(ta);ta.select();document.execCommand('copy');document.body.removeChild(ta);ok();}catch(e){}
  }

  // episode search + filter (videos page only)
  var eps=Array.prototype.slice.call(document.querySelectorAll('details.ep'));
  if(eps.length){
    var search=document.getElementById('epsearch');
    var chips=Array.prototype.slice.call(document.querySelectorAll('.fchip'));
    var count=document.getElementById('epcount');
    var activeF='all';
    function applyEp(){
      var q=(search&&search.value||'').toLowerCase().trim();
      var shown=0;
      eps.forEach(function(ep){
        var catOk=(activeF==='all'||ep.dataset.cat===activeF);
        var hook=ep.querySelector('.ephook');
        var hay=(ep.dataset.kw||'')+' '+(hook?hook.textContent.toLowerCase():'');
        var qOk=(!q||hay.indexOf(q)>-1);
        var show=catOk&&qOk;
        ep.classList.toggle('hidden',!show);
        if(show)shown++;
      });
      var filtering=(activeF!=='all'||q);
      document.querySelectorAll('#epwrap > h4').forEach(function(h){h.style.display=filtering?'none':'';});
      if(count) count.textContent=shown+(shown===1?' video':' videos');
    }
    if(search) search.addEventListener('input',applyEp);
    chips.forEach(function(c){
      c.addEventListener('click',function(){
        chips.forEach(function(x){x.classList.remove('on');});
        c.classList.add('on'); activeF=c.dataset.f; applyEp();
      });
    });
    applyEp();
  }
  onScroll();
})();

/* ===== Start map checklist (progress saved on device, only goes up in spirit) ===== */
(function(){
  "use strict";
  var journey=document.querySelector('.journey'); if(!journey) return;
  var steps=Array.prototype.slice.call(document.querySelectorAll('.step'));
  var total=steps.length, KEY='maddyplan_steps';
  function load(){ try{ return new Set(JSON.parse(localStorage.getItem(KEY)||'[]')); }catch(e){ return new Set(); } }
  function save(set){ try{ localStorage.setItem(KEY, JSON.stringify(Array.prototype.slice.call(set))); }catch(e){} }
  var done=load();
  var C=2*Math.PI*34;
  var ringfg=document.querySelector('.ringfg'), ringtxt=document.getElementById('ringtxt');
  var nextA=document.getElementById('nexttext'), nextSub=document.getElementById('nextsub');
  var nextCard=document.getElementById('nextstep'), allDone=document.querySelector('.alldone');
  steps.forEach(function(st,i){ if(!st.id) st.id='step-'+i; });
  function apply(){
    var n=0;
    steps.forEach(function(st){
      var id=st.dataset.id, b=st.querySelector('.box');
      if(done.has(id)){ st.setAttribute('data-done',''); n++; if(b){b.textContent='\u2713';b.setAttribute('aria-pressed','true');} }
      else { st.removeAttribute('data-done'); if(b){b.textContent='';b.setAttribute('aria-pressed','false');} }
    });
    if(ringfg) ringfg.style.strokeDasharray=(C*(total?n/total:0))+' '+C;
    if(ringtxt) ringtxt.textContent=n+'/'+total;
    var next=null;
    for(var i=0;i<steps.length;i++){ if(!done.has(steps[i].dataset.id)){ next=steps[i]; break; } }
    if(next){
      var lbl=next.querySelector('.slabel'), t=next.querySelector('.stime');
      if(nextA){ nextA.textContent=lbl?lbl.textContent:'Open'; nextA.setAttribute('data-target',next.id); }
      if(nextSub) nextSub.textContent=t?('about '+t.textContent):'';
      if(nextCard) nextCard.style.display='';
      if(allDone) allDone.style.display='none';
    } else {
      if(nextCard) nextCard.style.display='none';
      if(allDone) allDone.style.display='block';
    }
  }
  steps.forEach(function(st){
    var box=st.querySelector('.box'); if(!box) return;
    box.addEventListener('click', function(){
      var id=st.dataset.id;
      if(done.has(id)) done.delete(id); else done.add(id);
      save(done); apply();
    });
  });
  if(nextA){ nextA.addEventListener('click', function(e){
    e.preventDefault();
    var el=document.getElementById(nextA.getAttribute('data-target'));
    if(el) el.scrollIntoView({behavior:'smooth',block:'center'});
  }); }
  apply();
})();
