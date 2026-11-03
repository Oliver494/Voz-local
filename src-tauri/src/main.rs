#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
mod gateway;
mod process;
mod recording;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::{
    collections::HashMap,
    fs::{self, File},
    io::{BufRead, BufReader, Read, Seek, SeekFrom, Write},
    path::{Path, PathBuf},
    process::{Command, Stdio},
    sync::{
        atomic::{AtomicBool, AtomicUsize, Ordering},
        Arc, Mutex,
    },
    time::Duration,
};
use tauri::{Emitter, Manager};
use tauri_plugin_dialog::{DialogExt, MessageDialogButtons, MessageDialogKind};
use tauri_plugin_opener::OpenerExt;
use uuid::Uuid;

#[derive(Clone, Serialize, Deserialize)]
struct Settings {
    profile: String,
    model: String,
    #[serde(default)]
    models_dir: Option<String>,
}
impl Default for Settings {
    fn default() -> Self {
        Self {
            profile: "cpu".into(),
            model: "1.7B".into(),
            models_dir: None,
        }
    }
}
struct Engine {
    process: process::Process,
    base: String,
    token: String,
}
struct Desktop {
    root: PathBuf,
    resources: PathBuf,
    client: reqwest::blocking::Client,
    engine: Mutex<Option<Engine>>,
    setup_process: Mutex<Option<process::Process>>,
    progress: Mutex<Value>,
    samples: Mutex<HashMap<String, PathBuf>>,
    recording: Mutex<Option<recording::Recording>>,
    settings: Mutex<Settings>,
    preparing: AtomicBool,
    busy: AtomicUsize,
    media_origin: Mutex<String>,
    closing: AtomicBool,
}
type State<'a> = tauri::State<'a, Arc<Desktop>>;
fn error(e: impl std::fmt::Display) -> String {
    e.to_string()
}
fn binary(resources: &Path, name: &str) -> PathBuf {
    resources.join("tools").join(if cfg!(windows) {
        format!("{name}.exe")
    } else {
        name.into()
    })
}
fn python(root: &Path) -> PathBuf {
    root.join("environment").join(if cfg!(windows) {
        "Scripts/python.exe"
    } else {
        "bin/python"
    })
}
fn report(app: &tauri::AppHandle, state: &Desktop, value: Value) {
    *state.progress.lock().unwrap() = value.clone();
    let _ = app.emit("desktop-progress", &value);
}
fn runtime_env(state: &Desktop, command: &mut Command) {
    command
        .current_dir(&state.root)
        .env("UV_PYTHON_INSTALL_DIR", state.root.join("python"))
        .env("UV_PYTHON_PREFERENCE", "only-managed")
        .env("UV_NO_PROGRESS", "1")
        .env("VOZ_LOCAL_DATA_DIR", &state.root)
        .env("PYTHONUNBUFFERED", "1")
        .env("VOZ_LOCAL_PARENT_PID", std::process::id().to_string())
        .env("TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL", "1");
    let ffmpeg = std::env::var_os("VOZ_LOCAL_FFMPEG")
        .map(PathBuf::from)
        .unwrap_or_else(|| binary(&state.resources, "ffmpeg"));
    command.env("VOZ_LOCAL_FFMPEG", &ffmpeg);
    let mut path = vec![ffmpeg.parent().unwrap().to_path_buf()];
    path.extend(std::env::split_paths(
        &std::env::var_os("PATH").unwrap_or_default(),
    ));
    if let Ok(path) = std::env::join_paths(path) {
        command.env("PATH", path);
    }
    let settings = state.settings.lock().unwrap().clone();
    command.env("VOZ_LOCAL_DEFAULT_MODEL", settings.model).env(
        "VOZ_LOCAL_DEVICE",
        if settings.profile == "cpu" {
            "cpu"
        } else {
            "cuda"
        },
    );
    process::hide(command);
}
fn backend_script(state: &Desktop, name: &str) -> PathBuf {
    state.resources.join("backend/scripts/desktop").join(name)
}
fn save_settings(state: &Desktop) -> Result<(), String> {
    let temp = state.root.join("desktop-settings.tmp");
    fs::write(
        &temp,
        serde_json::to_vec(&*state.settings.lock().unwrap()).map_err(error)?,
    )
    .map_err(error)?;
    // Rename cannot replace on some Windows filesystems; back up the old config first.
    let destination = state.root.join("desktop-settings.json");
    let backup = state.root.join("desktop-settings.previous.json");
    if destination.exists() {
        if backup.exists() {
            fs::remove_file(&backup).map_err(error)?;
        }
        fs::rename(&destination, &backup).map_err(error)?;
    }
    if let Err(e) = fs::rename(&temp, &destination) {
        let _ = fs::rename(&backup, &destination);
        return Err(error(e));
    }
    Ok(())
}
fn run_progress(
    app: &tauri::AppHandle,
    state: &Desktop,
    mut command: Command,
) -> Result<(), String> {
    runtime_env(state, &mut command);
    let logs = File::options()
        .append(true)
        .create(true)
        .open(state.root.join("logs/setup.log"))
        .map_err(error)?;
    let mut child = command
        .stdout(Stdio::piped())
        .stderr(logs)
        .spawn()
        .map_err(error)?;
    let stdout = child.stdout.take().ok_or("Missing setup output")?;
    *state.setup_process.lock().unwrap() = Some(process::Process::new(child)?);
    for line in BufReader::new(stdout).lines() {
        let line = line.map_err(error)?;
        if let Ok(value) = serde_json::from_str::<Value>(&line) {
            report(app, state, value);
        }
    }
    let mut process = state
        .setup_process
        .lock()
        .unwrap()
        .take()
        .ok_or("Setup stopped")?;
    let code = process.child.wait().map_err(error)?;
    if code.success() {
        Ok(())
    } else {
        Err(format!(
            "Setup failed ({code}). See setup.log / Revisa el diagnóstico. {}",
            state.progress.lock().unwrap()["message"]
        ))
    }
}
fn stop_engine(state: &Desktop) {
    if let Some(mut engine) = state.engine.lock().unwrap().take() {
        engine.process.stop();
    }
}
fn start_engine(app: &tauri::AppHandle, state: &Desktop) -> Result<(), String> {
    let result = start_engine_impl(app, state);
    if result.is_err() {
        state.setup_process.lock().unwrap().take();
    }
    result
}
fn start_engine_impl(app: &tauri::AppHandle, state: &Desktop) -> Result<(), String> {
    stop_engine(state);
    report(
        app,
        state,
        json!({"phase":"starting","message":"Starting voice engine / Iniciando motor de voz"}),
    );
    let token = Uuid::new_v4().to_string() + &Uuid::new_v4().to_string();
    let mut command = Command::new(python(&state.root));
    command.arg(backend_script(state, "server.py"));
    runtime_env(state, &mut command);
    let log = File::options()
        .append(true)
        .create(true)
        .open(state.root.join("logs/engine.log"))
        .map_err(error)?;
    let mut child = command
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(log)
        .spawn()
        .map_err(error)?;
    child
        .stdin
        .take()
        .ok_or("Missing stdin")?
        .write_all(format!("{}\n", json!({"token":token})).as_bytes())
        .map_err(error)?;
    let stdout = child.stdout.take().ok_or("Missing stdout")?;
    *state.setup_process.lock().unwrap() = Some(process::Process::new(child)?);
    // Keep ownership while waiting; a failed handshake drops and kills the process tree.
    let (send, receive) = std::sync::mpsc::sync_channel(1);
    std::thread::spawn(move || {
        let mut reader = BufReader::new(stdout);
        let mut line = String::new();
        let result = reader.read_line(&mut line).map(|_| line).map_err(error);
        let _ = send.send(result);
        // Drain stdout so Python cannot block on a full pipe later.
        for _ in reader.lines() {}
    });
    let line = receive
        .recv_timeout(Duration::from_secs(90))
        .map_err(error)??;
    let ready: Value = serde_json::from_str(&line).map_err(error)?;
    let port = ready["port"]
        .as_u64()
        .filter(|p| *p > 0 && *p <= 65535)
        .ok_or("Invalid engine handshake")?;
    let base = format!("http://127.0.0.1:{port}");
    let until = std::time::Instant::now() + Duration::from_secs(60);
    loop {
        // Status validates authenticated HTTP readiness after the socket handshake.
        if state
            .client
            .get(format!("{base}/api/status"))
            .bearer_auth(&token)
            .timeout(Duration::from_secs(8))
            .send()
            .map(|r| r.status().is_success())
            .unwrap_or(false)
        {
            break;
        }
        if std::time::Instant::now() > until {
            return Err(
                "Engine did not become ready. See engine.log / El motor no responde.".into(),
            );
        }
        std::thread::sleep(Duration::from_millis(300));
    }
    *state.engine.lock().unwrap() = Some(Engine {
        process: state
            .setup_process
            .lock()
            .unwrap()
            .take()
            .ok_or("Engine start cancelled")?,
        base,
        token,
    });
    report(
        app,
        state,
        json!({"phase":"ready","message":"Ready / Listo"}),
    );
    Ok(())
}
fn detect_profile() -> String {
    let mut nvidia = Command::new("nvidia-smi");
    process::hide(&mut nvidia);
    if nvidia.output().map(|o| o.status.success()).unwrap_or(false) {
        return "cuda".into();
    }
    #[cfg(target_os = "linux")]
    {
        for (tool, args) in [("lspci", vec![]), ("/opt/rocm/bin/rocminfo", vec![])] {
            if let Ok(o) = Command::new(tool).args(args as Vec<&str>).output() {
                let text = String::from_utf8_lossy(&o.stdout);
                if text.contains("9060") || text.contains("gfx1200") {
                    return "rocm".into();
                }
            }
        }
    }
    "cpu".into()
}
#[tauri::command]
async fn desktop_info(state: State<'_>) -> Result<Value, String> {
    let state = state.inner().clone();
    tauri::async_runtime::spawn_blocking(move|| {
        Ok(json!({"data_dir":state.root,"os":std::env::consts::OS,"recommended_profile":detect_profile(),
            "installed":state.root.join("desktop-ready.json").is_file() && state.root.join("environment-ready.json").is_file() && python(&state.root).is_file(),
            "running":state.engine.lock().unwrap().is_some(),"settings":*state.settings.lock().unwrap(),
            "progress":*state.progress.lock().unwrap(),"busy":state.busy.load(Ordering::SeqCst)>0,
            "smoke_media":std::env::args().any(|a|a=="--smoke-media"),"media_origin":state.media_origin.lock().unwrap().clone()}))
    }).await.map_err(error)?
}
#[tauri::command]
async fn prepare_engine(
    app: tauri::AppHandle,
    state: State<'_>,
    profile: String,
    model: String,
) -> Result<(), String> {
    if !["cpu", "cuda", "rocm"].contains(&profile.as_str())
        || !["1.7B", "0.6B"].contains(&model.as_str())
    {
        return Err("Invalid model/device".into());
    }
    if cfg!(windows) && profile == "rocm" {
        return Err("ROCm setup is supported only for Linux RX 9060 XT.".into());
    }
    let state = state.inner().clone();
    if state.busy.load(Ordering::SeqCst) > 0 || state.preparing.swap(true, Ordering::SeqCst) {
        return Err("An operation is already running".into());
    }
    let result=tauri::async_runtime::spawn_blocking({let state=state.clone();let app=app.clone();move|| {
        stop_engine(&state);
        {let mut settings=state.settings.lock().unwrap();settings.profile=profile.clone();settings.model=model.clone();}
        let uv=binary(&state.resources,"uv");
        if !uv.is_file(){return Err("Bundled uv missing. Run resource preparation before building.".into());}
        let mut python_install=Command::new(&uv);python_install.args(["python","install","--no-bin","--no-registry","3.12"]);
        report(&app,&state,json!({"phase":"python","message":"Downloading Python if needed / Preparando Python"}));
        run_progress(&app,&state,python_install)?;
        let mut setup=Command::new(&uv);
        setup.args(["run","--no-project","--python","3.12"]).arg(backend_script(&state,"bootstrap.py"))
            .arg("--data").arg(&state.root).arg("--uv").arg(&uv).arg("--profile").arg(&profile).arg("--model").arg(&model);
        run_progress(&app,&state,setup)?;
        save_settings(&state)?;
        fs::write(state.root.join("desktop-ready.json"), b"ready").map_err(error)?;
        start_engine(&app,&state)
    }}).await.map_err(error)?;
    state.preparing.store(false, Ordering::SeqCst);
    if let Err(e) = &result {
        report(&app, &state, json!({"phase":"error","message":e}));
    }
    result
}
#[tauri::command]
async fn restart_engine(app: tauri::AppHandle, state: State<'_>) -> Result<(), String> {
    let state = state.inner().clone();
    if state
        .preparing
        .compare_exchange(false, true, Ordering::SeqCst, Ordering::SeqCst)
        .is_err()
    {
        return Err("Wait for the current operation / Espera a que termine.".into());
    }
    if state.busy.load(Ordering::SeqCst) > 0 {
        state.preparing.store(false, Ordering::SeqCst);
        return Err("Wait for the current operation / Espera a que termine.".into());
    }
    let result = tauri::async_runtime::spawn_blocking({
        let state = state.clone();
        move || start_engine(&app, &state)
    })
    .await
    .map_err(error)?;
    state.preparing.store(false, Ordering::SeqCst);
    result
}
fn endpoint(state: &Desktop, path: &str) -> Result<(String, String), String> {
    if !path.starts_with("/api/")
        || path.contains("..")
        || path.contains('\\')
        || path.contains('#')
        || path.contains("://")
    {
        return Err("Invalid API path".into());
    }
    let lock = state.engine.lock().unwrap();
    let engine = lock
        .as_ref()
        .ok_or("Voice engine is not running / El motor no está iniciado")?;
    Ok((format!("{}{path}", engine.base), engine.token.clone()))
}
struct Busy(Arc<Desktop>);
impl Busy {
    fn new(state: Arc<Desktop>) -> Self {
        state.busy.fetch_add(1, Ordering::SeqCst);
        Self(state)
    }
}
impl Drop for Busy {
    fn drop(&mut self) {
        self.0.busy.fetch_sub(1, Ordering::SeqCst);
    }
}
#[tauri::command]
async fn api_request(
    state: State<'_>,
    method: String,
    path: String,
    body: Option<Value>,
) -> Result<Value, String> {
    let state = state.inner().clone();
    if !["GET", "POST", "PATCH", "DELETE"].contains(&method.as_str()) {
        return Err("Method not allowed".into());
    }
    tauri::async_runtime::spawn_blocking(move || {
        let _busy = if method != "GET" {
            Some(Busy::new(state.clone()))
        } else {
            None
        };
        let (url, token) = endpoint(&state, &path)?;
        let mut request = state
            .client
            .request(method.parse().map_err(error)?, url)
            .bearer_auth(token);
        if let Some(body) = body {
            request = request.json(&body);
        }
        let response = request.send().map_err(error)?;
        let status = response.status();
        let value: Value = response.json().map_err(error)?;
        if !status.is_success() {
            return Err(value["detail"]
                .as_str()
                .map(str::to_owned)
                .unwrap_or_else(|| value.to_string()));
        }
        Ok(value)
    })
    .await
    .map_err(error)?
}
#[tauri::command]
async fn choose_sample(app: tauri::AppHandle, state: State<'_>) -> Result<Option<Value>, String> {
    let state = state.inner().clone();
    tauri::async_runtime::spawn_blocking(move || {
        let file = app
            .dialog()
            .file()
            .add_filter("Audio", &["wav", "mp3", "m4a", "webm", "ogg", "flac"])
            .blocking_pick_file();
        if let Some(file) = file {
            let path = file.into_path().map_err(error)?;
            if fs::metadata(&path).map_err(error)?.len() > 100 * 1024 * 1024 {
                return Err("Sample exceeds 100 MB / La muestra supera 100 MB".into());
            }
            let id = Uuid::new_v4().to_string();
            let name = path
                .file_name()
                .unwrap_or_default()
                .to_string_lossy()
                .to_string();
            state.samples.lock().unwrap().insert(id.clone(), path);
            Ok(Some(json!({"id":id,"name":name})))
        } else {
            Ok(None)
        }
    })
    .await
    .map_err(error)?
}
#[tauri::command]
async fn upload_voice(
    state: State<'_>,
    name: String,
    transcript: String,
    sample_id: String,
) -> Result<Value, String> {
    let state = state.inner().clone();
    tauri::async_runtime::spawn_blocking(move || {
        let _busy = Busy::new(state.clone());
        let path = state
            .samples
            .lock()
            .unwrap()
            .get(&sample_id)
            .cloned()
            .ok_or("Select or record an audio sample")?;
        let (url, token) = endpoint(&state, "/api/voices")?;
        let form = reqwest::blocking::multipart::Form::new()
            .text("name", name)
            .text("transcript", transcript)
            .file("file", &path)
            .map_err(error)?;
        let response = state
            .client
            .post(url)
            .bearer_auth(token)
            .multipart(form)
            .send()
            .map_err(error)?;
        let status = response.status();
        let result: Value = response.json().map_err(error)?;
        if !status.is_success() {
            return Err(result["detail"].as_str().unwrap_or("Upload failed").into());
        }
        state.samples.lock().unwrap().remove(&sample_id);
        if path.parent() == Some(state.root.join("tmp/recordings").as_path()) {
            let _ = fs::remove_file(path);
        }
        Ok(result)
    })
    .await
    .map_err(error)?
}
#[tauri::command]
async fn recording_start(state: State<'_>) -> Result<(), String> {
    let state = state.inner().clone();
    tauri::async_runtime::spawn_blocking(move || {
        let mut recording = state.recording.lock().unwrap();
        if recording.is_some() {
            return Err("Already recording".into());
        }
        let id = Uuid::new_v4().to_string();
        let dir = state.root.join("tmp/recordings");
        fs::create_dir_all(&dir).map_err(error)?;
        *recording = Some(recording::Recording::start(
            id.clone(),
            dir.join(format!("{id}.wav")),
        )?);
        Ok(())
    })
    .await
    .map_err(error)?
}
#[tauri::command]
async fn recording_stop(state: State<'_>) -> Result<Value, String> {
    let state = state.inner().clone();
    tauri::async_runtime::spawn_blocking(move || {
        let recording = state
            .recording
            .lock()
            .unwrap()
            .take()
            .ok_or("Not recording")?;
        let (id, path) = recording.finish()?;
        state.samples.lock().unwrap().insert(id.clone(), path);
        Ok(json!({"id":id,"name":"recording.wav"}))
    })
    .await
    .map_err(error)?
}
#[tauri::command]
async fn export_audio(
    app: tauri::AppHandle,
    state: State<'_>,
    project_id: String,
    format: String,
    title: String,
) -> Result<bool, String> {
    if !["wav", "mp3"].contains(&format.as_str())
        || !project_id.chars().all(|c| c.is_ascii_hexdigit())
    {
        return Err("Invalid export".into());
    }
    let state = state.inner().clone();
    tauri::async_runtime::spawn_blocking(move || {
        let _busy = Busy::new(state.clone());
        let name: String = title
            .chars()
            .filter(|c| c.is_alphanumeric() || " _-".contains(*c))
            .take(100)
            .collect();
        let file = app
            .dialog()
            .file()
            .set_file_name(format!(
                "{}.{format}",
                if name.is_empty() { "Voz Local" } else { &name }
            ))
            .add_filter(&format, &[&format])
            .blocking_save_file();
        let Some(file) = file else { return Ok(false) };
        let path = file.into_path().map_err(error)?;
        let (url, token) = endpoint(
            &state,
            &format!("/api/projects/{project_id}/export?format={format}"),
        )?;
        let mut response = state
            .client
            .post(url)
            .bearer_auth(token)
            .send()
            .map_err(error)?;
        if !response.status().is_success() {
            return Err(response.text().unwrap_or_default());
        }
        let temporary = path.with_file_name(format!(".voz-export-{}.tmp", Uuid::new_v4()));
        let result = (|| {
            let mut output = File::create(&temporary).map_err(error)?;
            std::io::copy(&mut response, &mut output).map_err(error)?;
            output.sync_all().map_err(error)?;
            fs::rename(&temporary, &path).map_err(error)?;
            Ok(true)
        })();
        if result.is_err() {
            let _ = fs::remove_file(temporary);
        }
        result
    })
    .await
    .map_err(error)?
}
#[tauri::command]
async fn model_size(state: State<'_>, model: String) -> Result<u64, String> {
    if !["1.7B", "0.6B"].contains(&model.as_str()) {
        return Err("Invalid model".into());
    }
    let state = state.inner().clone();
    tauri::async_runtime::spawn_blocking(move || {
        let info: Value = state
            .client
            .get(format!(
                "https://huggingface.co/api/models/Qwen/Qwen3-TTS-12Hz-{model}-Base?blobs=true"
            ))
            .timeout(Duration::from_secs(15))
            .send()
            .map_err(error)?
            .error_for_status()
            .map_err(error)?
            .json()
            .map_err(error)?;
        Ok(info["siblings"]
            .as_array()
            .ok_or("No model metadata")?
            .iter()
            .map(|f| {
                f["size"]
                    .as_u64()
                    .or_else(|| f["lfs"]["size"].as_u64())
                    .unwrap_or(0)
            })
            .sum())
    })
    .await
    .map_err(error)?
}
#[tauri::command]
async fn choose_models(app: tauri::AppHandle, state: State<'_>) -> Result<Option<String>, String> {
    let state = state.inner().clone();
    if state.preparing.load(Ordering::SeqCst) || state.busy.load(Ordering::SeqCst) > 0 {
        return Err("Wait for the current operation".into());
    }
    tauri::async_runtime::spawn_blocking(move|| {
        let file=app.dialog().file().set_title("Choose existing models folder / Elige la carpeta models anterior").blocking_pick_folder();
        let Some(file)=file else{return Ok(None)};let path=file.into_path().map_err(error)?;
        if !["1.7B","0.6B"].iter().any(|size|path.join(format!("Qwen3-TTS-12Hz-{size}-Base/model.safetensors")).is_file()){return Err("Choose a models folder containing Qwen3-TTS / Elige una carpeta models con Qwen3-TTS.".into());}
        state.settings.lock().unwrap().models_dir=Some(path.to_string_lossy().into());save_settings(&state)?;Ok(Some(path.to_string_lossy().into()))
    }).await.map_err(error)?
}
#[tauri::command]
async fn import_legacy(app: tauri::AppHandle, state: State<'_>) -> Result<bool, String> {
    let state = state.inner().clone();
    if state
        .preparing
        .compare_exchange(false, true, Ordering::SeqCst, Ordering::SeqCst)
        .is_err()
    {
        return Err("Wait for current operation".into());
    }
    if state.busy.load(Ordering::SeqCst) > 0 {
        state.preparing.store(false, Ordering::SeqCst);
        return Err("Wait for current operation".into());
    }
    let result=tauri::async_runtime::spawn_blocking({let state=state.clone();let app=app.clone();move|| {
        let file=app.dialog().file().set_title("Choose previous data folder / Elige la carpeta data anterior").blocking_pick_folder();
        let Some(file)=file else{return Ok(false)};
        if !python(&state.root).is_file(){return Err("Prepare Python using the setup assistant first / Completa el asistente primero.".into());}
        stop_engine(&state);
        let mut command=Command::new(python(&state.root));runtime_env(&state,&mut command);
        command.arg(backend_script(&state,"import_data.py")).arg(file.into_path().map_err(error)?).arg(&state.root);
        if let Err(e)=run_progress(&app,&state,command){let _=start_engine(&app,&state);return Err(e);}
        let settings:Settings=serde_json::from_slice(&fs::read(state.root.join("desktop-settings.json")).map_err(error)?).map_err(error)?;
        *state.settings.lock().unwrap()=settings;
        start_engine(&app,&state)?;Ok(true)
    }}).await.map_err(error)?;
    state.preparing.store(false, Ordering::SeqCst);
    result
}
#[tauri::command]
async fn open_external(app: tauri::AppHandle, url: String) -> Result<(), String> {
    let url = url::Url::parse(&url).map_err(error)?;
    if !["https", "http"].contains(&url.scheme()) {
        return Err("Only HTTP links are allowed".into());
    }
    app.opener()
        .open_url(url.as_str(), None::<&str>)
        .map_err(error)
}
#[tauri::command]
async fn open_data(app: tauri::AppHandle, state: State<'_>) -> Result<(), String> {
    app.opener()
        .open_path(state.root.to_string_lossy(), None::<&str>)
        .map_err(error)
}
#[tauri::command]
async fn ui_report(state: State<'_>, kind: String, message: String) -> Result<(), String> {
    if !["ready", "error"].contains(&kind.as_str()) {
        return Err("Invalid UI report".into());
    }
    let mut log = File::options()
        .create(true)
        .append(true)
        .open(state.root.join("logs/desktop.log"))
        .map_err(error)?;
    writeln!(
        log,
        "{} {}",
        kind,
        message
            .chars()
            .take(2000)
            .collect::<String>()
            .replace('\n', " ")
    )
    .map_err(error)
}
#[tauri::command]
async fn diagnostics(state: State<'_>) -> Result<String, String> {
    let mut text = String::new();
    for name in ["setup.log", "engine.log", "desktop.log"] {
        if let Ok(mut file) = File::open(state.root.join("logs").join(name)) {
            let len = file.metadata().map_err(error)?.len();
            file.seek(SeekFrom::Start(len.saturating_sub(16000)))
                .map_err(error)?;
            let mut bytes = Vec::new();
            file.read_to_end(&mut bytes).map_err(error)?;
            text += &format!("\n=== {name} ===\n{}", String::from_utf8_lossy(&bytes));
        }
    }
    Ok(text)
}
fn media(
    state: &Desktop,
    request: tauri::http::Request<Vec<u8>>,
) -> tauri::http::Response<Vec<u8>> {
    let result = (|| -> Result<_, String> {
        let path = request.uri().path();
        if let Some(id) = path.strip_prefix("/sample/") {
            let file = state
                .samples
                .lock()
                .unwrap()
                .get(id)
                .cloned()
                .ok_or("Sample not found")?;
            let mime = match file
                .extension()
                .and_then(|s| s.to_str())
                .unwrap_or("")
                .to_lowercase()
                .as_str()
            {
                "mp3" => "audio/mpeg",
                "ogg" => "audio/ogg",
                "webm" => "audio/webm",
                "m4a" => "audio/mp4",
                "flac" => "audio/flac",
                _ => "audio/wav",
            };
            let data = fs::read(file).map_err(error)?;
            return Ok(tauri::http::Response::builder()
                .status(200)
                .header("Content-Type", mime)
                .header("Access-Control-Allow-Origin", "*")
                .body(data)
                .unwrap());
        }
        // Restrict media to GET audio endpoints; never expose general API calls or arbitrary files.
        if !(path.ends_with("/audio")
            || path.ends_with("/raw-audio")
            || path.ends_with("/previous-audio")
            || path.ends_with("/previous-raw-audio"))
        {
            return Err("Invalid media endpoint".into());
        }
        let (url, token) = endpoint(
            state,
            request
                .uri()
                .path_and_query()
                .map(|p| p.as_str())
                .unwrap_or(path),
        )?;
        let mut fetch = state.client.get(url).bearer_auth(token);
        let requested = request
            .headers()
            .get("range")
            .and_then(|r| r.to_str().ok())
            .unwrap_or("bytes=0-");
        let bounded = if let Some(start) = requested
            .strip_prefix("bytes=")
            .and_then(|r| r.strip_suffix('-'))
            .and_then(|r| r.parse::<u64>().ok())
        {
            format!(
                "bytes={start}-{}",
                start.saturating_add(8 * 1024 * 1024 - 1)
            )
        } else {
            requested.into()
        };
        fetch = fetch.header("Range", bounded);
        let response = fetch.send().map_err(error)?;
        let mut builder = tauri::http::Response::builder()
            .status(response.status().as_u16())
            .header("Access-Control-Allow-Origin", "*");
        for name in [
            "content-type",
            "content-range",
            "accept-ranges",
            "content-length",
        ] {
            if let Some(value) = response.headers().get(name) {
                builder = builder.header(name, value.to_str().map_err(error)?);
            }
        }
        builder
            .body(response.bytes().map_err(error)?.to_vec())
            .map_err(error)
    })();
    result.unwrap_or_else(|e| {
        if let Ok(mut log) = File::options()
            .create(true)
            .append(true)
            .open(state.root.join("logs/desktop.log"))
        {
            let _ = writeln!(log, "error media: {e}");
        }
        tauri::http::Response::builder()
            .status(503)
            .body(e.into_bytes())
            .unwrap()
    })
}
fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_single_instance::init(|app,_,_|{if let Some(window)=app.get_webview_window("main"){let _=window.show();let _=window.set_focus();}}))
        .plugin(tauri_plugin_dialog::init()).plugin(tauri_plugin_opener::init())
        .register_asynchronous_uri_scheme_protocol("voz-media",|context,request,responder| {
            let state=context.app_handle().state::<Arc<Desktop>>().inner().clone();
            std::thread::spawn(move||responder.respond(media(&state,request)));
        })
        .invoke_handler(tauri::generate_handler![desktop_info,prepare_engine,restart_engine,api_request,choose_sample,upload_voice,recording_start,recording_stop,export_audio,model_size,choose_models,import_legacy,open_external,open_data,diagnostics,ui_report])
        .setup(|app| {
            let root=if cfg!(debug_assertions){std::env::var_os("VOZ_LOCAL_DESKTOP_TEST_DIR").map(PathBuf::from).unwrap_or(app.path().app_local_data_dir()?)}else{app.path().app_local_data_dir()?};
            for folder in ["logs","tmp/recordings"] {fs::create_dir_all(root.join(folder))?;}
            // Only remove known uncommitted recording files; saved voices/projects are untouched.
            for entry in fs::read_dir(root.join("tmp/recordings"))?.flatten(){let path=entry.path();if path.extension().and_then(|e|e.to_str())==Some("wav"){let _=fs::remove_file(path);}}
            let resources=if cfg!(debug_assertions){PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("resources")}else{app.path().resource_dir()?.join("resources")};
            let settings=fs::read(root.join("desktop-settings.json")).ok().and_then(|s|serde_json::from_slice(&s).ok()).unwrap_or_default();
            let state=Arc::new(Desktop{root,resources,settings:Mutex::new(settings),client:reqwest::blocking::Client::builder().no_proxy().connect_timeout(Duration::from_secs(15)).build()?,engine:Mutex::new(None),setup_process:Mutex::new(None),progress:Mutex::new(json!({"phase":"idle"})),samples:Mutex::new(HashMap::new()),recording:Mutex::new(None),preparing:AtomicBool::new(false),busy:AtomicUsize::new(0),media_origin:Mutex::new(String::new()),closing:AtomicBool::new(false)});
            let smoke_media=std::env::args().any(|arg|arg=="--smoke-media");
            let smoke_engine=smoke_media || std::env::args().any(|arg|arg=="--smoke-engine");
            if smoke_engine || std::env::args().any(|arg|arg=="--smoke-startup") {
                let handle=app.handle().clone();let state=state.clone();let log=state.root.join("logs/desktop.log");
                std::thread::spawn(move|| {
                    for _ in 0..240 {
                        let contents=fs::read_to_string(&log).unwrap_or_default();
                        let expected=if smoke_media{"ready Desktop media protocol decoded WAV and seeked"}else if smoke_engine{"ready Desktop project UI loaded from authenticated engine"}else{"ready Desktop interface loaded and IPC connected"};
                        if contents.contains(expected) {
                            if smoke_engine {
                                let base=state.engine.lock().unwrap().as_ref().map(|e|e.base.clone());
                                if let Some(base)=base {
                                    let denied=state.client.get(format!("{base}/api/voices")).timeout(Duration::from_secs(5)).send().map(|r|r.status().as_u16()==401).unwrap_or(false);
                                    stop_engine(&state);
                                    let stopped=state.client.get(format!("{base}/api/voices")).timeout(Duration::from_secs(2)).send().is_err();
                                    if !denied || !stopped {eprintln!("Private engine shutdown/auth smoke failed");handle.exit(1);return;}
                                    println!("NATIVE_UI_ENGINE_SQLITE_READY; AUTH_401; OWNED_PROCESS_STOPPED");
                                }else{handle.exit(1);return;}
                            }else{println!("NATIVE_UI_IPC_READY");}
                            state.closing.store(true,Ordering::SeqCst);handle.exit(0);return;
                        }
                        if contents.contains("error ") {eprintln!("{contents}");stop_engine(&state);handle.exit(1);return;}
                        std::thread::sleep(Duration::from_millis(500));
                    }
                    eprintln!("Native UI did not report readiness");stop_engine(&state);handle.exit(1);
                });
            }
            gateway::start(state.clone())?;
            app.manage(state.clone());
            tauri::WebviewWindowBuilder::new(app,"main",tauri::WebviewUrl::App("index.html".into()))
                .title("Voz Local").inner_size(1180.,820.).min_inner_size(800.,600.)
                .on_navigation(|url| url.scheme()=="tauri" || matches!(url.host_str(),Some("tauri.localhost")))
                .build()?;
            let handle=app.handle().clone();
            std::thread::spawn(move||loop {
                std::thread::sleep(Duration::from_secs(2));if state.closing.load(Ordering::SeqCst){break;}
                let crashed={let mut lock=state.engine.lock().unwrap();if let Some(engine)=lock.as_mut(){engine.process.child.try_wait().ok().flatten().is_some()}else{false}};
                if crashed {stop_engine(&state);report(&handle,&state,json!({"phase":"error","message":"Voice engine stopped. Restart it in Settings / Reinicia el motor en Ajustes."}));}
            });
            Ok(())
        })
        .on_window_event(|window,event| {
            if let tauri::WindowEvent::CloseRequested{api,..}=event {
                let state=window.state::<Arc<Desktop>>();
                if state.closing.load(Ordering::SeqCst){return;}
                api.prevent_close();
                let app=window.app_handle().clone();let state=state.inner().clone();
                let busy=state.busy.load(Ordering::SeqCst)>0||state.preparing.load(Ordering::SeqCst)||state.recording.lock().unwrap().is_some();
                let finish=move|| {state.closing.store(true,Ordering::SeqCst);std::thread::spawn(move||{stop_engine(&state);state.setup_process.lock().unwrap().take();state.recording.lock().unwrap().take();app.exit(0);});};
                if busy {window.dialog().message("Audio generation, recording or setup is running. Exit and discard pending work? / Hay una operación activa. ¿Salir y descartar el trabajo pendiente?").kind(MessageDialogKind::Warning).buttons(MessageDialogButtons::OkCancelCustom("Exit / Salir".into(),"Wait / Esperar".into())).show(move|yes|{if yes{finish();}});}else{finish();}
            }
        })
        .run(tauri::generate_context!()).expect("Failed to start Voz Local");
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn rejects_remote_and_traversal_api_paths() {
        let root = std::env::temp_dir().join(Uuid::new_v4().to_string());
        let state = Desktop {
            root,
            resources: PathBuf::new(),
            client: reqwest::blocking::Client::new(),
            engine: Mutex::new(None),
            setup_process: Mutex::new(None),
            progress: Mutex::new(json!({})),
            samples: Mutex::new(HashMap::new()),
            recording: Mutex::new(None),
            settings: Mutex::new(Settings::default()),
            preparing: AtomicBool::new(false),
            busy: AtomicUsize::new(0),
            media_origin: Mutex::new(String::new()),
            closing: AtomicBool::new(false),
        };
        for path in [
            "https://example.com/api/voices",
            "/api/../secret",
            "/api/voices#secret",
            "/api/\\\\host",
        ] {
            assert_eq!(endpoint(&state, path).unwrap_err(), "Invalid API path");
        }
        assert!(endpoint(&state, "/api/voices")
            .unwrap_err()
            .contains("not running"));
    }
    #[test]
    fn busy_guard_releases_on_error() {
        let state = Arc::new(Desktop {
            root: PathBuf::new(),
            resources: PathBuf::new(),
            client: reqwest::blocking::Client::new(),
            engine: Mutex::new(None),
            setup_process: Mutex::new(None),
            progress: Mutex::new(json!({})),
            samples: Mutex::new(HashMap::new()),
            recording: Mutex::new(None),
            settings: Mutex::new(Settings::default()),
            preparing: AtomicBool::new(false),
            busy: AtomicUsize::new(0),
            media_origin: Mutex::new(String::new()),
            closing: AtomicBool::new(false),
        });
        {
            let _guard = Busy::new(state.clone());
            assert_eq!(state.busy.load(Ordering::SeqCst), 1);
        }
        assert_eq!(state.busy.load(Ordering::SeqCst), 0);
    }
}
