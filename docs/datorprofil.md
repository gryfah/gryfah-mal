# Datorprofil – gemensam maskinreferens

**Inventerad:** 2026-11-15 10:20:48 (Europe/Stockholm)  
**Källa:** Lokalt insamlad `datorinventering.json` från Windows PowerShell.  
**Status:** Kärnhårdvara verifierad; AI-miljön och vissa komponenter återstår att inventera.  
**Integritet:** Serienummer, datornamn, användarnamn, MAC/IP, licensnycklar och privata sökvägar ska inte läggas in i denna publika fil.

## Sammanfattning för alla projekt

| Del | Verifierad specifikation |
| --- | --- |
| Operativsystem | Windows 11 Home, 64-bit, version 10.0.26300, build 26300 |
| Processor | Intel Core i7-9700K @ 3,60 GHz; **8 kärnor / 8 trådar** |
| Moderkort | Alienware **0T76PD** |
| BIOS | **1.0.26** |
| Arbetsminne | **16 GiB** (2 × 8 GiB), **2400 MHz** konfigurerat |
| Diskret GPU | **NVIDIA GeForce RTX 5070** |
| Dedikerat GPU-minne | **12 227 MiB (~11,94 GiB)** enligt `nvidia-smi` |
| NVIDIA-drivrutin | **621.24** enligt `nvidia-smi` |
| CUDA UMD (drivrutinsrapport) | **13.5** – inte ett mått på installerat CUDA Toolkit |
| Integrerad GPU | Intel UHD Graphics 630 |
| Identifierad fysisk SSD | **Predator SSD GM7 4TB**, rapporterad storlek **3815,44 GiB** |
| C: | **3814,33 GiB** totalt; **1861,77 GiB** ledigt vid inventering |
| G: | **2054 GiB** totalt; **1484,46 GiB** ledigt vid inventering |
| Python i PATH | **Python 3.15.2** |
| PyTorch i ComfyUI | **2.10.0+cu130**, verifierat i startlogg 2026-11-15 |
| ComfyUI | **0.45.0**, Python **3.13.14**, portable installation; [detaljinventering](comfyui-inventering.md) |

## Hårdvarudetaljer

### CPU / moderkort / RAM

- Intel(R) Core(TM) i7-9700K CPU @ 3.60GHz; 8 fysiska kärnor och 8 logiska processorer.
- Alienware 0T76PD, BIOS 1.0.26.
- Två minnesmoduler om 8 GiB vardera, 2400 MHz rapporterad och konfigurerad hastighet.
- RAM-modulernas rapporterade artikelnummer: `XJ69DF-MIE` (båda). Tillverkarkoden `01980000802C` är inte tolkad.
- Kanaler, faktiskt timings, lediga DIMM-platser och maximal stödd kapacitet är inte verifierade.

### Grafik och drivrutiner

| Adapter | Windows-drivrutinsversion | Kommentar |
| --- | --- | --- |
| NVIDIA GeForce RTX 5070 | 32.0.16.2124 | `nvidia-smi` anger 621.24 |
| Intel UHD Graphics 630 | 27.20.100.9664 | Integrerad grafik |

`nvidia-smi` rapporterade **12227 MiB totalt GPU-minne** och **11158 MiB ledigt** vid inventeringstillfället, alltså ungefär **1069 MiB upptaget**. Dessa siffror är en ögonblicksbild, inte konstant tillgängligt minne.

**Viktigt:** Windows `Win32_VideoController.AdapterRAM` rapporterade ~4 GiB för RTX 5070, men denna äldre WMI-egenskap är olämplig för att fastställa VRAM på moderna kort. **Använd 12227 MiB från `nvidia-smi`**, inte 4 GiB.

Drivrutinens CUDA UMD-version **13.5** visar drivrutinsmiljön; installerad CUDA Toolkit och PyTorch CUDA-runtime är fortfarande **okända**. GPU:ns belastningstemperatur, TGP och faktisk uthållig prestanda är inte uppmätta.

### Lagring

Inventeringen listade **en identifierad fysisk disk**, Predator SSD GM7 4TB (3815,44 GiB). Windows klassificerade den under `Win32_DiskDrive` som `SCSI` och `Fixed hard disk media`; dessa generiska fält ska **inte** användas för att dra slutsatsen att disken är en mekanisk hårddisk.

| Volym | Kapacitet | Ledigt | Kommentar |
| --- | ---: | ---: | --- |
| C: | 3814,33 GiB | 1861,77 GiB | Matchar storleksmässigt den identifierade 4 TB-disken |
| G: | 2054 GiB | 1484,46 GiB | **Fysisk bakomliggande lagring ej identifierad** |

**Anmärkning:** G: syns som separat logisk volym men inte som separat enhet i rapportens lista över fysiska diskar. Anta inte att båda volymerna ligger på samma disk, och summera inte volymerna som verifierad fysisk kapacitet. Möjliga förklaringar kräver ytterligare inventering.

