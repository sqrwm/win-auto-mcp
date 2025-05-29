$stdoutLog = "server_stdout.log"
$stderrLog = "server_stderr.log"
$pidFile = "server.pid"

# 启动 Python 服务
$process = Start-Process -FilePath "python" `
                         -ArgumentList "simple_server.py --browser edge-beta --transport sse" `
                         -RedirectStandardOutput $stdoutLog `
                         -RedirectStandardError $stderrLog `
                         -NoNewWindow -PassThru

# 保存 PID
$process.Id | Out-File -Encoding ASCII -FilePath $pidFile -Force
Write-Output "Server started with PID $($process.Id)"
