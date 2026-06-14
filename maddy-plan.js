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
