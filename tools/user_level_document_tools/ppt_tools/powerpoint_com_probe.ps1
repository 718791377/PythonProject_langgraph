<#
.SYNOPSIS
Probe Microsoft PowerPoint COM creation, PPTX/PDF export, optional PNG export, and process cleanup.
#>
[CmdletBinding()]
param(
    [string]$InputPptx,
    [string]$OutputDir = "$(Join-Path (Get-Location) '.local\ppt_render_tools\powerpoint_com_probe')",
    [string]$JsonPath,
    [string]$MarkdownPath,
    [switch]$SkipPngExport
)

$ErrorActionPreference = 'Stop'

function Get-PowerPointProcessIds {
    @(Get-Process -Name 'POWERPNT' -ErrorAction SilentlyContinue | ForEach-Object { [int]$_.Id })
}

function Release-ComObjectQuietly {
    param([object]$ComObject)
    if ($null -ne $ComObject) {
        try { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($ComObject) } catch { }
    }
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
if ([string]::IsNullOrWhiteSpace($JsonPath)) { $JsonPath = Join-Path $OutputDir 'powerpoint_com_probe.json' }
if ([string]::IsNullOrWhiteSpace($MarkdownPath)) { $MarkdownPath = Join-Path $OutputDir 'powerpoint_com_probe.md' }

$beforeIds = @(Get-PowerPointProcessIds)
$app = $null
$presentation = $null
$createdSlide = $null
$started = (Get-Date).ToString('o')
$result = [ordered]@{
    schema_version = 1
    generated_at = $started
    user_interactive = [Environment]::UserInteractive
    input_pptx = $InputPptx
    output_dir = (Resolve-Path -LiteralPath $OutputDir).Path
    installed = $false
    enabled = $true
    selected = $true
    ready = $false
    status = 'blocked'
    version = ''
    pptx_output = ''
    pdf_output = ''
    png_output = ''
    png_outputs = @()
    before_powerpnt_pids = @($beforeIds)
    after_powerpnt_pids = @()
    leaked_powerpnt_pids = @()
    error_type = ''
    error_message = ''
    notes = @()
}

try {
    if (-not [Environment]::UserInteractive) {
        $result.notes += 'Current process is not an interactive Windows user session; PowerPoint COM may fail with desktop/logon errors.'
    }

    $app = New-Object -ComObject PowerPoint.Application
    $result.installed = $true
    $result.version = [string]$app.Version

    if (-not [string]::IsNullOrWhiteSpace($InputPptx)) {
        $resolvedInput = (Get-Item -LiteralPath $InputPptx -ErrorAction Stop).FullName
        # ReadOnly=True, Untitled=False, WithWindow=False
        $presentation = $app.Presentations.Open($resolvedInput, $true, $false, $false)
        $result.input_pptx = $resolvedInput
    } else {
        $presentation = $app.Presentations.Add()
        # 12 = ppLayoutBlank, 1 = msoTextOrientationHorizontal.
        $createdSlide = $presentation.Slides.Add(1, 12)
        $shape = $createdSlide.Shapes.AddTextbox(1, 72, 72, 640, 120)
        $shape.TextFrame.TextRange.Text = 'PowerPoint COM render probe - ????'
        $result.pptx_output = Join-Path $OutputDir 'powerpoint_com_probe.pptx'
        $presentation.SaveAs($result.pptx_output)
    }

    if ([string]::IsNullOrWhiteSpace($result.pptx_output) -and -not [string]::IsNullOrWhiteSpace($InputPptx)) {
        $result.pptx_output = $result.input_pptx
    }

    $pdfPath = Join-Path $OutputDir 'powerpoint_com_probe.pdf'
    # 32 = ppSaveAsPDF.
    $presentation.SaveAs($pdfPath, 32)
    if (Test-Path -LiteralPath $pdfPath) { $result.pdf_output = (Get-Item -LiteralPath $pdfPath).FullName }

    if (-not $SkipPngExport -and $presentation.Slides.Count -ge 1) {
        $pngFiles = @()
        for ($slideIndex = 1; $slideIndex -le $presentation.Slides.Count; $slideIndex++) {
            $pngPath = Join-Path $OutputDir ("powerpoint_com_probe_slide{0}.png" -f $slideIndex)
            $presentation.Slides.Item($slideIndex).Export($pngPath, 'PNG', 1280, 720)
            if (Test-Path -LiteralPath $pngPath) {
                $pngFiles += (Get-Item -LiteralPath $pngPath).FullName
            }
        }
        $result.png_outputs = @($pngFiles)
        if (@($pngFiles).Count -gt 0) { $result.png_output = $pngFiles[0] }
    }

    $result.ready = [bool]($result.pdf_output -and (Test-Path -LiteralPath $result.pdf_output))
    $result.status = if ($result.ready) { 'ok' } else { 'blocked' }
} catch {
    $result.error_type = $_.Exception.GetType().FullName
    $result.error_message = $_.Exception.Message
    $result.status = 'blocked'
    $result.ready = $false
} finally {
    if ($null -ne $presentation) { try { $presentation.Close() | Out-Null } catch { } }
    if ($null -ne $app) { try { $app.Quit() | Out-Null } catch { } }
    Release-ComObjectQuietly -ComObject $createdSlide
    Release-ComObjectQuietly -ComObject $presentation
    Release-ComObjectQuietly -ComObject $app
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
    Start-Sleep -Milliseconds 500
    $afterIds = @(Get-PowerPointProcessIds)
    $result.after_powerpnt_pids = @($afterIds)
    $result.leaked_powerpnt_pids = @($afterIds | Where-Object { $beforeIds -notcontains $_ })
    if (@($result.leaked_powerpnt_pids).Count -gt 0) {
        $result.ready = $false
        $result.status = 'blocked'
        $result.notes += 'New POWERPNT process remained after COM cleanup.'
    }
    $result.finished_at = (Get-Date).ToString('o')
    $result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $JsonPath -Encoding UTF8
    $lines = @(
        '# PowerPoint COM Probe',
        '',
        "- Status: $($result.status)",
        "- Ready: $($result.ready)",
        "- UserInteractive: $($result.user_interactive)",
        "- Version: $($result.version)",
        "- PDF: $($result.pdf_output)",
        "- PNG: $($result.png_output)",
        "- PNG outputs: $($result.png_outputs -join ', ')",
        "- Leaked POWERPNT PIDs: $($result.leaked_powerpnt_pids -join ', ')",
        "- JSON: $JsonPath"
    )
    if ($result.error_message) { $lines += ''; $lines += '## Error'; $lines += $result.error_message }
    if (@($result.notes).Count -gt 0) { $lines += ''; $lines += '## Notes'; $result.notes | ForEach-Object { $lines += "- $_" } }
    $lines | Set-Content -LiteralPath $MarkdownPath -Encoding UTF8
}

Write-Host "Wrote: $JsonPath"
Write-Host "Wrote: $MarkdownPath"
if ($result.ready) { exit 0 }
exit 1
