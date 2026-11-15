# Datorprofil – gemensam referens för AI-projekt

**Status:** Ofullständig – hårdvaran är ännu inte inventerad på den faktiska datorn.  
**Senast sammanställd:** 2026-11-15  
**Princip:** Okänt betyder inte noll, saknas eller inkompatibelt. Gissa aldrig hårdvaruvärden.  
**Integritet:** Publicera inte datornamn, användarnamn, serienummer, MAC-adresser, IP-adresser, licensnycklar eller personliga filvägar här.

## Verifierat genom tidigare användaruppgifter

| Område | Uppgift | Säkerhet |
| --- | --- | --- |
| Plattform | Windows-PC | Användaruppgift |
| Gränssnitt för generativ AI | ComfyUI körs lokalt | Användaruppgift |
| Bild-/videoprojekt | Lokala flöden för bild/video; Wan används/utvärderas | Användaruppgift |
| Lokala språkmodeller | Gemma 26B har nämnts i planerade arbetsflöden | Avsedd användning; installation ej verifierad |
| Lagring | SSD finns, och diskuteras i samband med nästan fullt lagringsutrymme | Användaruppgift; storlek okänd |
| Windows-växlingsfil | Finns/har funnits | Användaruppgift; nuvarande inställning okänd |

## Hårdvara – inväntar lokal inventering

| Komponent | Exakt modell / kapacitet | Status |
| --- | --- | --- |
| Processor (CPU), kärnor/trådar | Okänt | Ej avläst |
| Moderkort och BIOS/UEFI | Okänt | Ej avläst |
| Installerat RAM | Okänt | Ej avläst |
| Grafikkort (GPU), eventuella flera kort | Okänt | Ej avläst |
| Dedikerat grafikminne (VRAM) | Okänt | Ej avläst |
| Grafikdrivrutin | Okänt | Ej avläst |
| CUDA-drivrutinsstöd / CUDA Toolkit | Okänt | Ej avläst |
| Diskar: modell, typ, storlek och ledigt utrymme | Okänt | Ej avläst |
| Windows-utgåva, version och build | Okänt | Ej avläst |
| Python och PyTorch | Okänt | Ej avläst |
| ComfyUI-version och installationsvariant | Okänt | Ej avläst |
| GPU-kylning/temperatur under belastning | Okänt | Ej mätt |
| Nätaggregat och effektgränser | Okänt | Kräver separat kontroll |
| Skärmupplösning | Okänt | Ej avläst |

## AI-kapacitet – får inte antas innan inventeringen är klar

För ComfyUI, diffusion och Wan ska bedömningar baseras på **GPU-modell, faktisk dedikerad VRAM, drivrutin, PyTorch/CUDA-version, RAM, ledigt diskutrymme, modellstorlek, precision och offloading**. CUDA-värdet i `nvidia-smi` är drivrutinens högsta stödda CUDA-version, inte nödvändigtvis den installerade CUDA Toolkit-versionen. *Delat* GPU-minne är inte samma sak som dedikerat VRAM.

När mätvärden har hämtats, fyll även i:
- Verifierat fungerande modeller, upplösningar, batchstorlekar och videolängder.
- Faktiska minnesgränser, genereringstid och vanliga out-of-memory-fel.
- Placering av modellbibliotek (endast generiska enhetsbeteckningar; inga privata sökvägar).
- Eventuell samkörning med andra processer på grafikkortet.
- Versionslåsningar och kända kompatibilitetsproblem.

## Engångsinventering på Windows

Öppna **PowerShell** på datorn och kör nedanstående kod. Den ändrar inte systeminställningar. Den läser maskinuppgifter och skriver en rapport på skrivbordet. Läs igenom rapporten innan du delar den. Rapporten utelämnar avsiktligt datornamn, användarnamn, serienummer, nätverksidentifierare och lokala installationssökvägar.

