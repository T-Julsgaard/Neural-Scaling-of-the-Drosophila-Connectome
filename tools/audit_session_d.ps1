$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
function Read-Json($Path) { Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json }
function Interval($Values) {
    $v = @($Values); $mean = ($v | Measure-Object -Average).Average
    $ss = 0.0; foreach ($x in $v) { $ss += [math]::Pow($x - $mean, 2) }
    $h = 2.0686576104190406 * [math]::Sqrt($ss / ($v.Count - 1) / $v.Count)
    return @{ mean=$mean; lower=$mean-$h; upper=$mean+$h }
}
function Assert-Close($Actual, $Expected) {
    foreach ($key in 'mean','lower','upper') {
        if ([math]::Abs($Actual[$key] - $Expected.$key) -gt 1e-12) { throw "Interval mismatch: $key" }
    }
}
$hashes = @{}
foreach ($session in '010','011') {
    $selection = Read-Json "results/exp$session/selection.json"
    foreach ($p in $selection.source.PSObject.Properties) {
        if ((Get-FileHash -LiteralPath $p.Name -Algorithm SHA256).Hash.ToLower() -ne $p.Value) { throw "Source mismatch: $($p.Name)" }
        $hashes[$p.Name] = $p.Value
    }
    $contract = Read-Json "results/exp$session/confirmation/contract.json"
    if ([datetime]$selection.created_utc -gt [datetime]$contract.created_utc) { throw 'Selection chronology' }
    foreach ($p in $selection.development_hashes.PSObject.Properties) {
        if ((Get-FileHash -LiteralPath "results/exp$session/development/$($p.Name)" -Algorithm SHA256).Hash.ToLower() -ne $p.Value) { throw 'Development hash mismatch' }
    }
}
$b = @(Get-ChildItem results/exp010/confirmation/block_*.json | ForEach-Object { Read-Json $_.FullName })
$c = @(Get-ChildItem results/exp011/confirmation/block_*.json | ForEach-Object { Read-Json $_.FullName })
if ($b.Count -ne 24 -or $c.Count -ne 24) { throw 'Wrong sample count' }
$bgap = @(); $bloss = @(); $cgap = @(); $closs = @(); $coff = @(); $clips = 0
foreach ($r in $b) {
    $g=0.0; $l=0.0
    foreach ($rep in 'native','calibrated') {
        $m=$r.representations.$rep.models
        $g += ($m.offline_full_0.score[0]-$m.supervised.score[0])/2
        $l += $m.supervised.forgetting_old/2
    }
    $bgap += $g; $bloss += $l
}
$s = Read-Json results/exp011/selection.json
$etas = @((1/2400),(1/600),(1/150),(2/75)); $lambdas = @(1e-6,1e-4,.01,.1)
foreach ($r in $c) {
    $g=0.0; $l=0.0; $o=0.0
    foreach ($rep in 'native','calibrated') {
        $m=$r.representations.$rep.models
        $online=$m.("blocked_" + [array]::IndexOf($etas,[double]$s.etas.$rep.blocked))
        $offline=$m.("offline_" + [array]::IndexOf($lambdas,[double]$s.lambdas.$rep))
        $g += ($offline.old-$online.old)/2; $l += $online.forgetting/2; $o += $offline.old/2
        $clips += $online.clips
    }
    $cgap += $g; $closs += $l; $coff += $o
}
$ba=Read-Json results/exp010/analysis.json; $ca=Read-Json results/exp011/analysis.json
Assert-Close (Interval $bgap) $ba.primary_gap
Assert-Close (Interval $bloss) $ba.forgetting
Assert-Close (Interval $cgap) $ca.primary_gap
Assert-Close (Interval $closs) $ca.primary_forgetting
Assert-Close (Interval $coff) $ca.tables.native_calibrated.offline.old
if ($clips -ne 0) { throw 'Unexpected selected clipping' }
# Verify archives against saved hashes, without generating tasks or rerunning learners.
foreach ($session in '009','010','011') {
    foreach ($p in Get-ChildItem "results/exp$session/confirmation/block_*.json") {
        $r=Read-Json $p.FullName
        $archive=[IO.Path]::ChangeExtension($p.FullName,'.npz')
        if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLower() -ne $r.sha256) { throw "Archive mismatch: $archive" }
    }
}
$result = [ordered]@{
    date='2026-09-16'; passed=$true
    scope='Read-only saved-checkpoint arithmetic, B/C source/development hashes and chronology, 72 A/B/C confirmation archive checksums; no scientific replay or new experiment; not independent scientific validation'
    source_hashes=$hashes; confirmation_blocks=@{A=24;B=$b.Count;C=$c.Count}
    B_gap=(Interval $bgap); B_loss=(Interval $bloss); C_gap=(Interval $cgap); C_loss=(Interval $closs); C_offline=(Interval $coff)
    C_selected_clipping_events=$clips
    legacy_validator='Not run; known obsolete count/schema remains unresolved'
}
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath research/session_d_record_check.json -Encoding utf8
[pscustomobject]$result | Select-Object date,passed,scope | Format-List
