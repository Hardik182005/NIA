import * as THREE from 'three';

const EXAMS=12, PERIODS=8, STUDENTS=120, SEED=42, PARTICLES=32, ITERATIONS=100;
function randomSource(seed){let s=seed>>>0;return()=>{s=(1664525*s+1013904223)>>>0;return s/4294967296}}
const random=randomSource(SEED), enrollment=[];
for(let s=0;s<STUDENTS;s++){
  const cohort=Math.min(Math.floor(s/Math.ceil(STUDENTS/3)),2);
  const ids=Array.from({length:Math.floor(EXAMS/3)},(_,i)=>cohort*Math.floor(EXAMS/3)+i);
  for(let i=ids.length-1;i>0;i--){const j=Math.floor(random()*(i+1));[ids[i],ids[j]]=[ids[j],ids[i]]}
  enrollment.push(ids.slice(0,3+(s%4===0?1:0)).sort((a,b)=>a-b));
}
const sizes=Array(EXAMS).fill(0), weights=Array.from({length:EXAMS},()=>Array(EXAMS).fill(0));
for(const row of enrollment){for(const e of row)sizes[e]++;for(let a=0;a<row.length;a++)for(let b=a+1;b<row.length;b++){weights[row[a]][row[b]]++;weights[row[b]][row[a]]++}}
const degree=weights.map(row=>row.reduce((a,b)=>a+b,0));
function conflicts(assign){let n=0;for(let a=0;a<EXAMS;a++)for(let b=a+1;b<EXAMS;b++)if(assign[a]===assign[b])n+=weights[a][b];return n}
function repair(position){
  const load=Array(PERIODS).fill(0), plan=Array(EXAMS).fill(-1);
  const order=Array.from({length:EXAMS},(_,i)=>i).sort((a,b)=>degree[b]-degree[a]||position[a]-position[b]||a-b);
  for(const exam of order){let best=0,bestScore=Infinity;
    for(let p=0;p<PERIODS;p++){let clash=0;for(let other=0;other<EXAMS;other++)if(plan[other]===p)clash+=weights[exam][other];
            const score=clash*10000+(load[p]===0?20:0)+load[p]*3+Math.abs(p-Math.round(position[exam]))*.02;
      if(score<bestScore){bestScore=score;best=p}}
    plan[exam]=best;load[best]++;
  }return plan;
}
function evaluate(position){const plan=repair(position),loads=Array(PERIODS).fill(0);for(const p of plan)loads[p]++;
  const live=loads.filter(x=>x>0),mean=live.reduce((a,b)=>a+b,0)/Math.max(1,live.length);
  const spread=Math.sqrt(live.reduce((n,x)=>n+(x-mean)**2,0)/Math.max(1,live.length));
  const clashes=conflicts(plan),used=live.length;return{plan,clashes,used,spread,score:clashes*10000+used*100+spread};
}
function optimize(){const rand=randomSource(SEED+99),swarm=[];let global=null;
  for(let n=0;n<PARTICLES;n++){const pos=Array.from({length:EXAMS},()=>rand()*(PERIODS-1)),vel=Array(EXAMS).fill(0),f=evaluate(pos);swarm.push({pos,vel,best:pos.slice(),bestScore:f.score});if(!global||f.score<global.score)global={pos:pos.slice(),...f}}
  for(let it=0;it<ITERATIONS;it++)for(const particle of swarm){
    for(let d=0;d<EXAMS;d++){const r1=rand(),r2=rand();particle.vel[d]=.68*particle.vel[d]+1.42*r1*(particle.best[d]-particle.pos[d])+1.42*r2*(global.pos[d]-particle.pos[d]);particle.pos[d]=Math.max(0,Math.min(PERIODS-1,particle.pos[d]+particle.vel[d]))}
    const f=evaluate(particle.pos);if(f.score<particle.bestScore){particle.bestScore=f.score;particle.best=particle.pos.slice()}if(f.score<global.score)global={pos:particle.pos.slice(),...f}
  }return{...global,iterations:ITERATIONS};
}

