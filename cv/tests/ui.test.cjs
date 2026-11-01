const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
function harness() {
  const elements=new Map();
  function element(id) {
    if(!elements.has(id))elements.set(id,{value:'',checked:true,disabled:false,hidden:false,textContent:'',children:[],width:960,height:540,
      append(x){this.children.push(x)},replaceChildren(){this.children=[]},
      insertRow(){const row={cells:[],insertCell(){const cell={};this.cells.push(cell);return cell}};this.children.push(row);return row},
      getContext(){return {clearRect(){},drawImage(){},strokeRect(){},fillRect(){},fillText(){},beginPath(){},moveTo(){},lineTo(){},stroke(){},measureText(){return {width:20}}}}});
    return elements.get(id);
  }
  const context=vm.createContext({document:{getElementById:element,createElement:()=>({})},
    fetch:async()=>({ok:true,json:async()=>({device:'cpu',model_available:true})}),
    setTimeout(){},clearTimeout(){},console,Date,FormData,JSON,
    Image:class{set src(value){this.width=100;this.height=100;this.onload()}}});
  vm.runInContext(fs.readFileSync(path.join(__dirname,'../static/app.js'),'utf8'),context);
  return {element,run:code=>vm.runInContext(code,context)};
}
test('manual comparison freezes displayed frame and handles zero denominator',()=>{
  const h=harness();h.run('displayRecord={frame_index:12,people_count:2}');h.element('manual').value='0';
  h.element('compare-form').onsubmit({preventDefault(){}});
  assert.match(h.element('comparison').textContent,/Frame 12/);
  assert.match(h.element('comparison').textContent,/mẫu số 0/);
  assert.equal(h.run('paused'),true);
  h.element('manual').value='4';h.element('compare-form').onsubmit({preventDefault(){}});
  assert.match(h.element('comparison').textContent,/50.00%/);
});
test('no frame comparison gives clear message',()=>{
  const h=harness();h.element('compare-form').onsubmit({preventDefault(){}});
  assert.match(h.element('message').textContent,/Chưa có khung hình/);
});
test('frame shows real zero, null counters and underflow warning',()=>{
  const h=harness();h.run(`showRecord({frame_width:100,frame_height:100,detections:[],people_count:0,in_count:null,out_count:null,estimated_occupancy:null,occupancy_underflow:false,timestamp_ms:0,frame_index:0,processing_ms:20},{width:100,height:100})`);
  assert.equal(h.element('people').textContent,0);
  assert.equal(h.element('in').textContent,'—');
  assert.equal(h.element('fps').textContent,'50.0');
  h.run(`showRecord({...displayRecord,estimated_occupancy:0,occupancy_underflow:true},image)`);
  assert.match(h.element('occupancy-note').textContent,/Cảnh báo/);
});
test('cancelled session exposes exports and enables new run',async()=>{
  const h=harness();h.run(`job='abc'; fetch=async()=>({ok:true,json:async()=>({status:'cancelled',latest:null,events:[]})})`);
  await h.run('poll()');
  assert.equal(h.element('start').disabled,false);
  assert.equal(h.element('stop').disabled,true);
  assert.equal(h.element('downloads').children.length,4);
  assert.match(h.element('result-status').textContent,/một phần/);
});
