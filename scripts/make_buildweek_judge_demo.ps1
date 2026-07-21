$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Speech

$repo = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$assets = Join-Path $repo "docs\assets"
$work = Join-Path $env:TEMP "repairloop-buildweek-demo"
$sourceDemo = Join-Path $assets "repairloop-demo.mp4"
$output = Join-Path $assets "repairloop-buildweek-judge-demo-90s.mp4"
$narration = Join-Path $work "narration.wav"

Remove-Item $work -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $work | Out-Null

$width = 1280
$height = 720
$bg = [System.Drawing.Color]::FromArgb(13, 17, 23)
$panel = [System.Drawing.Color]::FromArgb(22, 27, 34)
$border = [System.Drawing.Color]::FromArgb(48, 54, 61)
$text = [System.Drawing.Color]::FromArgb(230, 237, 243)
$muted = [System.Drawing.Color]::FromArgb(170, 181, 196)
$green = [System.Drawing.Color]::FromArgb(63, 185, 80)
$blue = [System.Drawing.Color]::FromArgb(88, 166, 255)
$orange = [System.Drawing.Color]::FromArgb(255, 107, 74)

$brandFont = New-Object System.Drawing.Font("Segoe UI", 28, [System.Drawing.FontStyle]::Bold)
$titleFont = New-Object System.Drawing.Font("Segoe UI", 30, [System.Drawing.FontStyle]::Bold)
$bodyFont = New-Object System.Drawing.Font("Segoe UI", 21, [System.Drawing.FontStyle]::Regular)
$bulletFont = New-Object System.Drawing.Font("Consolas", 18, [System.Drawing.FontStyle]::Regular)
$footerFont = New-Object System.Drawing.Font("Segoe UI", 16, [System.Drawing.FontStyle]::Regular)

function New-Brush($color) { New-Object System.Drawing.SolidBrush($color) }

function New-Slide([int]$Index, [string]$Badge, [string]$Title, [string]$Subtitle, [string[]]$Bullets) {
    $bitmap = New-Object System.Drawing.Bitmap($width, $height)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
    $graphics.Clear($bg)
    $graphics.FillEllipse((New-Brush ([System.Drawing.Color]::FromArgb(35, 255, 107, 74))), -160, -220, 600, 600)
    $graphics.FillEllipse((New-Brush ([System.Drawing.Color]::FromArgb(28, 88, 166, 255))), 970, 430, 480, 480)
    $graphics.DrawString("RepairLoop", $brandFont, (New-Brush $orange), 88, 22)
    $graphics.DrawString($Badge.ToUpperInvariant(), $footerFont, (New-Brush $blue), 92, 72)
    $graphics.DrawString($Title, $titleFont, (New-Brush $text), 88, 106)

    $format = New-Object System.Drawing.StringFormat
    $format.Trimming = [System.Drawing.StringTrimming]::EllipsisWord
    $graphics.DrawString($Subtitle, $bodyFont, (New-Brush $muted), (New-Object System.Drawing.RectangleF(92, 154, 1080, 50)), $format)
    $graphics.FillRectangle((New-Brush $panel), 88, 222, 1104, 350)
    $graphics.DrawRectangle((New-Object System.Drawing.Pen($border, 2)), 88, 222, 1104, 350)

    $y = 268
    foreach ($bullet in $Bullets) {
        $graphics.DrawString("• " + $bullet, $bulletFont, (New-Brush $text), 124, $y)
        $y += 48
    }
    $graphics.DrawString("LOCAL-FIRST  •  EXPLICIT APPLY  •  VERIFIED RECOVERY", $footerFont, (New-Brush $green), 88, 650)
    $path = Join-Path $work ("slide_{0:D2}.png" -f $Index)
    $bitmap.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $graphics.Dispose()
    $bitmap.Dispose()
    return $path
}

