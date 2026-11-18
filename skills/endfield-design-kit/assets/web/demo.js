/* Visual starter only. All eight records are synthetic demonstration values. */
'use strict';
const records=[
 {id:'A01',batch:'SET 01',value:31,error:3.2,reviewed:true},
 {id:'A02',batch:'SET 01',value:48,error:2.4,reviewed:true},
 {id:'A03',batch:'SET 01',value:42,error:4.1,reviewed:false},
 {id:'A04',batch:'SET 01',value:83,error:2.6,reviewed:false},
 {id:'A05',batch:'SET 02',value:70,error:3.4,reviewed:true},
 {id:'A06',batch:'SET 02',value:58,error:4.5,reviewed:false},
 {id:'A07',batch:'SET 02',value:79,error:2.9,reviewed:true},
 {id:'A08',batch:'SET 02',value:65,error:3.1,reviewed:false}
];
let selected='A04';
const byId=id=>document.getElementById(id);
function filtered(){const query=byId('query').value.trim().toLowerCase(),batch=byId('batch').value;return records.filter(r=>(batch==='all'||r.batch===batch)&&(!query||(r.id+' '+r.batch).toLowerCase().includes(query)));}
function select(id){
 const active=document.activeElement;
 const source=active?.classList.contains('yp-record-button')?'record':active?.classList.contains('point')?'point':null;
 selected=id;render();
 if(source){const node=document.querySelector((source==='record'?'.yp-record-button':'.point')+'[data-record="'+CSS.escape(id)+'"]');node?.focus();}
}
function render(){
 const list=filtered();if(!list.some(r=>r.id===selected))selected=list[0]?.id||null;
 byId('rows').replaceChildren();
 for(const r of list){const row=document.createElement('tr');row.dataset.current=String(r.id===selected);const cell=document.createElement('td'),button=document.createElement('button');button.className='yp-record-button';button.dataset.record=r.id;button.textContent=r.id;button.setAttribute('aria-pressed',String(r.id===selected));button.addEventListener('click',()=>select(r.id));cell.append(button);row.append(cell);for(const [index,value] of [r.batch,r.value,r.error.toFixed(1),r.reviewed?'已复核':'待复核'].entries()){const td=document.createElement('td');td.textContent=value;if(index===1||index===2)td.className='number';row.append(td);}row.addEventListener('click',e=>{if(!e.target.closest('button'))select(r.id);});byId('rows').append(row);}
 byId('empty').hidden=!!list.length;byId('recordCount').textContent=`${list.length} / ${records.length} 条演示记录`;
 const r=list.find(r=>r.id===selected);byId('recordId').textContent=r?`${r.id} / ${r.batch}`:'暂无记录';byId('recordValue').textContent=r?r.value:'—';byId('detailId').textContent=r?r.id:'—';byId('detailError').textContent=r?`± ${r.error.toFixed(1)}`:'—';byId('detailState').textContent=r?(r.reviewed?'已复核':'待复核'):'—';byId('selectedTag').textContent=r?`当前记录 ${r.id}`:'没有匹配记录';byId('nextRecord').disabled=!r;
 renderChart(list);
}
function svgNode(tag,attributes,text){const node=document.createElementNS('http://www.w3.org/2000/svg',tag);Object.entries(attributes).forEach(([key,value])=>node.setAttribute(key,String(value)));if(text!==undefined)node.textContent=text;return node;}
function renderChart(list){
 const width=Math.max(240,Math.min(760,byId('chart').clientWidth||760)),height=width<430?260:330,left=48,right=width-12,bottom=height-38,scale=(bottom-24)/100;
 byId('chart').setAttribute('viewBox',`0 0 ${width} ${height}`);
 const grid=byId('chartGrid'),points=byId('chartPoints');grid.replaceChildren();points.replaceChildren();
 for(const value of [0,25,50,75,100]){const y=bottom-value*scale;grid.append(svgNode('line',{x1:left,y1:y,x2:right,y2:y,class:'grid'}),svgNode('text',{x:left-13,y:y+4,'text-anchor':'end'},value));}
 const coords=list.map((r,i)=>({r,x:list.length===1?(left+right)/2:left+i*(right-left)/(list.length-1),y:bottom-r.value*scale}));
 byId('trace').setAttribute('d',coords.map((p,i)=>`${i?'L':'M'}${p.x},${p.y}`).join(' '));
 for(const {r,x,y} of coords){grid.append(svgNode('text',{x,y:height-13,'text-anchor':'middle'},r.id));const point=svgNode('circle',{cx:x,cy:y,r:r.id===selected?6:4,class:'point','data-record':r.id,tabindex:0,role:'button','aria-label':`选择演示记录 ${r.id}，响应 ${r.value}`,'aria-pressed':String(r.id===selected)});point.addEventListener('click',()=>select(r.id));point.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();select(r.id);}});points.append(point);}
}
const views={analysis:['// 01 / WORKBENCH','数据分析工作台','浏览记录、对照响应曲线，再整理成可以复核的报告。'],report:['// 02 / READING','数据与复核报告','同一套视觉语言，适配连续阅读和打印。'],components:['// 03 / ELEMENTS','组件与配色','查看动作、选中、状态和深浅色的实际效果。']};
function showView(view){if(!views[view])return;Object.keys(views).forEach(key=>byId(key+'View').hidden=key!==view);document.querySelectorAll('[data-view]').forEach(button=>{if(button.dataset.view===view)button.setAttribute('aria-current','page');else button.removeAttribute('aria-current');});const [kicker,title,subtitle]=views[view];byId('pageKicker').textContent=kicker;byId('pageTitle').textContent=title;byId('pageSubtitle').textContent=subtitle;}
document.querySelectorAll('[data-view]').forEach(button=>button.addEventListener('click',()=>showView(button.dataset.view)));
document.querySelector('.yp-brand').addEventListener('click',()=>showView('analysis'));
byId('showReport').addEventListener('click',()=>showView('report'));
byId('printReport').addEventListener('click',()=>window.print());
byId('themeToggle').addEventListener('click',()=>{const dark=document.documentElement.dataset.theme!=='dark';document.documentElement.dataset.theme=dark?'dark':'light';byId('themeToggle').textContent=dark?'浅色模式':'深色模式';byId('themeToggle').setAttribute('aria-pressed',String(dark));});
byId('toneToggle').addEventListener('click',()=>{const soft=document.documentElement.dataset.tone!=='soft';document.documentElement.dataset.tone=soft?'soft':'bright';byId('toneToggle').textContent=soft?'亮黄强调':'柔黄强调';byId('toneToggle').setAttribute('aria-pressed',String(soft));});
byId('query').addEventListener('input',render);byId('batch').addEventListener('change',render);byId('nextRecord').addEventListener('click',()=>{const list=filtered();select(list[(list.findIndex(r=>r.id===selected)+1)%list.length].id);});
byId('exportCsv').addEventListener('click',()=>{const lines=['record,batch,response_au,error_au,reviewed',...filtered().map(r=>[r.id,r.batch,r.value,r.error,r.reviewed?'yes':'no'].join(','))];const url=URL.createObjectURL(new Blob(['\uFEFF'+lines.join('\r\n')],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='yellow-paper-demo.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);byId('feedback').textContent='已导出演示记录 CSV。';});
document.querySelectorAll('[data-demo-action]').forEach(button=>button.addEventListener('click',()=>byId('componentFeedback').textContent=button.dataset.demoAction+'：已触发演示反馈。'));
window.addEventListener('resize',()=>{if(!byId('analysisView').hidden)renderChart(filtered());});
render();