// Actual 3D scene: a draggable isometric array of exam blocks and periods.
function makeLabel(label){const c=document.createElement('canvas');c.width=256;c.height=96;const x=c.getContext('2d');x.fillStyle='#fff';x.fillRect(0,0,256,96);x.fillStyle='#111';x.font='600 48px monospace';x.textAlign='center';x.textBaseline='middle';x.fillText(label,128,48);const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;return t}
function mountScene(){const canvas=document.querySelector('#scene');try{
  const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setSize(canvas.clientWidth,canvas.clientHeight,false);renderer.shadowMap.enabled=true;renderer.outputColorSpace=THREE.SRGBColorSpace;
  const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(33,canvas.clientWidth/canvas.clientHeight,.1,100);camera.position.set(9,8,12);camera.lookAt(0,1,0);
  const rig=new THREE.Group();scene.add(rig);scene.add(new THREE.HemisphereLight(0xffffff,0xaaa9a3,2.1));const light=new THREE.DirectionalLight(0xffffff,3.3);light.position.set(-5,10,8);light.castShadow=true;scene.add(light);
  const floor=new THREE.Mesh(new THREE.PlaneGeometry(15,12),new THREE.MeshStandardMaterial({color:0xf5f5f2,roughness:.9}));floor.rotation.x=-Math.PI/2;floor.position.y=-.06;floor.receiveShadow=true;rig.add(floor);
  const grid=new THREE.GridHelper(13,13,0xc6c6c0,0xd8d8d3);grid.position.y=-.045;rig.add(grid);
  const blocks=new THREE.Group(),base=new THREE.MeshStandardMaterial({color:0xd2d2ce,roughness:.7}),dark=new THREE.MeshStandardMaterial({color:0x1a1a19,roughness:.42});rig.add(blocks);
  const names=['AI','ML','DB','OS','CN','DS','SE','NLP','CV','IOT','DM','IR'];
  names.forEach((name,i)=>{const x=(i%4-1.5)*2.15,z=(Math.floor(i/4)-1)*2.2,h=.55+(i%3)*.24;const plinth=new THREE.Mesh(new THREE.BoxGeometry(1.5,.18,1.3),base);plinth.position.set(x,.08,z);plinth.castShadow=true;plinth.receiveShadow=true;blocks.add(plinth);const exam=new THREE.Mesh(new THREE.BoxGeometry(1.08,h,.87),dark);exam.position.set(x,.18+h/2,z);exam.castShadow=true;exam.receiveShadow=true;blocks.add(exam);const face=new THREE.Mesh(new THREE.PlaneGeometry(.75,.28),new THREE.MeshBasicMaterial({map:makeLabel(name),transparent:true}));face.position.set(x,.22+h,z+.446);blocks.add(face)});
  let dragging=false,lastX=0,lastY=0,rot=0;canvas.addEventListener('pointerdown',e=>{dragging=true;lastX=e.clientX;lastY=e.clientY;canvas.setPointerCapture(e.pointerId)});canvas.addEventListener('pointermove',e=>{if(!dragging)return;rot+=(e.clientX-lastX)*.008;rig.rotation.y=rot;camera.position.y=Math.max(4,Math.min(13,camera.position.y+(e.clientY-lastY)*.025));camera.lookAt(0,1,0);lastX=e.clientX;lastY=e.clientY});canvas.addEventListener('pointerup',()=>dragging=false);
  new ResizeObserver(()=>{renderer.setSize(canvas.clientWidth,canvas.clientHeight,false);camera.aspect=canvas.clientWidth/canvas.clientHeight;camera.updateProjectionMatrix()}).observe(canvas);
  function draw(t){if(!dragging)rig.rotation.y=rot+Math.sin(t*.00023)*.10;renderer.render(scene,camera);requestAnimationFrame(draw)}requestAnimationFrame(draw);
}catch(e){canvas.setAttribute('aria-label','Three-dimensional preview is unavailable in this browser.')}}
mountScene();
function render(result){document.querySelector('#clash-count').textContent=result.clashes;document.querySelector('#period-count').textContent=result.used;document.querySelector('#iteration-count').textContent=result.iterations;document.querySelector('#strip-conflicts').textContent=`${result.clashes} clashes`;document.querySelector('#strip-slots').textContent=`${result.used} periods occupied`;
  const days=['Mon','Tue','Wed','Thu'];document.querySelector('#schedule-body').innerHTML=result.plan.map((p,i)=>`<tr><td>EX-${String(i+1).padStart(2,'0')}</td><td>${sizes[i]}</td><td>${days[Math.floor(p/2)]}</td><td>${p%2===0?'AM':'PM'} · ${p+1}</td></tr>`).join('');document.querySelector('#run-status').textContent='Search complete. Every candidate schedule was checked against student clashes.'}
document.querySelector('#run-button').addEventListener('click',()=>{const button=document.querySelector('#run-button');button.disabled=true;button.innerHTML='Searching… <span>↻</span>';document.querySelector('#run-status').textContent='Updating candidate schedules…';requestAnimationFrame(()=>{render(optimize());button.disabled=false;button.innerHTML='Run PSO <span>↗</span>'})});
