use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};
use std::{
    fs::File,
    io::BufWriter,
    path::PathBuf,
    sync::{mpsc, Arc, Mutex},
    thread,
};
type Writer = Arc<Mutex<Option<hound::WavWriter<BufWriter<File>>>>>;
pub struct Recording {
    stop: mpsc::Sender<()>,
    pub id: String,
    pub path: PathBuf,
    done: mpsc::Receiver<Result<(), String>>,
}
fn input<T>(
    device: &cpal::Device,
    config: &cpal::StreamConfig,
    writer: Writer,
    error: Arc<Mutex<Option<String>>>,
) -> Result<cpal::Stream, String>
where
    T: cpal::SizedSample,
    f32: cpal::FromSample<T>,
{
    let channels = config.channels as usize;
    device
        .build_input_stream(
            config,
            move |data: &[T], _| {
                if let Ok(mut lock) = writer.lock() {
                    if let Some(w) = lock.as_mut() {
                        // Bound a sample to 60 seconds. The UI also stops its timer at this limit.
                        for frame in data.chunks(channels) {
                            if w.duration() >= config_rate_limit(w.spec().sample_rate) {
                                break;
                            }
                            let mono = frame
                                .iter()
                                .map(|v| <f32 as cpal::FromSample<T>>::from_sample_(*v))
                                .sum::<f32>()
                                / channels as f32;
                            let _ = w.write_sample((mono.clamp(-1., 1.) * i16::MAX as f32) as i16);
                        }
                    }
                }
            },
            move |e| {
                if let Ok(mut lock) = error.lock() {
                    *lock = Some(e.to_string());
                }
            },
            None,
        )
        .map_err(|e| e.to_string())
}
fn config_rate_limit(rate: u32) -> u32 {
    rate.saturating_mul(60)
}
impl Recording {
    pub fn start(id: String, path: PathBuf) -> Result<Self, String> {
        let (stop, receiver) = mpsc::channel();
        let (ready_tx, ready_rx) = mpsc::sync_channel(1);
        let (done_tx, done) = mpsc::channel();
        let destination = path.clone();
        thread::spawn(move || {
            let result = (|| -> Result<(), String> {
                let device = cpal::default_host()
                    .default_input_device()
                    .ok_or("No microphone available / No hay micrófono disponible")?;
                let supported = device.default_input_config().map_err(|e| e.to_string())?;
                let spec = hound::WavSpec {
                    channels: 1,
                    sample_rate: supported.sample_rate().0,
                    bits_per_sample: 16,
                    sample_format: hound::SampleFormat::Int,
                };
                let writer: Writer = Arc::new(Mutex::new(Some(
                    hound::WavWriter::create(&destination, spec).map_err(|e| e.to_string())?,
                )));
                let errors = Arc::new(Mutex::new(None));
                let config = supported.config();
                let stream = match supported.sample_format() {
                    cpal::SampleFormat::F32 => {
                        input::<f32>(&device, &config, writer.clone(), errors.clone())
                    }
                    cpal::SampleFormat::I16 => {
                        input::<i16>(&device, &config, writer.clone(), errors.clone())
                    }
                    cpal::SampleFormat::U16 => {
                        input::<u16>(&device, &config, writer.clone(), errors.clone())
                    }
                    _ => Err(
                        "Unsupported microphone format / Formato de micrófono no compatible".into(),
                    ),
                }?;
                stream.play().map_err(|e| e.to_string())?;
                let _ = ready_tx.send(Ok(()));
                let _ = receiver.recv_timeout(std::time::Duration::from_secs(65));
                drop(stream);
                if let Some(w) = writer.lock().map_err(|e| e.to_string())?.take() {
                    w.finalize().map_err(|e| e.to_string())?;
                }
                if let Some(e) = errors.lock().map_err(|e| e.to_string())?.take() {
                    return Err(e);
                }
                Ok(())
            })();
            if let Err(e) = &result {
                let _ = ready_tx.send(Err(e.clone()));
            }
            let _ = done_tx.send(result);
        });
        ready_rx
            .recv_timeout(std::time::Duration::from_secs(10))
            .map_err(|e| e.to_string())??;
        Ok(Self {
            stop,
            id,
            path,
            done,
        })
    }
    pub fn finish(self) -> Result<(String, PathBuf), String> {
        let _ = self.stop.send(());
        self.done
            .recv_timeout(std::time::Duration::from_secs(10))
            .map_err(|e| e.to_string())??;
        Ok((self.id, self.path))
    }
}