```powershell
$ErrorActionPreference = 'SilentlyContinue'
$report = [ordered]@{}
$os = Get-CimInstance Win32_OperatingSystem
$cpu = @(Get-CimInstance Win32_Processor)
$board = Get-CimInstance Win32_BaseBoard
$bios = Get-CimInstance Win32_BIOS
$ram = @(Get-CimInstance Win32_PhysicalMemory)
$gpu = @(Get-CimInstance Win32_VideoController)
$disks = @(Get-CimInstance Win32_DiskDrive)
$volumes = @(Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3")
$report['Inventeringsdatum'] = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')
$report['Windows'] = [ordered]@{ Caption=$os.Caption; Version=$os.Version; Build=$os.BuildNumber; Architecture=$os.OSArchitecture }
$report['CPU'] = @($cpu | ForEach-Object { [ordered]@{ Model=$_.Name.Trim(); Cores=$_.NumberOfCores; Threads=$_.NumberOfLogicalProcessors } })
$report['Motherboard'] = [ordered]@{ Manufacturer=$board.Manufacturer; Product=$board.Product; BIOSVersion=($bios.SMBIOSBIOSVersion -join ', ') }
$report['RAM'] = [ordered]@{
  TotalGiB=[math]::Round(($ram | Measure-Object -Property Capacity -Sum).Sum / 1GB,2)
  Modules=@($ram | ForEach-Object { [ordered]@{ CapacityGiB=[math]::Round($_.Capacity/1GB,2); SpeedMHz=$_.Speed; ConfiguredClockMHz=$_.ConfiguredClockSpeed; Manufacturer=$_.Manufacturer; PartNumber=$_.PartNumber } })
}
$report['GPU'] = @($gpu | ForEach-Object { [ordered]@{ Name=$_.Name; DriverVersion=$_.DriverVersion; AdapterRAM_ReportedBytes=$_.AdapterRAM } })
$report['PhysicalDisks'] = @($disks | ForEach-Object { [ordered]@{ Model=$_.Model; Interface=$_.InterfaceType; SizeGiB=[math]::Round($_.Size/1GB,2); MediaType=$_.MediaType } })
$report['Volumes'] = @($volumes | ForEach-Object { [ordered]@{ Drive=$_.DeviceID; SizeGiB=[math]::Round($_.Size/1GB,2); FreeGiB=[math]::Round($_.FreeSpace/1GB,2) } })
$report['Python'] = (& python --version 2>&1 | Out-String).Trim()
$report['PyTorch'] = (& python -c "import torch; print('torch='+torch.__version__); print('torch_cuda='+str(torch.version.cuda)); print('cuda_available='+str(torch.cuda.is_available())); print('gpu_names='+str([torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]))" 2>&1 | Out-String).Trim()
$report['NvidiaSMI'] = (& nvidia-smi --query-gpu=name,driver_version,memory.total,memory.free --format=csv,noheader,nounits 2>&1 | Out-String).Trim()
$report['NvidiaSMI_DriverCUDA'] = (& nvidia-smi 2>&1 | Select-Object -First 4 | Out-String).Trim()
$report['CUDA_Toolkit'] = (& nvcc --version 2>&1 | Out-String).Trim()
$report['DirectX'] = 'Ej insamlat'
$out = Join-Path ([Environment]::GetFolderPath('Desktop')) 'datorinventering.json'
$report | ConvertTo-Json -Depth 8 | Set-Content -Path $out -Encoding UTF8
Write-Host "Inventering skapad: $out"
```

**Viktigt:** Om ett kommando saknas är det inte bevis för att motsvarande program saknas i alla Python-/ComfyUI-miljöer. En separat ComfyUI-virtuell miljö kan ha andra paket än det `python` som finns i PATH. Win32_VideoControllers rapporterade AdapterRAM kan vara fel eller begränsat; använd i första hand `nvidia-smi` för NVIDIA-kort.

## Användning i framtida projekt

Använd den här filen som gemensam referens när du bedömer datorns prestanda, modellkompatibilitet och minnesgränser. Kontrollera **status och inventeringsdatum** innan en uppgift används som fakta. Hämta alltid de verkliga maskinvärdena från användarens insamlade rapport, inte från lösa antaganden eller gamla resonemang.

**Nästa steg:** Kör engångsinventeringen, granska `datorinventering.json` och dela resultatet. Ersätt därefter alla `Okänt`-fält med verifierade uppgifter och datum.
