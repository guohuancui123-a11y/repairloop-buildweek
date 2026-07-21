$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Drawing

$repo = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$assets = Join-Path $repo "docs\assets"
$frames = Join-Path $assets "demo_frames"
$video = Join-Path $assets "repairloop-demo.mp4"
$gif = Join-Path $assets "repairloop-demo.gif"
$vertical = Join-Path $assets "repairloop-demo-vertical.mp4"
$verticalClean = Join-Path $assets "repairloop-demo-vertical-clean.mp4"

New-Item -ItemType Directory -Force -Path $assets | Out-Null
New-Item -ItemType Directory -Force -Path $frames | Out-Null
Get-ChildItem $frames -Filter "frame_*.png" -ErrorAction SilentlyContinue | Remove-Item -Force

$width = 1280
$height = 720
$fps = 10
$bg = [System.Drawing.Color]::FromArgb(13, 17, 23)
$panel = [System.Drawing.Color]::FromArgb(22, 27, 34)
$panel2 = [System.Drawing.Color]::FromArgb(16, 22, 31)
$border = [System.Drawing.Color]::FromArgb(48, 54, 61)
$text = [System.Drawing.Color]::FromArgb(230, 237, 243)
$muted = [System.Drawing.Color]::FromArgb(139, 148, 158)
$green = [System.Drawing.Color]::FromArgb(63, 185, 80)
$red = [System.Drawing.Color]::FromArgb(248, 81, 73)
$blue = [System.Drawing.Color]::FromArgb(88, 166, 255)
$yellow = [System.Drawing.Color]::FromArgb(210, 153, 34)
$orange = [System.Drawing.Color]::FromArgb(255, 107, 74)
$purple = [System.Drawing.Color]::FromArgb(188, 140, 255)

$brandFont = New-Object System.Drawing.Font("Segoe UI", 40, [System.Drawing.FontStyle]::Bold)
$titleFont = New-Object System.Drawing.Font("Segoe UI", 34, [System.Drawing.FontStyle]::Bold)
$subtitleFont = New-Object System.Drawing.Font("Segoe UI", 21, [System.Drawing.FontStyle]::Regular)
$smallFont = New-Object System.Drawing.Font("Segoe UI", 18, [System.Drawing.FontStyle]::Regular)
$footerFont = New-Object System.Drawing.Font("Segoe UI", 20, [System.Drawing.FontStyle]::Regular)
$monoFont = New-Object System.Drawing.Font("Consolas", 24, [System.Drawing.FontStyle]::Regular)
$monoSmallFont = New-Object System.Drawing.Font("Consolas", 20, [System.Drawing.FontStyle]::Regular)

function New-Brush($color) {
    return New-Object System.Drawing.SolidBrush($color)
}

function Draw-RoundRect($graphics, $brush, $pen, [int]$x, [int]$y, [int]$w, [int]$h, [int]$r) {
    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    $path.AddArc($x, $y, $r, $r, 180, 90)
    $path.AddArc($x + $w - $r, $y, $r, $r, 270, 90)
    $path.AddArc($x + $w - $r, $y + $h - $r, $r, $r, 0, 90)
    $path.AddArc($x, $y + $h - $r, $r, $r, 90, 90)
    $path.CloseFigure()
    if ($brush -ne $null) { $graphics.FillPath($brush, $path) }
    if ($pen -ne $null) { $graphics.DrawPath($pen, $path) }
    $path.Dispose()
}

function Draw-Terminal($graphics, $x, $y, $w, $h, $lines) {
    Draw-RoundRect $graphics (New-Brush $panel) (New-Object System.Drawing.Pen($border, 2)) $x $y $w $h 18
    $graphics.FillEllipse((New-Brush $red), $x + 28, $y + 24, 14, 14)
    $graphics.FillEllipse((New-Brush $yellow), $x + 52, $y + 24, 14, 14)
    $graphics.FillEllipse((New-Brush $green), $x + 76, $y + 24, 14, 14)
    $graphics.DrawString("terminal", $smallFont, (New-Brush $muted), $x + $w - 105, $y + 15)

    $lineY = $y + 72
    foreach ($line in $lines) {
        $font = if ($line.Small) { $monoSmallFont } else { $monoFont }
        $graphics.DrawString($line.Text, $font, (New-Brush $line.Color), $x + 34, $lineY)
        $lineY += if ($line.Small) { 35 } else { 42 }
    }
}

