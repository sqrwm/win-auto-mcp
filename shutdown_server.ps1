# 关闭通过 PID 文件启动的服务
$pidFile = "server.pid"

if (Test-Path $pidFile) {
    $serverPid = Get-Content $pidFile
    try {
        Stop-Process -Id $serverPid -Force -ErrorAction Stop
        Write-Output "Stopped server with PID $pid"
        Remove-Item $pidFile
    } catch {
        Write-Warning "Failed to stop server: $_"
    }
} else {
    Write-Warning "No PID file found."
}
