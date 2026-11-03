/* Desktop adapter. In a normal browser the existing web application is unchanged. */
(() => {
  if (!window.__TAURI__) return;
  const invoke = window.__TAURI__.core.invoke;
  window.addEventListener('error',event=>invoke('ui_report',{kind:'error',message:String(event.message)}).catch(()=>{}));
  window.addEventListener('unhandledrejection',event=>invoke('ui_report',{kind:'error',message:String(event.reason)}).catch(()=>{}));
  const es = () => localStorage.getItem('voz-local-language') === 'es';
  const text = (en, spanish) => es() ? spanish : en;
  const $ = id => document.getElementById(id);
  let unlock, info, working = false, firstReady = false;
  const bridge = window.VozDesktop = {active:true, sample:null, ready:new Promise(resolve => {unlock=resolve;})};
  document.documentElement.dataset.desktop = 'true';
  const overlay = document.createElement('div');
  overlay.className = 'desktop-setup';
  overlay.innerHTML = `<div class="desktop-setup-card" role="dialog" aria-modal="true" aria-labelledby="dt-title">
    <div class="desktop-brand">◖ Voz Local <small>Desktop</small></div>
    <h1 id="dt-title"></h1><p id="dt-intro"></p>
    <label id="dt-language-label" for="dt-language"></label><select id="dt-language"><option value="en">English</option><option value="es">Español</option></select>
    <label id="dt-profile-label" for="dt-profile"></label><select id="dt-profile"><option value="cpu">CPU</option><option value="cuda">NVIDIA · CUDA</option><option value="rocm">AMD RX 9060 XT · Linux ROCm</option></select>
    <label id="dt-model-label" for="dt-model"></label><select id="dt-model"><option value="1.7B">Qwen3-TTS 1.7B · Quality</option><option value="0.6B">Qwen3-TTS 0.6B · Lighter</option></select><p id="dt-size" class="field-help"></p>
    <button type="button" class="button secondary" id="dt-model-folder"></button><p id="dt-model-folder-path" class="field-help"></p>
    <p id="dt-explanation" class="field-help"></p><p class="desktop-progress" id="dt-progress" role="status" aria-live="polite"></p>
    <progress id="dt-progress-bar" hidden></progress><p id="dt-error" class="desktop-error" role="alert" hidden></p>
    <div class="desktop-setup-actions"><button class="button primary" type="button" id="dt-install"></button><button class="button secondary" type="button" id="dt-restart"></button><button class="button secondary" type="button" id="dt-later" hidden></button></div>
  </div>`;
  document.body.append(overlay);
  $('instalacion').innerHTML = `<div class="section-title"><div><h1 id="dt-settings-title"></h1><p id="dt-settings-subtitle"></p></div></div>
    <div class="panel"><h2 id="dt-engine-title"></h2><p id="dt-runtime"></p><div class="desktop-settings-buttons">
      <button type="button" class="button primary" id="dt-open-setup"></button><button type="button" class="button secondary" id="dt-import"></button><button type="button" class="button secondary" id="dt-open-data"></button><button type="button" class="button secondary" id="dt-show-logs"></button>
    </div><p id="dt-import-help" class="field-help"></p><p id="dt-settings-status" role="status"></p><pre id="dt-logs" hidden></pre></div>`;
  const nav = document.querySelector('[data-view="instalacion"] span:last-child');
  nav.removeAttribute('data-i18n');
  const upload = $('voice-file');
  upload.hidden = true; document.querySelector('label[for="voice-file"]').hidden = true;
  const choose = document.createElement('button'); choose.className='button secondary';choose.type='button';choose.id='dt-choose-sample';upload.parentElement.append(choose);
  const selected = document.createElement('p');selected.className='field-help';selected.id='dt-chosen-sample';upload.parentElement.append(selected);
  bridge.localize = () => {
    const labels = {
      'dt-title':['Welcome to Voz Local','Bienvenido a Voz Local'],
      'dt-intro':['Prepare your voice engine once. Your recordings stay on this computer.','Prepara el motor una vez. Tus grabaciones se guardan en este equipo.'],
      'dt-language-label':['Interface language','Idioma de la interfaz'],
      'dt-profile-label':['Processing device','Dispositivo para generar'],
      'dt-model-label':['Voice model','Modelo de voz'],
      'dt-model-folder':['Reuse downloaded models…','Reutilizar modelos descargados…'],
      'dt-explanation':['Python, voice libraries and the selected model are downloaded when needed. GPU drivers must already be installed. CPU is slower. No terminal is required.','Python, las bibliotecas y el modelo se descargan si faltan. Los controladores de GPU deben estar instalados. CPU es más lento. No necesitas terminal.'],
      'dt-install':['Prepare and start','Preparar e iniciar'],
      'dt-restart':['Start / restart existing engine','Iniciar / reiniciar motor existente'],
      'dt-later':['Back to my project','Volver a mi proyecto'],
      'dt-settings-title':['Settings','Ajustes'],
      'dt-settings-subtitle':['Voice engine, storage and diagnostics.','Motor de voz, almacenamiento y diagnóstico.'],
      'dt-engine-title':['Local engine','Motor local'],
      'dt-open-setup':['Configure engine','Configurar motor'],
      'dt-import':['Import previous installation…','Importar instalación anterior…'],
      'dt-open-data':['Open data folder','Abrir carpeta de datos'],
      'dt-show-logs':['Show diagnostics','Ver diagnóstico'],
      'dt-import-help':['Import requires an empty desktop library. Choose the old data folder. The original installation is kept; existing model weights are reused without copying them.','La importación requiere una biblioteca de escritorio vacía. Elige la carpeta data anterior. Se conserva la instalación original y se reutilizan los modelos sin copiarlos.'],
      'dt-choose-sample':['Upload audio…','Subir audio…']
    };
    for(const [id,values] of Object.entries(labels)) $(id).textContent=text(...values);
    nav.textContent=text('Settings','Ajustes');
    $('dt-language').value=es()?'es':'en';
    if(location.hash==='#instalacion')document.title=`Voz Local · ${nav.textContent}`;
  };
  const fail = error => { $('dt-error').hidden=false;$('dt-error').textContent=String(error); };
  function progress(value) {
    const labels={python:['Preparing Python','Preparando Python'],dependencies:['Installing voice libraries','Instalando bibliotecas de voz'],device:['Checking PyTorch computation','Comprobando PyTorch'],model:['Downloading / checking model','Descargando / comprobando modelo'],starting:['Starting voice engine','Iniciando motor'],ready:['Engine ready','Motor preparado']};
    $('dt-progress').textContent=(labels[value.phase]?text(...labels[value.phase]):'')+(value.total?` · ${value.current}/${value.total} ${value.unit||''}`:'');
    $('dt-progress-bar').hidden=!working;
    if(value.total){$('dt-progress-bar').max=value.total;$('dt-progress-bar').value=value.current;}else $('dt-progress-bar').removeAttribute('value');
    if(value.phase==='error') {fail(value.message);overlay.hidden=false;}
  }
  async function refresh() {
    info=await invoke('desktop_info');
    $('dt-runtime').textContent=`${info.settings.profile.toUpperCase()} · Qwen3-TTS ${info.settings.model} · ${info.data_dir}`;
    $('dt-restart').disabled=!info.installed;
    $('dt-later').hidden=!info.running;
    $('dt-import').disabled=!info.installed;
    return info;
  }
  async function size() {
    $('dt-size').textContent=text('Checking download size…','Consultando tamaño de descarga…');
    const model=$('dt-model').value;
    try {const bytes=await invoke('model_size',{model});if($('dt-model').value===model)$('dt-size').textContent=bytes?`${text('Model files','Archivos del modelo')}: ${(bytes/1024**3).toFixed(2)} GB · ${text('dependencies need additional space','las dependencias necesitan espacio adicional')}`:text('Size unavailable. Internet is needed on first setup.','Tamaño no disponible. La primera preparación necesita internet.');}
    catch{$('dt-size').textContent=text('Size unavailable offline. Existing complete models can be reused.','Tamaño no disponible sin conexión. Puedes reutilizar modelos completos descargados.');}
  }
  async function start(prepare) {
    if(working)return;
    working=true;$('dt-error').hidden=true;$('dt-install').disabled=true;$('dt-restart').disabled=true;
    for(const id of ['dt-profile','dt-model','dt-model-folder','dt-later'])$(id).disabled=true;
    try {
      if(prepare)await invoke('prepare_engine',{profile:$('dt-profile').value,model:$('dt-model').value});
      else await invoke('restart_engine');
      overlay.hidden=true;await refresh();unlock();
      if(firstReady)document.dispatchEvent(new Event('desktop-engine-ready'));
      firstReady=true;
    }catch(error){fail(error);}
    finally {working=false;$('dt-progress-bar').hidden=true;$('dt-install').disabled=false;
      for(const id of ['dt-profile','dt-model','dt-model-folder','dt-later'])$(id).disabled=false;
      await refresh().catch(()=>{});
    }
  }
  $('dt-install').onclick=()=>start(true);$('dt-restart').onclick=()=>start(false);
  $('dt-open-setup').onclick=async()=>{overlay.hidden=false;await refresh();};
  $('dt-later').onclick=()=>{overlay.hidden=true;};
  $('dt-language').onchange=()=>{$('language-select').value=$('dt-language').value;$('language-select').dispatchEvent(new Event('change'));bridge.localize();size();};
  $('language-select').addEventListener('change',()=>bridge.localize());
  $('dt-model').onchange=size;
  $('dt-model-folder').onclick=async()=>{try{const path=await invoke('choose_models');if(path)$('dt-model-folder-path').textContent=path;}catch(e){fail(e);}};
  $('dt-open-data').onclick=()=>invoke('open_data').catch(e=>{$('dt-settings-status').textContent=String(e);});
  $('dt-show-logs').onclick=async()=>{try{$('dt-logs').textContent=await invoke('diagnostics');$('dt-logs').hidden=false;}catch(e){$('dt-settings-status').textContent=String(e);}};
  $('dt-import').onclick=async()=>{if(working)return;working=true;$('dt-import').disabled=true;try{if(await invoke('import_legacy')){$('dt-settings-status').textContent=text('Imported. Your original installation is unchanged.','Importado. La instalación original se conserva.');document.dispatchEvent(new Event('desktop-engine-ready'));await refresh();}}catch(e){$('dt-settings-status').textContent=String(e);}finally{working=false;$('dt-import').disabled=false;}};
  choose.onclick=async()=>{try{const sample=await invoke('choose_sample');if(sample){bridge.sample=sample;$('dt-chosen-sample').textContent=sample.name;$('record-preview').src=bridge.media('/sample/'+sample.id);$('record-preview').hidden=false;}}catch(e){$('dt-chosen-sample').textContent=String(e);}};
  bridge.request=async(path,options={})=> {
    try {
      if(options.body instanceof FormData && path==='/api/voices')return await invoke('upload_voice',{name:options.body.get('name'),transcript:options.body.get('transcript'),sampleId:bridge.sample?.id});
      let timer, stopped=false;
      const node=$('generation-progress'), previous=node?.textContent||'', start=Date.now();
      if(path.endsWith('/generate')) timer=setInterval(async()=>{
        try {
          const status=await invoke('api_request',{method:'GET',path:'/api/desktop/progress',body:null});
          const labels={loading:['Loading model','Cargando modelo'],downloading:['Downloading model','Descargando modelo'],generating:['Generating audio','Generando audio'],idle:['Preparing audio','Preparando audio']};
          if(!stopped && node)node.textContent=[previous,text(...(labels[status.phase]||labels.idle)),`${Math.floor((Date.now()-start)/1000)} s`].filter(Boolean).join(' · ');
        }catch{}
      },1000);
      try{return await invoke('api_request',{method:options.method||'GET',path,body:options.body?JSON.parse(options.body):null});}
      finally{stopped=true;if(timer){clearInterval(timer);if(node)node.textContent=previous;}}
    } catch(error) { throw new Error(typeof error==='string'?error:error.message||String(error)); }
  };
  bridge.appError=error=>invoke('ui_report',{kind:'error',message:String(error.message||error)}).catch(()=>{});
  bridge.appReady=async()=>{
    await invoke('ui_report',{kind:'ready',message:'Desktop project UI loaded from authenticated engine'});
    if(!info.smoke_media)return;
    const player=document.querySelector('#chunk-list audio');
    if(!player)throw new Error('Native media smoke requires an existing project audio');
    player.muted=true;
    await new Promise((resolve,reject)=>{
      const timer=setTimeout(()=>reject(new Error('Native audio metadata timed out')),10000);
      player.onloadedmetadata=()=>{clearTimeout(timer);resolve();};
      player.onerror=()=>{clearTimeout(timer);reject(new Error('Native audio protocol error: '+(player.error?.message||player.error?.code)));};
      player.preload='metadata';player.load();
    });
    await invoke('ui_report',{kind:'ready',message:'Native media metadata loaded'});
    if(!Number.isFinite(player.duration)||player.duration<=0)throw new Error('Invalid native audio duration');
    await new Promise((resolve,reject)=>{
      const timer=setTimeout(()=>reject(new Error('Native seeking timed out')),10000);
      player.onseeked=()=>{clearTimeout(timer);resolve();};
      player.currentTime=Math.min(.25,player.duration/2);
    });
    await invoke('ui_report',{kind:'ready',message:'Desktop media protocol decoded WAV and seeked'});
  };
  bridge.media=path=>info ? info.media_origin+path : path;
  bridge.export=async(project,format)=>{try{return await invoke('export_audio',{projectId:project.id,format,title:project.title});}catch(e){throw new Error(String(e));}};
  bridge.record=async(state,t,message)=> {
    try {
      await invoke('recording_start');state.recordedFile=null;bridge.sample=null;state.seconds=0;
      state.recorder={stop:async()=>{
        $('stop-button').disabled=true;
        try {bridge.sample=await invoke('recording_stop');$('record-preview').src=bridge.media('/sample/'+bridge.sample.id);$('record-preview').hidden=false;$('dt-chosen-sample').textContent=bridge.sample.name;}
        catch(e){message(String(e),true);}
        finally{clearInterval(state.timer);$('record-button').hidden=false;$('stop-button').hidden=true;$('stop-button').disabled=false;$('record-timer').textContent=t('sampleRecorded',{seconds:state.seconds});state.recorder=null;}
      }};
      $('record-button').hidden=true;$('stop-button').hidden=false;$('record-timer').textContent=t('recording',{seconds:0});
      state.timer=setInterval(()=>{state.seconds++;$('record-timer').textContent=t('recording',{seconds:state.seconds});if(state.seconds>=60)state.recorder?.stop();},1000);
    }catch(e){message(`${t('micError')} ${String(e)}`,true);}
  };
  document.addEventListener('click',event=>{const link=event.target.closest('a[href]');if(!link)return;if(/^https?:/.test(link.href)&&!link.getAttribute('href').startsWith('#')){event.preventDefault();invoke('open_external',{url:link.href}).catch(fail);}});
  window.addEventListener('hashchange',()=>bridge.localize());
  bridge.localize();
  window.__TAURI__.event.listen('desktop-progress',event=>progress(event.payload)).catch(fail);
  refresh().then(result=>{
    invoke('ui_report',{kind:'ready',message:'Desktop interface loaded and IPC connected'}).catch(()=>{});
    $('dt-profile').value=result.installed?result.settings.profile:result.recommended_profile;
    $('dt-model').value=result.installed?result.settings.model:result.recommended_profile==='cpu'?'0.6B':'1.7B';
    $('dt-model-folder-path').textContent=result.settings.models_dir||'';
    if(result.installed)start(false);size();
  }).catch(fail);
})();