function Draw-StepPills($graphics, $activeIndex) {
    $labels = @("Run", "Capture", "Repair", "Verify")
    $x = 90
    for ($i = 0; $i -lt $labels.Count; $i++) {
        $color = if ($i -le $activeIndex) { $green } else { $border }
        Draw-RoundRect $graphics (New-Brush ([System.Drawing.Color]::FromArgb(35, $color.R, $color.G, $color.B))) (New-Object System.Drawing.Pen($color, 2)) $x 624 150 42 20
        $graphics.DrawString($labels[$i], $footerFont, (New-Brush $(if ($i -le $activeIndex) { $text } else { $muted })), $x + 39, 631)
        if ($i -lt $labels.Count - 1) {
            $graphics.DrawString("→", $footerFont, (New-Brush $muted), $x + 164, 631)
        }
        $x += 220
    }
}

function Save-Frame($index, $scene) {
    $bitmap = New-Object System.Drawing.Bitmap($width, $height)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
    $graphics.Clear($bg)

    $graphics.FillEllipse((New-Brush ([System.Drawing.Color]::FromArgb(36, 255, 107, 74))), -120, -190, 570, 570)
    $graphics.FillEllipse((New-Brush ([System.Drawing.Color]::FromArgb(22, 88, 166, 255))), 965, 450, 440, 440)
    $graphics.FillEllipse((New-Brush ([System.Drawing.Color]::FromArgb(16, 188, 140, 255))), 970, -170, 360, 360)

    $graphics.DrawString("RepairLoop", $brandFont, (New-Brush $orange), 90, 42)
    $graphics.DrawString($scene.Title, $titleFont, (New-Brush $text), 90, 105)
    $graphics.DrawString($scene.Subtitle, $subtitleFont, (New-Brush $muted), 92, 152)

    if ($scene.Badge) {
        Draw-RoundRect $graphics (New-Brush ([System.Drawing.Color]::FromArgb(35, $blue.R, $blue.G, $blue.B))) (New-Object System.Drawing.Pen($blue, 2)) 930 48 250 44 20
        $graphics.DrawString($scene.Badge, $smallFont, (New-Brush $text), 955, 57)
    }

    Draw-Terminal $graphics 90 205 1100 380 $scene.Lines

    if ($scene.Note) {
        Draw-RoundRect $graphics (New-Brush $panel2) (New-Object System.Drawing.Pen($border, 1)) 755 548 435 54 18
        $graphics.DrawString($scene.Note, $smallFont, (New-Brush $muted), 778, 563)
    }

    Draw-StepPills $graphics $scene.Step
    $graphics.DrawString("Local-first • dry-run by default • no source upload", $footerFont, (New-Brush $muted), 90, 682)

    $path = Join-Path $frames ("frame_{0:D3}.png" -f $index)
    $bitmap.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $graphics.Dispose()
    $bitmap.Dispose()
    return $path
}

