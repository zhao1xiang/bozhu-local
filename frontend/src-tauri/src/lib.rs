use std::process::{Command, Stdio};
use std::sync::Mutex;
use std::fs::OpenOptions;
use std::io::Write;
use tauri::{Manager, State};

#[cfg(target_os = "windows")]
use std::os::windows::process::CommandExt;

#[cfg(target_os = "windows")]
const CREATE_NO_WINDOW: u32 = 0x08000000;

struct BackendProcess(Mutex<Option<std::process::Child>>);

fn log_to_file(message: &str) {
    let log_path = std::env::current_exe()
        .ok()
        .and_then(|p| p.parent().map(|p| {
            let logs_dir = p.join("logs");
            // 确保 logs 目录存在
            let _ = std::fs::create_dir_all(&logs_dir);
            logs_dir.join("tauri.log")
        }))
        .unwrap_or_else(|| std::path::PathBuf::from("logs/tauri.log"));
    
    if let Ok(mut file) = OpenOptions::new()
        .create(true)
        .append(true)
        .open(&log_path)
    {
        let timestamp = chrono::Local::now().format("%Y-%m-%d %H:%M:%S");
        let _ = writeln!(file, "[{}] {}", timestamp, message);
    }
}

#[cfg(target_os = "windows")]
fn kill_all_backend_processes() {
    log_to_file("检查并清理已存在的 backend_server.exe 进程...");
    
    // 使用 taskkill 强制终止所有 backend_server.exe 进程（静默执行，不显示窗口）
    let mut cmd = Command::new("taskkill");
    cmd.args(&["/F", "/IM", "backend_server.exe"])
        .stdout(Stdio::null())
        .stderr(Stdio::null());
    
    // 设置 CREATE_NO_WINDOW 标志，防止弹出黑窗口
    #[cfg(target_os = "windows")]
    cmd.creation_flags(CREATE_NO_WINDOW);
    
    match cmd.status() {
        Ok(status) => {
            if status.success() {
                log_to_file("✓ 清理成功：已终止所有 backend_server.exe 进程");
            } else {
                // 如果没有找到进程，taskkill 会返回错误，这是正常的
                log_to_file("没有找到运行中的 backend_server.exe 进程（或已清理）");
            }
        }
        Err(e) => {
            log_to_file(&format!("执行 taskkill 失败: {}", e));
        }
    }
    
    // 等待进程完全终止
    std::thread::sleep(std::time::Duration::from_millis(500));
}

#[tauri::command]
async fn start_backend(state: State<'_, BackendProcess>) -> Result<String, String> {
    log_to_file("=== 开始启动后端 ===");
    
    // 先清理所有已存在的后端进程
    #[cfg(target_os = "windows")]
    kill_all_backend_processes();
    
    let mut process_guard = state.0.lock().unwrap();
    
    if process_guard.is_some() {
        log_to_file("后端已经在运行中");
        return Ok("Backend is already running".to_string());
    }

    let app_dir = std::env::current_exe()
        .map_err(|e| {
            let msg = format!("获取当前 exe 路径失败: {}", e);
            log_to_file(&msg);
            msg
        })?
        .parent()
        .ok_or_else(|| {
            let msg = "获取父目录失败".to_string();
            log_to_file(&msg);
            msg
        })?
        .to_path_buf();

    log_to_file(&format!("应用目录: {:?}", app_dir));

    // 后端文件在 backend 子目录
    let backend_dir = app_dir.join("backend");
    let backend_exe = backend_dir.join("backend_server.exe");
    log_to_file(&format!("后端目录: {:?}", backend_dir));
    log_to_file(&format!("后端 EXE 路径: {:?}", backend_exe));
    
    if !backend_exe.exists() {
        let msg = format!("后端可执行文件不存在: {:?}", backend_exe);
        log_to_file(&msg);
        return Err(msg);
    }
    
    log_to_file("✓ 后端 EXE 文件存在");
    
    // 检查数据库文件（在 backend 目录）
    let db_file = backend_dir.join("database.db");
    if db_file.exists() {
        log_to_file(&format!("✓ 数据库文件存在: {:?}", db_file));
    } else {
        log_to_file(&format!("✗ 数据库文件不存在: {:?}", db_file));
    }
    
    // 日志文件在 logs 目录
    let logs_dir = app_dir.join("logs");
    std::fs::create_dir_all(&logs_dir).map_err(|e| {
        let msg = format!("创建 logs 目录失败: {}", e);
        log_to_file(&msg);
        msg
    })?;
    
    let log_file = logs_dir.join("backend.log");
    log_to_file(&format!("后端日志文件: {:?}", log_file));
    
    let log_output = OpenOptions::new()
        .create(true)
        .append(true)
        .open(&log_file)
        .map_err(|e| {
            let msg = format!("创建日志文件失败: {}", e);
            log_to_file(&msg);
            msg
        })?;
    
    let mut cmd = Command::new(&backend_exe);
    cmd.current_dir(&backend_dir)  // 在 backend 目录运行
        .stdout(Stdio::from(log_output.try_clone().unwrap()))
        .stderr(Stdio::from(log_output));
    
    #[cfg(target_os = "windows")]
    cmd.creation_flags(CREATE_NO_WINDOW);
    
    log_to_file("正在启动后端进程...");
    
    let child = cmd.spawn()
        .map_err(|e| {
            let msg = format!("启动后端失败: {}", e);
            log_to_file(&msg);
            msg
        })?;

    log_to_file(&format!("✓ 后端进程已启动，PID: {:?}", child.id()));

    *process_guard = Some(child);
    log_to_file("=== 后端启动完成 ===");
    Ok("Backend started successfully".to_string())
}

