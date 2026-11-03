//! WebKitGTK cannot play audio from custom URI schemes. Use a loopback-only,
//! random-capability media gateway on Linux; never expose the backend session token.
use crate::{endpoint, error, Desktop};
use std::{
    sync::{atomic::Ordering, Arc},
    time::Duration,
};
use tiny_http::{Header, Response, StatusCode};
use uuid::Uuid;
fn headers(source: &reqwest::header::HeaderMap) -> Vec<Header> {
    let mut headers = vec![Header::from_bytes("Access-Control-Allow-Origin", "*").unwrap()];
    for name in ["content-type", "content-range", "accept-ranges"] {
        if let Some(value) = source.get(name) {
            if let Ok(header) = Header::from_bytes(name, value.as_bytes()) {
                headers.push(header);
            }
        }
    }
    headers
}
fn handle(state: &Desktop, request: tiny_http::Request, prefix: &str) {
    let uri = request.url().to_string();
    let Some(path) = uri.strip_prefix(prefix) else {
        let _ = request.respond(Response::empty(StatusCode(403)));
        return;
    };
    if !["GET", "HEAD"].contains(&request.method().as_str()) {
        let _ = request.respond(Response::empty(StatusCode(405)));
        return;
    }
    let range = request
        .headers()
        .iter()
        .find(|h| h.field.equiv("Range"))
        .map(|h| h.value.to_string());
    if path.starts_with("/sample/") {
        let mut builder =
            tauri::http::Request::builder().uri(format!("voz-media://localhost{path}"));
        if let Some(range) = &range {
            builder = builder.header("Range", range.as_str());
        }
        if let Ok(fake) = builder.body(Vec::new()) {
            let data = crate::media(state, fake);
            let (parts, body) = data.into_parts();
            let mut response = Response::from_data(body).with_status_code(parts.status.as_u16());
            for (name, value) in &parts.headers {
                if name.as_str() != "content-length" {
                    if let Ok(header) = Header::from_bytes(name.as_str(), value.as_bytes()) {
                        response.add_header(header);
                    }
                }
            }
            let _ = request.respond(response);
            return;
        }
    }
    let only_path = path.split('?').next().unwrap_or("");
    if !(only_path.ends_with("/audio")
        || only_path.ends_with("/raw-audio")
        || only_path.ends_with("/previous-audio")
        || only_path.ends_with("/previous-raw-audio"))
    {
        let _ = request.respond(Response::empty(StatusCode(403)));
        return;
    }
    let result = (|| -> Result<_, String> {
        let (url, token) = endpoint(state, path)?;
        let mut fetch = state.client.get(url).bearer_auth(token);
        if let Some(range) = range {
            let bounded = if let Some(start) = range
                .strip_prefix("bytes=")
                .and_then(|r| r.strip_suffix('-'))
                .and_then(|r| r.parse::<u64>().ok())
            {
                format!(
                    "bytes={start}-{}",
                    start.saturating_add(8 * 1024 * 1024 - 1)
                )
            } else {
                range
            };
            fetch = fetch.header("Range", bounded);
        }
        let response = fetch.send().map_err(error)?;
        let status = StatusCode(response.status().as_u16());
        let fields = headers(response.headers());
        let length = response
            .content_length()
            .and_then(|v| usize::try_from(v).ok());
        // reqwest's response is a Read stream. Do not buffer a complete narration.
        Ok(Response::new(status, fields, response, length, None))
    })();
    match result {
        Ok(response) => {
            let _ = request.respond(response);
        }
        Err(_) => {
            let _ = request.respond(Response::empty(StatusCode(503)));
        }
    }
}
pub fn start(state: Arc<Desktop>) -> Result<(), String> {
    if !cfg!(target_os = "linux") {
        *state.media_origin.lock().unwrap() = "http://voz-media.localhost".into();
        return Ok(());
    }
    let server = tiny_http::Server::http("127.0.0.1:0").map_err(error)?;
    let address = server
        .server_addr()
        .to_ip()
        .ok_or("Missing loopback media address")?;
    let ticket = Uuid::new_v4().to_string() + &Uuid::new_v4().to_string();
    let prefix = format!("/{ticket}");
    *state.media_origin.lock().unwrap() = format!("http://127.0.0.1:{}/{ticket}", address.port());
    std::thread::spawn(move || {
        while !state.closing.load(Ordering::SeqCst) {
            if let Ok(Some(request)) = server.recv_timeout(Duration::from_millis(250)) {
                let state = state.clone();
                let prefix = prefix.clone();
                std::thread::spawn(move || handle(&state, request, &prefix));
            }
        }
    });
    Ok(())
}
