#[cfg(unix)]
use std::os::unix::process::CommandExt;
#[cfg(windows)]
use std::os::windows::{io::AsRawHandle, process::CommandExt};
use std::process::{Child, Command};
pub fn hide(command: &mut Command) {
    #[cfg(windows)]
    command.creation_flags(0x08000000 | 0x00000200);
    #[cfg(unix)]
    command.process_group(0);
}
pub struct Process {
    pub child: Child,
    #[cfg(windows)]
    job: usize,
}
impl Process {
    pub fn new(child: Child) -> Result<Self, String> {
        #[cfg(windows)]
        unsafe {
            let mut child = child;
            use windows_sys::Win32::Foundation::CloseHandle;
            use windows_sys::Win32::System::JobObjects::*;
            let job = CreateJobObjectW(std::ptr::null(), std::ptr::null());
            if job.is_null() {
                let error = std::io::Error::last_os_error().to_string();
                let _ = child.kill();
                let _ = child.wait();
                return Err(error);
            }
            let mut limits: JOBOBJECT_EXTENDED_LIMIT_INFORMATION = std::mem::zeroed();
            limits.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
            if SetInformationJobObject(
                job,
                JobObjectExtendedLimitInformation,
                &limits as *const _ as *const _,
                std::mem::size_of_val(&limits) as u32,
            ) == 0
                || AssignProcessToJobObject(job, child.as_raw_handle() as _) == 0
            {
                let error = std::io::Error::last_os_error().to_string();
                CloseHandle(job);
                let _ = child.kill();
                let _ = child.wait();
                return Err(error);
            }
            return Ok(Self {
                child,
                job: job as usize,
            });
        }
        #[cfg(not(windows))]
        Ok(Self { child })
    }
    pub fn stop(&mut self) {
        #[cfg(unix)]
        unsafe {
            libc::kill(-(self.child.id() as i32), libc::SIGTERM);
        }
        #[cfg(windows)]
        unsafe {
            windows_sys::Win32::System::JobObjects::TerminateJobObject(self.job as _, 1);
        }
        let deadline = std::time::Instant::now() + std::time::Duration::from_secs(5);
        while std::time::Instant::now() < deadline {
            if self.child.try_wait().ok().flatten().is_some() {
                return;
            }
            std::thread::sleep(std::time::Duration::from_millis(50));
        }
        #[cfg(unix)]
        unsafe {
            libc::kill(-(self.child.id() as i32), libc::SIGKILL);
        }
        let _ = self.child.kill();
        let _ = self.child.wait();
    }
}
impl Drop for Process {
    fn drop(&mut self) {
        self.stop();
        #[cfg(windows)]
        unsafe {
            windows_sys::Win32::Foundation::CloseHandle(self.job as _);
        }
    }
}