fn stop_backend(state: &State<BackendProcess>) {
    log_to_file("=== 开始关闭后端 ===");
    
    let mut process_guard = state.0.lock().unwrap();
    
    if let Some(mut child) = process_guard.take() {
        log_to_file(&format!("正在终止后端进程，PID: {:?}", child.id()));
        
        match child.kill() {
            Ok(_) => {
                log_to_file("✓ 后端进程已终止");
                // 等待进程完全退出
                let _ = child.wait();
                log_to_file("✓ 后端进程已清理");
            }
            Err(e) => {
                log_to_file(&format!("✗ 终止后端进程失败: {}", e));
            }
        }
    } else {
        log_to_file("后端进程不存在或已经停止");
    }
    
    // 额外保险：使用 taskkill 强制终止所有 backend_server.exe 进程
    #[cfg(target_os = "windows")]
    {
        log_to_file("执行额外清理：强制终止所有 backend_server.exe 进程");
        kill_all_backend_processes();
    }
    
    log_to_file("=== 后端关闭完成 ===");
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    log_to_file("========================================");
    log_to_file("Tauri 应用启动");
    log_to_file(&format!("时间: {}", chrono::Local::now().format("%Y-%m-%d %H:%M:%S")));
    log_to_file("========================================");
    
    tauri::Builder::default()
        .manage(BackendProcess(Mutex::new(None)))
        .invoke_handler(tauri::generate_handler![start_backend])
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }
            
            log_to_file("开始自动启动后端...");
            
            // 自动启动后端
            let app_handle = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                let state = app_handle.state::<BackendProcess>();
                match start_backend(state).await {
                    Ok(msg) => {
                        log_to_file(&format!("后端启动成功: {}", msg));
                        println!("Backend startup: {}", msg);
                    }
                    Err(e) => {
                        log_to_file(&format!("后端启动错误: {}", e));
                        eprintln!("Backend startup error: {}", e);
                    }
                }
                // 等待后端启动 - 增加到 6 秒确保后端完全就绪
                log_to_file("等待 6 秒让后端完全启动...");
                std::thread::sleep(std::time::Duration::from_secs(6));
                log_to_file("后端应该已经就绪");
            });
            
            // 注册应用关闭事件处理
            let app_handle = app.handle().clone();
            let window = app.get_webview_window("main").unwrap();
            window.on_window_event(move |event| {
                if let tauri::WindowEvent::CloseRequested { .. } = event {
                    log_to_file("检测到窗口关闭请求");
                    let state = app_handle.state::<BackendProcess>();
                    stop_backend(&state);
                }
            });
            
            Ok(())
        })
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::Destroyed = event {
                log_to_file("窗口已销毁，确保后端关闭");
                let state = window.state::<BackendProcess>();
                stop_backend(&state);
            }
        })
        .build(tauri::generate_context!())
        .expect("error while building tauri application")
        .run(|app_handle, event| {
            if let tauri::RunEvent::ExitRequested { .. } = event {
                log_to_file("应用退出请求，关闭后端");
                let state = app_handle.state::<BackendProcess>();
                stop_backend(&state);
            }
        });
}