## ComfyUI-installation – separat inventering 2026-11-15

En fördjupad inventering av `C:\\ComfyUI_windows_portable` finns i **[ComfyUI-inventeringen](comfyui-inventering.md)**. Den dokumenterar ComfyUI Git-commit `eee59185ff4f43ae2d9ad122b245619d27d9daad`, **147 modellfiler** inklusive UNet, Wan, LoRA, text encoders, VAE, GGUF och **17 custom-node-kataloger**. `extra_model_paths.yaml` finns, men dess externa sökvägar har inte inventerats. **Aktiva ComfyUI-versioner är nu verifierade genom startloggen:** Python 3.13.14, PyTorch 2.10.0+cu130, ComfyUI 0.45.0. [Hela det maskinläsbara modellregistret](comfyui-modellregister.json) omfattar samtliga 147 inventerade filer.

## Mjukvara och lokala AI-flöden

- Windows 11 Home 64-bit, build 26300.
- `python --version` gav **Python 3.15.2** i den miljö där inventeringsskriptet kördes.
- Den ursprungliga inventeringens `PyTorch`-fält var **tomt**, men senare **ComfyUI-startlogg verifierar PyTorch 2.10.0+cu130** i installationens inbyggda Python 3.13.14. System-Python 3.15.2 är separat.
- `CUDA_Toolkit` fanns inte som fält i den uppladdade rapporten. Status **okänd**.
- `DirectX` markerades **ej insamlat**.
- ComfyUI **0.45.0**, Python **3.13.14**, PyTorch **2.10.0+cu130** och DynamicVRAM/offloading verifierades i uppstartsloggen. Wan-, Krea2-, Qwen- och GGUF-modellfiler samt custom nodes är dokumenterade i [ComfyUI-inventeringen](comfyui-inventering.md). Faktiska workflow-prestanda och fungerande modellkombinationer är fortfarande ej verifierade.

## Praktiska riktlinjer för modellval och felsökning

Maskinen har **cirka 12 GiB dedikerat GPU-minne** och **16 GiB system-RAM**. Dessa två pooler är inte utbytbara med samma prestanda. Vid förslag om ComfyUI, Wan, LLM eller uppskalning ska en lösning utvärderas med dessa utgångsvärden; antag **inte** 16+12 GiB som en gemensam snabb minnespool.

- Vid GPU-minnesproblem: kontrollera modellprecision/kvantisering, upplösning, antal frames, batchstorlek, samtidiga processer, temporära buffertar och offloading.
- Vid CPU/RAM- och diskbaserad offloading kan **16 GiB RAM** vara den praktiska flaskhalsen även om grafikkortet inte är fullt.
- Ge inte exakta prestandalöften utan test; CPU-generation, PCIe, minnesbandbredd, GPU-minne och implementation kan påverka kraftigt.
- Kontrollera tillgängligt VRAM vid körtillfället: inventeringens lediga 11158 MiB gäller endast klockslaget ovan.
- Håll isär drivrutin (621.24), CUDA UMD (13.5), CUDA Toolkit (okänd), PyTorch CUDA-runtime (okänd) och ComfyUI:s Python (okänd).

## Återstående kontrollpunkter

1. **ComfyUI:** installation, Python, PyTorch, CUDA-enhet, ComfyUI-commit/version och importerade custom nodes är verifierade. Återstår: exakt version på fler paket, extra modellvägar, metadata om modellernas faktiska innehåll och funktionstester.
2. **G:-volymens lagring:** fysisk enhet eller annan underliggande volymteknik; anslutningstyp och verkligt ledigt utrymme.
3. **System:** nätaggregat, GPU-variant, temperaturer vid last, RAM-uppgraderingsmöjligheter, växlingsfilens storlek och lagringsplats.
4. **Arbetsflöden:** uppmätta genereringstider, fungerande videolängder och resolutioner, modeller/precision, VRAM-toppar samt dokumenterade OOM-fel.

### Fördjupad kontroll vid behov

Kör i ComfyUI:s **egen Python-miljö**, inte nödvändigtvis den `python` som finns i PATH:

```powershell
python -c "import sys, torch; print('Python:',sys.version); print('PyTorch:',torch.__version__); print('Torch CUDA:',torch.version.cuda); print('CUDA available:',torch.cuda.is_available()); print('GPUs:',[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())])"
```

För kopplingen mellan G: och fysisk disk kan Windows PowerShell-kommandona `Get-Volume`, `Get-Partition` och `Get-Disk` användas. Granska resultaten och utelämna unika enhetsidentifierare före publicering.

## Referenspolicy

Detta är **den gemensamma maskinprofilen** för framtida projekt. Läs den när datorns förmåga, prestanda eller kompatibilitet diskuteras. Håll isär **uppmätt**, **uppgivet** och **okänt**. Uppdatera datum och värden när datorn uppgraderas. Datorprofilen är en statisk ögonblicksbild, inte liveövervakning.
