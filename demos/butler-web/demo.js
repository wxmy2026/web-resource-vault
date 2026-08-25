const $=id=>document.getElementById(id);
const state={days:7,apple:false,spotify:false,ctx:null,master:null,timer:null,nodes:[]};
const saved=JSON.parse(localStorage.getItem('butler-demo')||'{}');
['enabled','active','quiet','appleFail'].forEach(k=>{if(typeof saved[k]==='boolean')$(k).checked=saved[k]});
if(saved.time)$('time').value=saved.time;if(saved.days)state.days=saved.days;if(saved.apple)state.apple=true;if(saved.spotify)state.spotify=true;
function persist(){localStorage.setItem('butler-demo',JSON.stringify({enabled:$('enabled').checked,active:$('active').checked,quiet:$('quiet').checked,appleFail:$('appleFail').checked,time:$('time').value,days:state.days,apple:state.apple,spotify:state.spotify}))}
function stamp(){return new Date().toLocaleTimeString('zh-CN',{hour:'2-digit',minute:'2-digit',second:'2-digit'})}
function log(msg){$('decision').textContent=msg;const d=document.createElement('div');d.textContent=`${stamp()}  ${msg}`;$('log').prepend(d)}
function render(){ $('heroTime').textContent=$('time').value||'08:00';$('heroStatus').textContent=`轻柔音乐 · ${$('enabled').checked?'已开启':'已关闭'} · 剩余 ${state.days} 天${$('quiet').checked?' · 今天安静':''}`;$('appleText').textContent=state.apple?'Demo：已连接':'Demo：未连接';$('spotifyText').textContent=state.spotify?'Demo：已连接':'Demo：未连接';$('apple').textContent=state.apple?'断开':'模拟连接';$('spotify').textContent=state.spotify?'断开':'模拟连接';persist()}
['enabled','active','quiet','appleFail','time'].forEach(id=>$(id).addEventListener('change',()=>{render();log(`${id==='time'?'时间已改为 '+$('time').value:'设置已更新'}`)}));
$('renew').onclick=()=>{state.days=7;$('enabled').checked=true;$('quiet').checked=false;render();log('计划已续 7 天。')};
$('apple').onclick=()=>{state.apple=!state.apple;render();log(state.apple?'Apple Music 演示连接成功。':'Apple Music 已断开。')};
$('spotify').onclick=()=>{state.spotify=!state.spotify;render();log(state.spotify?'Spotify 演示连接成功。':'Spotify 已断开。')};
$('clearLog').onclick=()=>{$('log').innerHTML='';$('decision').textContent='等待你的操作。'};

function ensureAudio(){if(!state.ctx){const AC=window.AudioContext||window.webkitAudioContext;state.ctx=new AC();state.master=state.ctx.createGain();state.master.gain.value=+$('volume').value;state.master.connect(state.ctx.destination)}if(state.ctx.state==='suspended')state.ctx.resume()}
function tone(freq,start,dur,vol=.035,type='sine'){const o=state.ctx.createOscillator(),g=state.ctx.createGain();o.type=type;o.frequency.value=freq;g.gain.setValueAtTime(0,start);g.gain.linearRampToValueAtTime(vol,start+.35);g.gain.exponentialRampToValueAtTime(.0001,start+dur);o.connect(g);g.connect(state.master);o.start(start);o.stop(start+dur+.05);state.nodes.push(o)}
const chords=[[261.63,329.63,392,493.88],[220,261.63,329.63,392],[174.61,220,261.63,329.63],[196,246.94,293.66,329.63]];
let chordIndex=0;
function scheduleChord(){if(!state.ctx)return;const now=state.ctx.currentTime+.05;const chord=chords[chordIndex%chords.length];chord.forEach((f,i)=>{tone(f,now,5.8,.022-i*.002,'sine');tone(f/2,now,5.8,.009,'triangle')});tone(chord[(chordIndex+1)%chord.length]*2,now+.7,2.4,.018,'sine');tone(chord[(chordIndex+2)%chord.length]*2,now+3.1,2.2,.014,'sine');chordIndex++}
function play(){ensureAudio();stop(false);ensureAudio();scheduleChord();state.timer=setInterval(scheduleChord,5600);$('pulse').classList.add('playing');$('audioStatus').textContent='正在播放：浏览器实时合成的柔和晨间音乐';log('开始播放真实测试音乐。')}
function stop(write=true){if(state.timer){clearInterval(state.timer);state.timer=null}state.nodes.forEach(n=>{try{n.stop()}catch(e){}});state.nodes=[];$('pulse').classList.remove('playing');$('audioStatus').textContent='音乐已停止';if(write)log('音乐已停止。')}
$('play').onclick=play;$('stop').onclick=()=>stop(true);$('volume').oninput=()=>{if(state.master)state.master.gain.setTargetAtTime(+$('volume').value,state.ctx.currentTime,.05)};
$('simulate').onclick=()=>{if(!$('enabled').checked){stop(false);return log('08:00：早晨音乐已关闭，保持安静。')}if($('quiet').checked){stop(false);return log('08:00：今天设置为安静，不播放。')}if($('active').checked){stop(false);return log('08:00：检测状态显示你已经在使用 iPad，保持安静。')}if(state.apple&&!$('appleFail').checked){play();return log('08:00：正式版将优先用 Apple Music 个性化播放；Demo 现在播放真实测试音乐。')}if(state.spotify){play();return log('08:00：Apple Music 不可用，正式版切到 Spotify；Demo 现在播放真实测试音乐。')}play();log('08:00：在线服务不可用，启动本地柔和音乐兜底。')};
render();