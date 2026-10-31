import * as THREE from './three.module.js';
const host=document.querySelector('.scene');host.innerHTML='';
try {
const scene=new THREE.Scene();scene.fog=new THREE.Fog(0xedf0e9,22,48);const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.7));renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;host.append(renderer.domElement);
const camera=new THREE.PerspectiveCamera(35,1,.1,200);const root=new THREE.Group();scene.add(root);const ambient=new THREE.HemisphereLight(0xffffff,0x8b9c7e,2.5);scene.add(ambient);const sun=new THREE.DirectionalLight(0xfff7e9,3);sun.position.set(-10,25,15);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);Object.assign(sun.shadow.camera,{left:-25,right:25,top:25,bottom:-25});sun.shadow.bias=-.001;scene.add(sun);
const mats={};function material(c){return mats[c]??=new THREE.MeshStandardMaterial({color:c,roughness:.83})}
function cube(x,y,z,w,h,d,c,parent=root){const o=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),material(c));o.position.set(x,y,z);o.castShadow=true;o.receiveShadow=true;parent.add(o);return o}
const ground=cube(0,-.23,0,36,.4,36,0xf0f1e8);const grid=new THREE.GridHelper(36,36,0xc9d2c5,0xdde2d7);grid.position.y=-.015;root.add(grid);
cube(0,.02,0,17,.14,13,0xd8dece);cube(0,.12,0,12,.16,10,0xecece0);
const building=new THREE.Group();root.add(building);
const floors=[];
function apartment(x,z,w,d,count,parent=building,detail=false){
 for(let f=0;f<count;f++){
  const floor=new THREE.Group();floor.position.set(x,.2+f*.9,z);parent.add(floor);
  if(detail) floors.push(floor);
  cube(0,.06,0,w+.2,.12,d+.2,0xe4e2d6,floor);
  // Each storey is a complete architectural unit: slab, walls, windows and balcony.
  cube(0,.45,0,w,.78,d,0xc6c5b1,floor);
  for(let i=0;i<4;i++){
   const xx=-w/2+.45+i*(w-.9)/3;
   cube(xx,.48,d/2+.025,.53,.61,.06,0x4e6861,floor);
   cube(xx,.48,-d/2-.025,.53,.61,.06,0x59756c,floor);
   if(detail) cube(xx,.48,d/2+.065,.025,.61,.03,0xb9c6b9,floor);
  }
  for(let i=0;i<3;i++)cube(w/2+.025,.48,-d/2+.6+i*(d-1.2)/2,.06,.6,.64,0x526b61,floor);
  cube(0,.13,d/2+.38,w+.16,.12,.76,0xe1dfce,floor);
  cube(0,.52,d/2+.74,w,.035,.035,0x75877a,floor);
  for(let k=0;k<(detail?12:5);k++)cube(-w/2+k*w/((detail?12:5)-1),.34,d/2+.74,.025,.36,.025,0x75877a,floor);
  if(detail){cube(-w/2+.3,.23,d/2+.4,.45,.22,.3,0x8b9875,floor);cube(-w/2+.3,.4,d/2+.4,.48,.15,.32,0x70875f,floor);cube(.1,.85,0,.12,.05,d,0x9cab97,floor)}
 }
 const roof=new THREE.Group();roof.position.set(x,.2+count*.9,z);parent.add(roof);if(detail)floors.push(roof);
 cube(0,.08,0,w+.3,.16,d+.3,0xebe9dc,roof);cube(0,.2,0,w-.3,.08,d-.3,0xb0bba8,roof);
 cube(-.4,.5,-.4,1.4,.65,1.4,0xdcdccc,roof);cube(-.4,.85,-.4,1.5,.07,1.5,0xeeeede,roof);
 if(detail){for(let i=0;i<3;i++)cube(.8,.33,-.7+i*.5,1,.06,.35,0x566e69,roof);cube(0,.22,-d/2,w,.3,.08,0xd4d6c3,roof)}
}
apartment(0,0,4.2,3.5,6,building,true);
function tree(x,z,s=1){cube(x,.5*s,z,.13*s,1*s,.13*s,0x8a8063);for(let i=0;i<4;i++){const o=new THREE.Mesh(new THREE.IcosahedronGeometry((.45+i%2*.12)*s,1),material(i%2?0x6f8252:0x879365));o.position.set(x+Math.sin(i*2)*.25*s,1.1*s+i*.15*s,z+Math.cos(i*2)*.2*s);o.castShadow=true;root.add(o)}}
for(let i=0;i<8;i++){tree(-5+i*1.45,-4.4,.9);if(i!==3&&i!==4)tree(-5+i*1.45,4.4,.85)}for(let i=0;i<3;i++){tree(-5, -2+i*2);tree(5,-2+i*2)}
const neighborhood=new THREE.Group();root.add(neighborhood);
// The city exists from the first frame. Camera movement reveals it without toggling buildings.
for(let k=-3;k<=3;k++){
 cube(k*10-5,.005,0,1.6,.04,74,0xc4cdbf,neighborhood);
 cube(0,.005,k*10-5,74,.04,1.6,0xc4cdbf,neighborhood);
 for(let j=-3;j<=3;j++){
  if(k===0&&j===0)continue;
  const x=k*10,z=j*10;
  cube(x,.01,z,7.9,.08,7.9,0xdde2d3,neighborhood);
  apartment(x-1.8,z-1.5,2.5,2.4,2+Math.abs(k+j)%4,neighborhood);
  apartment(x+1.8,z+1.4,2.1,2.1,2+Math.abs(k-j)%3,neighborhood);
  tree(x+2.8,z-2.5,.8);tree(x-2.8,z+2.7,.7);
  cube(x+3,.2,z,.7,.35,1.25,0x8d9c90,neighborhood);
 }
}
ground.scale.set(2.2,1,2.2);
let daylight=document.documentElement.dataset.theme==='dark'?0:1;
const nightColor=new THREE.Color(0x101e23),dayColor=new THREE.Color(0xedf0e9);
const motionPreference=matchMedia('(prefers-reduced-motion: reduce)');
let motion=motionPreference.matches;
const sections=[...document.querySelectorAll('#home,#location,#property,#research,#valuation')];
const label=document.createElement('div');label.className='scene-caption';host.append(label);
const phases=['01 / THE PROPERTY','02 / THE CITY AROUND IT','03 / BACK TO THE DETAILS','04 / FLOOR BY FLOOR','05 / EVIDENCE TO ESTIMATE'];
let pending=false, animationFrame=0, lastTime=0, drift=0, previousSpread=-1;
renderer.shadowMap.autoUpdate=false;
const smooth=t=>{t=Math.max(0,Math.min(1,t));return t*t*(3-2*t)};
function draw(){
 pending=false;
 const dayTarget=document.documentElement.dataset.theme==='dark'?0:1;daylight=motion?dayTarget:daylight+(dayTarget-daylight)*.08;
 scene.fog.color.copy(nightColor).lerp(dayColor,daylight);ambient.intensity=.55+daylight*1.95;sun.intensity=.5+daylight*2.5;sun.color.set(daylight<.5?0xa8bdff:0xfff7e9);
 Object.values(mats).forEach(m=>{if([0x4e6861,0x59756c,0x526b61].includes(m.color.getHex())){m.emissive.setHex(0xffbc66);m.emissiveIntensity=(1-daylight)*.75}});
 let index=0;for(let i=0;i<sections.length;i++)if(scrollY>=sections[i].offsetTop-100)index=i;
 const current=sections[index],next=sections[index+1] || document.querySelector('#platform');
 const t=smooth((scrollY-current.offsetTop+100)/Math.max(1,next.offsetTop-current.offsetTop));
 const distances=[20,67,23,29,22,25],targets=[2,0,2.8,5.3,2.8,3.2],explosions=[0,0,0,1,0,0];
 const end=index+1,mix=(v)=>v[index]+(v[end]-v[index])*t;
 const spread=motion?0:mix(explosions);
 if(Math.abs(spread-previousSpread)>.0001){renderer.shadowMap.needsUpdate=true;previousSpread=spread;}
 floors.forEach((floor,i)=>floor.position.y=.2+i*.9+spread*i*.9);
 const narrow=innerWidth<=800;
 if(narrow){
  // Give every section a real, reserved architectural viewport below its copy.
  const slot=current.querySelector('.model-slot');
  host.style.position='absolute';host.style.top=(slot.getBoundingClientRect().top+scrollY)+'px';
  host.style.left='5%';host.style.width='90%';host.style.height=slot.offsetHeight+'px';
 }else{host.style.position='fixed';host.style.top='110px';host.style.left='48%';host.style.width='49%';host.style.height='calc(100svh - 145px)'}
 const w=host.clientWidth,h=host.clientHeight;
 if(renderer.domElement.width!==Math.round(w*renderer.getPixelRatio())||renderer.domElement.height!==Math.round(h*renderer.getPixelRatio()))renderer.setSize(w,h);
 camera.aspect=w/h;camera.updateProjectionMatrix();
 const distance=mix(distances)*Math.max(1,1/camera.aspect*.85);
 const angle=.78+(motion?0:(index+t)*.07+Math.sin(drift)*.065);
 camera.position.set(Math.sin(angle)*distance,distance*(.72+(motion?0:Math.sin(drift*.7)*.009)),Math.cos(angle)*distance);camera.lookAt(0,mix(targets),0);scene.fog.near=distance*.85;scene.fog.far=distance*1.7;
 host.style.opacity=String(smooth((document.querySelector('#platform').getBoundingClientRect().top-80)/200));
 label.textContent=phases[index]+' · ILLUSTRATIVE ARCHITECTURE';renderer.render(scene,camera);
}
// Idle drift only runs while the architecture is visible; never animate a hidden tab.
function loop(now){
 animationFrame=0;
 if(document.hidden)return;
 const visible=document.querySelector('#platform').getBoundingClientRect().top>80;
 if(!motion && visible){
  if(!lastTime || now-lastTime>=32){drift+=lastTime?Math.min(now-lastTime,80)*.00012:0;lastTime=now;draw();}
  animationFrame=requestAnimationFrame(loop);
 }else lastTime=0;
}
function wake(){if(!animationFrame&&!motion&&!document.hidden)animationFrame=requestAnimationFrame(loop);}
function update(){if(!pending){pending=true;requestAnimationFrame(draw)}wake();}
addEventListener('themechange',()=>{renderer.shadowMap.needsUpdate=true;update()});addEventListener('resize',update);addEventListener('scroll',update,{passive:true});
document.addEventListener('visibilitychange',()=>{lastTime=0;if(document.hidden){cancelAnimationFrame(animationFrame);animationFrame=0}else wake()});
motionPreference.addEventListener('change',()=>{motion=motionPreference.matches;update()});draw();wake();
addEventListener('pagehide',()=>{cancelAnimationFrame(animationFrame);renderer.dispose();scene.traverse(o=>{if(o.geometry)o.geometry.dispose()});Object.values(mats).forEach(m=>m.dispose())},{once:true});
} catch(e){host.innerHTML='<div class="fallback">Architectural view unavailable on this device.<br>Explore the property research workflow below.</div>'}
