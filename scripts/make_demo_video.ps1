$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Drawing

$repo = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$assets = Join-Path $repo "docs\assets"
$frames = Join-Path $assets "demo_frames"
$video = Join-Path $assets "lobster-demo.mp4"
$gif = Join-Path $assets "lobster-demo.gif"

New-Item -ItemType Directory -Force -Path $assets | Out-Null
New-Item -ItemType Directory -Force -Path $frames | Out-Null
Get-ChildItem $frames -Filter "frame_*.png" -ErrorAction SilentlyContinue | Remove-Item -Force

$width = 1280
$height = 720
$bg = [System.Drawing.Color]::FromArgb(13, 17, 23)
$panel = [System.Drawing.Color]::FromArgb(22, 27, 34)
$border = [System.Drawing.Color]::FromArgb(48, 54, 61)
$text = [System.Drawing.Color]::FromArgb(230, 237, 243)
$muted = [System.Drawing.Color]::FromArgb(139, 148, 158)
$green = [System.Drawing.Color]::FromArgb(63, 185, 80)
$red = [System.Drawing.Color]::FromArgb(248, 81, 73)
$blue = [System.Drawing.Color]::FromArgb(88, 166, 255)
$yellow = [System.Drawing.Color]::FromArgb(210, 153, 34)
$orange = [System.Drawing.Color]::FromArgb(255, 107, 74)

$titleFont = New-Object System.Drawing.Font("Segoe UI", 38, [System.Drawing.FontStyle]::Bold)
$brandFont = New-Object System.Drawing.Font("Segoe UI", 44, [System.Drawing.FontStyle]::Bold)
$subtitleFont = New-Object System.Drawing.Font("Segoe UI", 22, [System.Drawing.FontStyle]::Regular)
$footerFont = New-Object System.Drawing.Font("Segoe UI", 24, [System.Drawing.FontStyle]::Regular)
$monoFont = New-Object System.Drawing.Font("Consolas", 31, [System.Drawing.FontStyle]::Regular)

function New-Brush($color) {
    return New-Object System.Drawing.SolidBrush($color)
}

function Save-Frame($index, $title, $subtitle, $lines) {
    $bitmap = New-Object System.Drawing.Bitmap($width, $height)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.Clear($bg)

    $graphics.FillEllipse((New-Brush ([System.Drawing.Color]::FromArgb(32, 255, 107, 74))), -80, -180, 560, 560)
    $graphics.DrawString("Lobster", $brandFont, (New-Brush $orange), 90, 48)
    $graphics.DrawString($title, $titleFont, (New-Brush $text), 90, 112)
    $graphics.DrawString($subtitle, $subtitleFont, (New-Brush $muted), 90, 156)

    $graphics.FillRectangle((New-Brush $panel), 90, 190, 1100, 430)
    $graphics.DrawRectangle((New-Object System.Drawing.Pen($border, 2)), 90, 190, 1100, 430)
    $graphics.FillEllipse((New-Brush $red), 120, 208, 16, 16)
    $graphics.FillEllipse((New-Brush $yellow), 146, 208, 16, 16)
    $graphics.FillEllipse((New-Brush $green), 172, 208, 16, 16)

    $y = 258
    foreach ($line in $lines) {
        $graphics.DrawString($line.Text, $monoFont, (New-Brush $line.Color), 125, $y)
        $y += 52
    }

    $graphics.DrawString("Local-first  |  No API key  |  No cloud", $footerFont, (New-Brush $muted), 90, 650)

    $path = Join-Path $frames ("frame_{0:D3}.png" -f $index)
    $bitmap.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $graphics.Dispose()
    $bitmap.Dispose()
    return $path
}

$scenes = @(
    @{
        Duration = 2
        Title = "Run broken Python code"
        Subtitle = "Start from the real failing command."
        Lines = @(
            @{ Text = "> python app.py"; Color = $blue },
            @{ Text = "Traceback (most recent call last):"; Color = $muted },
            @{ Text = "ModuleNotFoundError: No module named 'flask'"; Color = $red }
        )
    },
    @{
        Duration = 3
        Title = "Lobster reads the crash"
        Subtitle = "It matches the error to a small local repair."
        Lines = @(
            @{ Text = "[ERROR] ModuleNotFoundError: flask"; Color = $red },
            @{ Text = "[FIX] missing dependency detected"; Color = $yellow },
            @{ Text = "[APPLY] python -m pip install flask"; Color = $blue },
            @{ Text = "[APPLY] ok: True"; Color = $green }
        )
    },
    @{
        Duration = 3
        Title = "Retry the same command"
        Subtitle = "No guessing. The original command must pass."
        Lines = @(
            @{ Text = "[RETRY] python app.py"; Color = $blue },
            @{ Text = "[RUN] service starting..."; Color = $muted },
            @{ Text = "[SUCCESS]"; Color = $green },
            @{ Text = "[VERIFY] fixed"; Color = $green }
        )
    },
    @{
        Duration = 2
        Title = "Broken code -> fixed code"
        Subtitle = "That is Lobster in 10 seconds."
        Lines = @(
            @{ Text = "BROKEN CODE -> CRASH"; Color = $red },
            @{ Text = "CRASH -> FIX"; Color = $yellow },
            @{ Text = "FIX -> RETRY"; Color = $blue },
            @{ Text = "RETRY -> SUCCESS"; Color = $green }
        )
    }
)

$frameIndex = 0
foreach ($scene in $scenes) {
    $framePath = Save-Frame $frameIndex $scene.Title $scene.Subtitle $scene.Lines
    for ($i = 1; $i -lt ($scene.Duration * 10); $i++) {
        $frameIndex++
        Copy-Item $framePath (Join-Path $frames ("frame_{0:D3}.png" -f $frameIndex))
    }
    $frameIndex++
}

& ffmpeg -y -framerate 10 -i (Join-Path $frames "frame_%03d.png") -c:v libx264 -pix_fmt yuv420p -movflags +faststart $video
& ffmpeg -y -i $video -vf "fps=10,scale=960:-1:flags=lanczos" -loop 0 $gif

Write-Output $video
Write-Output $gif
