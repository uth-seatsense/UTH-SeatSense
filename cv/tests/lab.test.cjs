const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {JSDOM}=require('jsdom');
function setup() {
  const dom=new JSDOM(fs.readFileSync(path.join(__dirname,'../static/index.html'),'utf8'),{url:'http://localhost:8001',runScripts:'outside-only'});
  const w=dom.window;
  w.HTMLCanvasElement.prototype.getContext=()=>({clearRect(){},drawImage(){},strokeRect(){},fillRect(){},fillText(){},beginPath(){},moveTo(){},lineTo(){},stroke(){},measureText(){return {width:20}}});
  w.fetch=async()=>({ok:true,json:async()=>({device:'cpu',model_available:true})});
  w.eval(fs.readFileSync(path.join(__dirname,'../static/lab.js'),'utf8'));
  return {w,dom,button:text=>[...w.document.querySelectorAll('button')].find(n=>n.textContent.trim()===text||n.lastElementChild?.textContent.trim()===text)};
}
test('original template initializes, disables RTSP, and can select webcam',()=>{
  const {w,dom,button}=setup();
  assert.equal(button('Live RTSP Stream').disabled,true);
  assert.equal(button('Stop Test').disabled,true);
  button('USB Webcam').click();
  assert.match(w.document.getElementById('lab-status').textContent,/USB Webcam/);
  assert.equal(w.document.querySelectorAll('img[data-alt]').length,0);
  assert.equal(w.document.querySelectorAll('canvas').length,1);
  dom.window.close();
});
test('missing camera support is reported and start is re-enabled',async()=>{
  const {w,dom,button}=setup();button('Start Test').click();
  await new Promise(resolve=>setImmediate(resolve));
  assert.match(w.document.getElementById('lab-status').textContent,/Webcam cần localhost/);
  assert.equal(button('Start Test').disabled,false);
  dom.window.close();
});
test('comparison and snapshots require a real displayed frame',()=>{
  const {w,dom,button}=setup();button('Compare Accuracy').click();
  assert.match(w.document.getElementById('lab-status').textContent,/Chưa có frame/);
  button('Snapshot').click();
  assert.match(w.document.getElementById('lab-status').textContent,/Chưa có frame/);
  dom.window.close();
});
test('real-record rendering updates template and manual comparison',()=>{
  const {w,dom,button}=setup();
  const image=w.document.createElement('canvas');image.width=100;image.height=100;
  w.show({people_count:2,in_count:1,out_count:0,processing_ms:20,frame_index:3,timestamp_ms:300,frame_width:100,frame_height:100,detections:[]},image);
  assert.equal(w.document.querySelector('span.font-metric-stat').textContent,'2');
  w.document.querySelector('input[value="76"]').value='4';
  button('Compare Accuracy').click();
  assert.match(w.document.getElementById('lab-status').textContent,/frame 3/);
  assert.ok([...w.document.querySelectorAll('span')].some(n=>n.textContent==='50.00%'));
  dom.window.close();
});