$slides = @(
    @{ Badge = "Build Week contribution"; Title = "From plan to proof"; Subtitle = "GPT-5.6 turned a plan into measurable recovery evidence."; Bullets = @("Audited the existing architecture and test surface", "Identified a missing implementation gap", "Kept the local-first safety model intact") },
    @{ Badge = "GPT-5.6 assisted"; Title = "An engineering workflow, not a black box"; Subtitle = "The model accelerated analysis, implementation, and test refinement. The repair engine remains deterministic."; Bullets = @("Architecture audit", "Isolated fixture design", "CLI and JSON report implementation", "Regression-test refinement") },
    @{ Badge = "Verified benchmarks"; Title = "Measure verified recovery"; Subtitle = "A repair only counts when the original failing command succeeds after the repair."; Bullets = @("Detected repair kind", "Verification outcome", "Repair time", "File-level patch size") },
    @{ Badge = "Three deterministic cases"; Title = "Local-only, inspectable, reproducible"; Subtitle = "No credentials, API key, network service, or package download is needed to run the benchmark suite."; Bullets = @("Missing local configuration file", "Missing Python syntax colon", "Missing SQLite users table") },
    @{ Badge = "Judge verification"; Title = "One command produces inspectable evidence"; Subtitle = "Run the full test suite, then request the benchmark JSON report."; Bullets = @("python -m pytest -q", "python -m repair_loop benchmark --json-report", "Expected: 33 tests; 3/3 passed; 3/3 verified") },
    @{ Badge = "Safety boundary"; Title = "GPT-5.6 accelerated the contribution"; Subtitle = "RepairLoop still applies only bounded local rules after explicit approval."; Bullets = @("No source upload by default", "No autonomous full-project rewrite", "Rerun verification remains the definition of success") },
    @{ Badge = "RepairLoop"; Title = "A measurable runtime repair loop"; Subtitle = "Broken Python command → narrow local repair → verified recovery."; Bullets = @("Run", "Capture", "Repair", "Verify") }
)

$slideVideos = @()
for ($index = 0; $index -lt $slides.Count; $index++) {
    $scene = $slides[$index]
    $image = New-Slide ($index + 1) $scene.Badge $scene.Title $scene.Subtitle $scene.Bullets
    $video = Join-Path $work ("slide_{0:D2}.mp4" -f ($index + 1))
    & ffmpeg -hide_banner -loglevel error -y -loop 1 -i $image -t 8 -r 30 -c:v libx264 -pix_fmt yuv420p $video
    $slideVideos += $video
}

$concat = Join-Path $work "concat.txt"
$concatLines = @("file '$($sourceDemo.Replace('\', '/'))'")
foreach ($video in $slideVideos) { $concatLines += "file '$($video.Replace('\', '/'))'" }
Set-Content -Path $concat -Value $concatLines -Encoding UTF8
$silent = Join-Path $work "silent.mp4"
& ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i $concat -c:v libx264 -pix_fmt yuv420p -an $silent

$narrationText = @'
RepairLoop is a local-first Python runtime repair loop. It starts with a real crash, proposes a narrow repair, requires explicit apply, and reruns the original command to verify recovery.

For Build Week, the project gained a verified repair benchmark framework. It turns the claim of reliable recovery into runnable evidence. Each benchmark copies a minimal failing project into an isolated temporary workspace, runs RepairLoop, reruns the same command, and records the result as versioned JSON.

GPT-5.6 accelerated the architecture audit, benchmark design, implementation, and test refinement. It helped identify the gap between a benchmark plan and a measurable runner, while preserving the existing local-first and rule-driven safety model.

The first benchmark suite covers a missing configuration file, a missing Python colon, and a missing SQLite users table. It is deterministic, local-only, and requires no credentials or network access.

The result is thirty-three passing tests, with all three benchmark cases passed and verified. RepairLoop does not treat a plausible patch as success. Success means the original broken command runs again.
'@
$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer
$speaker.SelectVoice("Microsoft Zira Desktop")
$speaker.Rate = -2
$speaker.SetOutputToWaveFile($narration)
$speaker.Speak($narrationText)
$speaker.Dispose()

& ffmpeg -hide_banner -loglevel error -y -i $silent -i $narration -filter:a "apad" -t 90 -c:v copy -c:a aac -b:a 160k -movflags +faststart $output
Write-Output $output