$scenes = @(
    @{
        Duration = 4
        Step = 0
        Badge = "34-second demo"
        Title = "A Python app breaks at runtime"
        Subtitle = "RepairLoop does not guess from a prompt. It starts from the real crash."
        Note = "Real stderr becomes the repair input."
        Lines = @(
            @{ Text = "> python demo/missing_file.py"; Color = $blue },
            @{ Text = "Traceback (most recent call last):"; Color = $muted; Small = $true },
            @{ Text = "FileNotFoundError:"; Color = $red },
            @{ Text = "  demo\\generated\\config.txt"; Color = $red },
            @{ Text = "exit code: 1"; Color = $yellow }
        )
    },
    @{
        Duration = 4
        Step = 1
        Badge = "the usual pain"
        Title = "The hard part is not seeing the error"
        Subtitle = "The hard part is turning it into a safe, verifiable next action."
        Note = "No full-project rewrite. No magic autopilot."
        Lines = @(
            @{ Text = "Problem:"; Color = $yellow },
            @{ Text = "  app cannot start"; Color = $red },
            @{ Text = "Risky fix:"; Color = $yellow },
            @{ Text = "  rewrite everything / trust a vague patch"; Color = $red; Small = $true },
            @{ Text = "RepairLoop goal: minimal local repair"; Color = $green }
        )
    },
    @{
        Duration = 4
        Step = 2
        Badge = "dry-run first"
        Title = "Preview the repair before changing files"
        Subtitle = "By default, RepairLoop explains what it would do and stops."
        Note = "Dry-run is the default safety gate."
        Lines = @(
            @{ Text = "> repair-loop repair -- python demo/missing_file.py"; Color = $blue; Small = $true },
            @{ Text = "[FIX] file_not_found"; Color = $yellow },
            @{ Text = "[FIX] create_path: demo\\generated\\config.txt"; Color = $muted; Small = $true },
            @{ Text = "[PREVIEW] no changes were made"; Color = $green },
            @{ Text = "rerun with --apply to execute"; Color = $muted; Small = $true }
        )
    },
    @{
        Duration = 4
        Step = 2
        Badge = "explicit apply"
        Title = "Apply only the narrow local fix"
        Subtitle = "When you approve, it performs the smallest repair it understands."
        Note = "The original command is preserved for verification."
        Lines = @(
            @{ Text = "> repair-loop repair --apply -- python demo/missing_file.py"; Color = $blue; Small = $true },
            @{ Text = "[APPLY] create demo\\generated\\config.txt"; Color = $yellow; Small = $true },
            @{ Text = "[APPLY] ok: True"; Color = $green },
            @{ Text = "[VERIFY] rerunning original command..."; Color = $muted },
            @{ Text = ""; Color = $muted }
        )
    },
    @{
        Duration = 4
        Step = 3
        Badge = "verified"
        Title = "Verification is the product"
        Subtitle = "RepairLoop proves the fix by rerunning the same broken command."
        Note = "Success means the program runs again."
        Lines = @(
            @{ Text = "[RUN] python demo/missing_file.py"; Color = $blue },
            @{ Text = "Loaded config: demo\\generated\\config.txt"; Color = $text; Small = $true },
            @{ Text = "[EXIT] 0"; Color = $green },
            @{ Text = "[VERIFY] success"; Color = $green },
            @{ Text = "Run → Capture → Repair → Verify"; Color = $purple; Small = $true }
        )
    },
    @{
        Duration = 4
        Step = 3
        Badge = "automation-ready"
        Title = "Use it from terminals, CI, or agents"
        Subtitle = "Human-readable logs for demos. JSON reports for automation."
        Note = "Local-first core. Optional integrations later."
        Lines = @(
            @{ Text = "> repair-loop repair --json-report -- python app.py"; Color = $blue; Small = $true },
            @{ Text = '{ "ok": false, "preview": true,'; Color = $muted; Small = $true },
            @{ Text = '  "suggestion": "file_not_found" }'; Color = $muted; Small = $true },
            @{ Text = "CI can inspect the result"; Color = $green },
            @{ Text = "Agents can use it as a repair primitive"; Color = $green; Small = $true }
        )
    },
    @{
        Duration = 4
        Step = 3
        Badge = "verified benchmarks"
        Title = "Measure verified recovery"
        Subtitle = "Isolated cases. Same command rerun."
        Note = "3/3 passed • 3/3 verified"
        Lines = @(
            @{ Text = "> repair-loop benchmark --json-report"; Color = $blue; Small = $true },
            @{ Text = 'schema_version: "1.0"'; Color = $muted; Small = $true },
            @{ Text = "file_not_found       PASS"; Color = $green },
            @{ Text = "syntax_error         PASS"; Color = $green },
            @{ Text = "sqlite_missing_table PASS"; Color = $green }
        )
    },
    @{
        Duration = 3
        Step = 3
        Badge = "now on PyPI"
        Title = "Install it in one command"
        Subtitle = "RepairLoop is now a public Python package."
        Note = "pip install repairloop"
        Lines = @(
            @{ Text = "> python -m pip install repairloop"; Color = $blue },
            @{ Text = "> repair-loop --help"; Color = $blue },
            @{ Text = "Local-first automatic code repair helper"; Color = $text; Small = $true },
            @{ Text = "No cloud. No API key. No source upload."; Color = $green },
            @{ Text = "github.com/guohuancui123-a11y/repairloop"; Color = $muted; Small = $true }
        )
    },
    @{
        Duration = 3
        Step = 3
        Badge = "open source"
        Title = "RepairLoop answers one question"
        Subtitle = "Can the broken Python command run again?"
        Note = "Star the repo if this saves you time."
        Lines = @(
            @{ Text = "BROKEN COMMAND"; Color = $red },
            @{ Text = "        ↓"; Color = $muted },
            @{ Text = "MINIMAL LOCAL FIX"; Color = $yellow },
            @{ Text = "        ↓"; Color = $muted },
            @{ Text = "VERIFIED RUN"; Color = $green }
        )
    }
)

$frameIndex = 0
foreach ($scene in $scenes) {
    $framePath = Save-Frame $frameIndex $scene
    for ($i = 1; $i -lt ($scene.Duration * $fps); $i++) {
        $frameIndex++
        Copy-Item $framePath (Join-Path $frames ("frame_{0:D3}.png" -f $frameIndex))
    }
    $frameIndex++
}

& ffmpeg -hide_banner -loglevel error -y -framerate $fps -i (Join-Path $frames "frame_%03d.png") -c:v libx264 -pix_fmt yuv420p -movflags +faststart $video
& ffmpeg -hide_banner -loglevel error -y -i $video -vf "fps=8,scale=960:-1:flags=lanczos" -loop 0 $gif
& ffmpeg -hide_banner -loglevel error -y -i $video -vf "scale=720:-2,pad=720:1280:(ow-iw)/2:(oh-ih)/2:color=0d1117" -c:v libx264 -pix_fmt yuv420p -movflags +faststart $vertical
Copy-Item $vertical $verticalClean -Force

Write-Output $video
Write-Output $gif
Write-Output $vertical
