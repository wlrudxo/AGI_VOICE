import"./Bzak7iHL.js";import{p as B,l as C,g as r,c as v,f as g,i as E,d,n as P,r as c,s as R,e as l,a as u,b as S,t as Y}from"./BL0wSOjl.js";import{s as j,e as h,a as q}from"./DoRbC73M.js";import{p as _,i as z}from"./D_XkNnm9.js";import{s as A}from"./Bg7-wDZ5.js";import{b as D}from"./RI3GwsiT.js";var F=g('<div class="tooltip svelte-11extwn"> </div>'),G=g('<div class="tooltip-wrapper svelte-11extwn" role="tooltip"><!></div> <!>',1);function N(x,i){B(i,!0);let p=_(i,"text",3,""),b=_(i,"position",3,"right"),o=v(!1),s,n=v("");function f(){if(!s||!r(o))return;const t=s.getBoundingClientRect();b()==="right"&&l(n,`
        position: fixed;
        left: ${t.right+8}px;
        top: ${t.top+t.height/2}px;
        transform: translateY(-50%);
      `)}C(()=>{r(o)&&f()});var m=G(),e=E(m),w=d(e);j(w,()=>i.children??P),c(e),D(e,t=>s=t,()=>s);var T=R(e,2);{var y=t=>{var a=F(),k=d(a,!0);c(a),Y(()=>{A(a,r(n)),q(k,p())}),u(t,a)};z(T,t=>{r(o)&&p()&&t(y)})}h("mouseenter",e,()=>{l(o,!0),setTimeout(f,0)}),h("mouseleave",e,()=>l(o,!1)),u(x,m),S()}export{N as T};
