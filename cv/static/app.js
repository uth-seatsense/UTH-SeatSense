const $ = id => document.getElementById(id);
const labels = {uploading:'Đang tải video',loading:'Đang tải model',processing:'Đang xử lý',completed:'Hoàn tất',cancelled:'Đã dừng · kết quả một phần',failed:'Lỗi xử lý'};
let job = null, paused = false, displayRecord = null, image = null, activeLine = null, timer = null;
const terminal = new Set(['completed','cancelled','failed']);
async function api(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) { const error = await response.json().catch(()=>({})); throw new Error(typeof error.detail === 'string' ? error.detail : `Yêu cầu thất bại (${response.status})`); }
  return response.json();
}
function notice(text) { $('message').textContent=text; $('message').hidden=!text; }
function busy(value) { $('settings').disabled=value; $('start').disabled=value; $('stop').disabled=!value; }
$('confidence').oninput=()=>{$('confidence-value').textContent=Number($('confidence').value).toFixed(2);};
$('line-enabled').onchange=()=>{$('line-settings').hidden=!$('line-enabled').checked;};
function draw() {
  if (!image || !displayRecord) return;
  const canvas=$('canvas'), ctx=canvas.getContext('2d'), record=displayRecord;
  canvas.width=image.width; canvas.height=image.height; ctx.drawImage(image,0,0);
  const sx=canvas.width/record.frame_width, sy=canvas.height/record.frame_height;
  ctx.lineWidth=2; ctx.font='13px monospace';
  if ($('show-line').checked && activeLine) {
    ctx.strokeStyle='#4fe1ed';ctx.beginPath();ctx.moveTo(activeLine[0]*canvas.width,activeLine[1]*canvas.height);ctx.lineTo(activeLine[2]*canvas.width,activeLine[3]*canvas.height);ctx.stroke();
  }
  for(const item of record.detections) {
    const [x1,y1,x2,y2]=item.bbox_xyxy, x=x1*sx,y=y1*sy;
    ctx.strokeStyle=item.track_id===null?'#ffc46b':'#5ee1a7';
    if($('boxes').checked)ctx.strokeRect(x,y,(x2-x1)*sx,(y2-y1)*sy);
    const text=[$('ids').checked?(item.track_id===null?'new':`#${item.track_id}`):'', $('scores').checked?`${(item.confidence*100).toFixed(1)}%`:''].filter(Boolean).join(' ');
    if(text){ctx.fillStyle='#11283b';ctx.fillRect(x,Math.max(0,y-20),ctx.measureText(text).width+10,20);ctx.fillStyle='#fff';ctx.fillText(text,x+4,Math.max(14,y-5));}
  }
  $('empty').hidden=true;
}
for (const id of ['boxes','ids','scores','show-line']) $(id).onchange=draw;
$('pause').onclick=()=>{paused=!paused;$('pause').textContent=paused?'Tiếp tục xem':'Tạm dừng xem';if(!paused && job && !$('settings').disabled)poll();};
function showRecord(record, picture) {
  displayRecord=record;image=picture;draw();
  $('people').textContent=record.people_count;$('in').textContent=record.in_count??'—';$('out').textContent=record.out_count??'—';
  $('occupancy').textContent=record.estimated_occupancy??'—';
  $('occupancy-note').textContent=record.occupancy_underflow?'Cảnh báo: số lượt ra vượt số có sẵn':record.estimated_occupancy===null?'Chưa biết số người ban đầu':'Số ban đầu + IN − OUT';
  $('time').textContent=`${(record.timestamp_ms/1000).toFixed(2)} s · ${record.frame_index+1} frame`;
  $('fps').textContent=record.processing_ms>0?(1000/record.processing_ms).toFixed(1):'—';
  $('latency').textContent=`${record.processing_ms.toFixed(1)} ms / frame · detector + tracker`;
  $('compare-frame').textContent=`Frame ${record.frame_index} · ${(record.timestamp_ms/1000).toFixed(2)} s`;
}
async function poll() {
  if(!job)return;
  try {
    const state=await api(`/api/jobs/${job}`);$('status').textContent=labels[state.status]||state.status;
    if(state.latest && !paused) {
      const picture=await new Promise((resolve,reject)=>{const img=new Image();img.onload=()=>resolve(img);img.onerror=reject;img.src=`data:image/jpeg;base64,${state.frame_image}`;});
      showRecord(state.latest,picture);
    }
    $('events').replaceChildren();
    if(!state.events.length){const row=$('events').insertRow();const cell=row.insertCell();cell.colSpan=4;cell.textContent='Chưa có sự kiện.';}
    for(const event of [...state.events].reverse()) { const row=$('events').insertRow();for(const value of [(event.timestamp_ms/1000).toFixed(2)+' s',`#${event.track_id}`,event.direction,(event.confidence*100).toFixed(1)+'%'])row.insertCell().textContent=value; }
    if(terminal.has(state.status)) {
      busy(false);$('result-status').textContent=labels[state.status];
      if(state.error)notice(state.error);
      if(state.status!=='failed') {
        $('downloads').replaceChildren();
        for(const [kind,label] of [['csv','CSV'],['jsonl','JSONL số đếm'],['events','JSONL sự kiện'],['summary','Tóm tắt JSON']]){const a=document.createElement('a');a.className='download';a.href=`/api/jobs/${job}/files/${kind}`;a.textContent=label;$('downloads').append(a);}
      }
      return;
    }
  } catch(error) { notice(error.message || 'Không lấy được khung hình. Đang thử lại…'); }
  timer=setTimeout(poll,500);
}
$('form').onsubmit=async event=>{
  event.preventDefault();notice('');const file=$('file').files[0];if(!file)return;
  if(file.size>200*1024*1024){notice('Video vượt giới hạn 200 MB.');return;}
  const options={confidence:Number($('confidence').value),camera_id:$('camera').value.trim(),room_id:$('room').value.trim()||null};
  activeLine=$('line-enabled').checked?['x1','y1','x2','y2'].map(id=>Number($(id).value)):null;
  if(activeLine){options.line=activeLine;options.in_direction=$('direction').value;if($('initial').value!=='')options.initial_occupancy=Number($('initial').value);}
  const data=new FormData();data.append('file',file);data.append('options',JSON.stringify(options));
  clearTimeout(timer);busy(true);$('stop').disabled=true;$('status').textContent='Đang tải video';job=null;paused=false;displayRecord=null;image=null;
  $('empty').hidden=false;$('canvas').getContext('2d').clearRect(0,0,$('canvas').width,$('canvas').height);
  for(const id of ['people','in','out','occupancy','fps'])$(id).textContent='—';
  $('comparison').textContent='Chưa có phép so sánh.';$('downloads').textContent='Đang chờ kết quả.';$('result-status').textContent='Đang chạy';
  $('pause').disabled=false;$('pause').textContent='Tạm dừng xem';
  try{const state=await api('/api/jobs',{method:'POST',body:data});job=state.id;$('stop').disabled=false;await poll();}catch(error){notice(error.message);busy(false);$('status').textContent='Không khởi động được';}
};
$('stop').onclick=async()=>{if(!job)return;try{await api(`/api/jobs/${job}/stop`,{method:'POST'});$('stop').disabled=true;$('status').textContent='Đang dừng…';}catch(error){notice(error.message);}};
$('compare-form').onsubmit=event=>{event.preventDefault();if(!displayRecord){notice('Chưa có khung hình để so sánh.');return;}paused=true;$('pause').textContent='Tiếp tục xem';const manual=Number($('manual').value),count=displayRecord.people_count,error=Math.abs(count-manual);$('comparison').textContent=`Frame ${displayRecord.frame_index}: AI ${count}, đếm tay ${manual}. Sai số tuyệt đối: ${error}; sai số tương đối: ${manual===0?'không xác định (mẫu số 0)':(error/manual*100).toFixed(2)+'%'}.`;};
api('/api/config').then(config=>{$('device').textContent=`YOLOv8n + ByteTrack · ${config.device}`;if(!config.model_available)notice('Chưa có model. Tải best.pt theo README và đặt vào cv/models/, hoặc cấu hình CV_MODEL_PATH.');}).catch(error=>notice(error.message));
