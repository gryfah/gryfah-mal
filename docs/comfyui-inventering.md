# ComfyUI-inventering – C:\ComfyUI_windows_portable

**Inventering:** 2026-11-15 10:31:37 (lokal tid).  
**Källa:** lokalt körd PowerShell-inventering, `comfyui_inventering.json`.  
**Status:** installerade filer och vissa Git-commits inventerade; körbar Python/PyTorch-miljö och externa modellvägar **inte** verifierade.  
**Viktigt:** detta GitHub-repository är publikt. Inventeringen beskriver enbart filnamn, inte modellinnehåll. Ingen fil har körts eller funktionstestats av inventeringen.

## Installation och miljö

- Installation: `C:\ComfyUI_windows_portable`
- ComfyUI: `Comfy-Org/ComfyUI`, branch `master`, commit `eee59185ff4f43ae2d9ad122b245619d27d9daad`.
- `ComfyUI/main.py`: finns.
- `ComfyUI/extra_model_paths.yaml`: **finns**, men innehåll och refererade externa mappar har **inte** lästs. Alla nedanstående listor gäller bara lokala undermappar under `ComfyUI/models`.
- Skriptets `Environment` är **tomt objekt `{}`**. Ingen versionsinformation för ComfyUI:s Python, PyTorch, CUDA-runtime, Triton, SageAttention, xFormers, Transformers eller Diffusers kan utläsas. Detta är inte bevis för att paketen saknas.
- Systemets Python 3.15.2 enligt den separata datorinventeringen ska **inte** antas vara ComfyUI:s Python.
- Datorns separata hårdvaruinventering: RTX 5070 med 12 227 MiB VRAM, 16 GiB RAM, i7-9700K, Windows 11. Se [datorprofilen](datorprofil.md).

## Omfattning

**147 inventerade modellfiler**, varav **85** i standardkategorier och **62** i övriga modellmappar; **17** kataloger för custom nodes. Filtyper omfattar Safetensors, GGUF, PyTorch-checkpoints och ONNX. Filstorlekar i källrapporten är avrundade GiB, inte hashar. Mappar utan matchande fil kan ändå innehålla konfiguration, tokenizer, bilder eller andra filer som skriptet inte inventerar.

| Standardmapp | Antal modellfiler |
| --- | ---: |
| `vae` | 11 |
| `ipadapter` | 1 |
| `controlnet` | 2 |
| `loras` | 30 |
| `clip_vision` | 1 |
| `checkpoints` | 8 |
| `upscale_models` | 3 |
| `clip` | 2 |
| `unet` | 14 |
| `text_encoders` | 13 |
| `diffusion_models`, `diffusers`, övriga standardkategorier | 0 matchande modellfiler |

## Diffusionsmodeller – UNet (14 filer)

Alla nedan finns i `ComfyUI/models/unet`.

| Fil | GiB |
| --- | ---: |
| `boring_realism_v0_1.safetensors` | 12.239 |
| `finepornV5INT8FP8_v5FP8.safetensors` | 12.239 |
| `FinePorn_V6.1_INT8.safetensors` | 13.162 |
| `Krea2-V3.5-FP8_00001_.safetensors` | 12.239 |
| `krea2Sickrealism_v10_fp8.safetensors` | 12.239 |
| `krea2TurboFP8_krea2TURBO.safetensors` | 12.014 |
| `krea2_coloss_turbo_nsfw_fp8_scaled.safetensors` | 12.239 |
| `krea2_photographic_turbo_fp8_scaled.safetensors` | 12.239 |
| `Pornmaster_krea2_Turbo_int8_convrot_v4.safetensors` | 13.162 |
| `qwen_image_2.1_int8_convrot.safetensors` | 6.758 |
| `rawgirlKrea2_v20Fp8.safetensors` | 11.940 |
| `snofsSexNudesAndOther_krea2TurboV14.safetensors` | 11.948 |
| `Wan2_2-I2V-A14B-HIGH_fp8_e4m3fn_scaled_KJ.safetensors` | 13.973 |
| `Wan2_2-I2V-A14B-LOW_fp8_e4m3fn_scaled_KJ.safetensors` | 13.973 |

**Observera:** `models/diffusion_models` innehöll inga matchande filer. Det betyder inte att inga diffusionsmodeller finns; de ligger här huvudsakligen i `unet` samt `checkpoints`.

## Checkpoints (8 filer)

| Fil | GiB |
| --- | ---: |
| `Qwen-Rapid-NSFW-v23_Q4_K.gguf` | 12.426 |
| `rt_detr_v4-x-hgnet_fp32.safetensors` | 0.231 |
| `sam3.1_multiplex_fp16.safetensors` | 1.626 |
| `wan2.1_14B_SCAIL_2_nvfp4_mxpf8_mix.safetensors` | 10.267 |
| `wan22RemixT2VI2V_i2vHighV30-Q4_K_M.gguf` | 8.989 |
| `wan22RemixT2VI2V_i2vLowV30-Q4_K_M.gguf` | 8.989 |
| `Wan2_2-I2V-A14B-HIGH_consistent_face_Q4KM.gguf` | 8.989 |
| `Wan2_2-I2V-A14B-LOW_consistent_face_Q4KM.gguf` | 8.989 |

## Text encoders (13 filer)

| Fil | GiB |
| --- | ---: |
| `nsfw_wan_umt5-xxl_fp8_scaled.safetensors` | 6.273 |
| `qwen38BFluxKlein9BTE_38b.safetensors` | 15.256 |
| `qwen3vl_4b_bf16.safetensors` | 8.266 |
| `qwen3vl_4b_fp8_scaled.safetensors` | 4.882 |
| `qwen3vl_8b_int8_convrot.safetensors` | 8.709 |
| `qwenImage21TextEncoderOriginal_v10_3241887.safetensors` | 8.709 |
| `qwen_2.5_vl_7b_fp8_scaled.safetensors` | 8.740 |
| `qwen_3_4b.safetensors` | 7.492 |
| `qwen_3_8b_fp4mixed.safetensors` | 6.335 |
| `qwen_3_8b_fp8mixed.safetensors` | 8.070 |
| `qwen_3_8b_fp8mixed_abliterated.safetensors` | 7.629 |
| `teSolordzZimageKrea2_krea2SolordzTEV10.safetensors` | 8.266 |
| `umt5_xxl_fp8_e4m3fn_scaled.safetensors` | 6.273 |

Ytterligare `clip/clip_g.safetensors` (1.294 GiB), `clip/clip_l.safetensors` (0.229 GiB) och `clip_vision/clip_vision_h.safetensors` (1.177 GiB).

## VAE (11 filer)

`ae.safetensors` (0.312 GiB); `flux2 Vae.safetensors` (0.313); `full_encoder_small_decoder.safetensors` (0.232); `qwenImage21VAEOriginalBf16_v10.safetensors` (0.629); `qwen_image_vae.safetensors` (0.236); `Wan2.1_VAE.safetensors` (0.236); `Wan2.1_VAE_upscale2x_imageonly_real_v1.safetensors` (0.473); `wan2.2_vae.safetensors` (1.313); `Wan2_1_VAE_fp32.safetensors` (0.473); `wan_2.1_vae.safetensors` (0.236); `wan_2.1_vae_fp16.safetensors` (0.236).

Flera namn liknar varandra men är **inte bekräftade som identiska filer** (hashar saknas).

## LoRA-biblioteket (30 filer)

`bfs_body_swap_v1.0_qwen_2.1.safetensors`; `bfs_body_swap_v1_krea2.safetensors`; `bfs_head_swap_v1.1_krea2.safetensors`; `depth-control-lora.safetensors`; `krea-smartphone-photo-slider.safetensors`; `Krea2-realism-V2.safetensors`; `krea2_general_edit_v2_r64.safetensors`; `krea2_identity_edit_v1_2.safetensors`; `krea2_identity_edit_v1_2_r64.safetensors`; `krea2_identity_edit_v2.safetensors`; `krea2_raw_to_turbo_r256_comfy.safetensors`; `krea2_realism_lora.safetensors`; `krea2_realism_lora_comfy.safetensors`; `krea2_style_reference.safetensors`; `krea2_turbo_openpose_controlnet.safetensors`; `PornMaster_Flat_chest_&_Innie_pussy_krea2_V1.safetensors`; `PornMaster_Low_Resolution_Slider_Krea2_V1.safetensors`; `p_qwen_image_2.1_8step_v0.1_comfyui.safetensors`; `Qwen-Image-2512-Lightning-4steps-V1.0-fp32.safetensors`; `RawGirlV3.safetensors`; `realism_engine_krea2_v3.1.safetensors`; `realistic hyman face.safetensors`; `RealisticSnapshotKrea2V2.safetensors`; `refcontrol_v2_poses.safetensors`; `snofs_krea_v1_4.safetensors`; `snofs_photoSlider14B.safetensors`; `W22_NSFW_Posing_Nude_i2v_HN_v2.safetensors`; `W22_NSFW_Posing_Nude_i2v_LN_v2.safetensors`; `wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors`; `wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors`.

**Wan 2.2-relaterade filer:** två FP8-high/low-UNet, fyra GGUF high/low-checkpoints, två Wan22 pose-LoRA, två LightX2V-step-LoRA, UMT5-textencoder och Wan2.2 VAE. Det räcker inte för att fastslå exakta fungerande kombinationer; workflow-filer och kompatibilitet är inte inspekterade.

## Andra standardkategorier

- `controlnet`: `control_v11f1e_sd15_tile.pth` (1.346 GiB), `krea2_turbo_openpose_controlnet.safetensors` (0.213 GiB).
- `ipadapter`: `v3_sd15_adapter.ckpt` (0.095 GiB).
- `upscale_models`: `4x-UltraSharp.pth`, `4x_foolhardy_Remacri.pth`, `4x_NMKD-Superscale-SP_178000_G.pth` (var och en ~0.062 GiB).
- Följande standardmappar hade inga filer med inventerade modelländelser: `gligen`, `embeddings`, `photomaker`, `configs`, `hypernetworks`, `diffusion_models`, `style_models`, `audio_encoders`, `diffusers`, `model_patches`.

## Lokala språkmodeller – models/llm (24 GGUF-filer)

Filnamn och identifierbara familjer i rapporten:
- Gemma 4 E4B: Q6_K, Q4_K_M och multimodal projektor.
- Gemma 4 26B A4B: Balanced Q3_K_M och Q4_K_M, Heretic Q2_K samt multimodala projektorer.
- GPT-OSS-20B: Aggressive MXFP4 och en Heretic IQ1_M-variant.
- Dolphin/Mistral Nemo 12B: Q5_K_M.
- Qwen3 VL 4B: Q4_K_M plus projektor.
- Qwen3.8 27B: Q3_K_XL, Aggressive IQ2_M, Huihui IQ2_XS och projektorer.
- Qwen3.6 27B: multimodal projektor (huvudmodell **ej identifierad** i den mappen).
- Qwen3 8B: Huihui Q8_0.
- Qwen3.5 9B: Heretic Q5_K_M.
- Dirty-Muse-Writer: Q6_K.

Vissa projektorer är separata GGUF-filer; att de finns betyder inte att alla modell-/projektorkombinationer fungerar. Gemma4 Q3-/Q4-/Q2- och Qwen3.8 Q3-/IQ2-varianter är separata lokala modeller. Den exakta modellfilinventeringen finns i den ursprungliga `comfyui_inventering.json` från 2026-11-15.

## Övriga modellmappar (62 filer i 26 kataloger)

| Katalog | Antal | Exempel eller funktion |
| --- | ---: | --- |
| `background_removal` | 1 | BiRefNet |
| `detection` | 2 | SAM 3D Body DINOv3 BF16/INT8 |
| `face_detailer` | 1 | YuNet ONNX face detection |
| `frame_interpolation` | 1 | RIFE v4.26 |
| `geometry_estimation` | 1 | MoGe 2 |
| `interpolation` | 2 | FlowFormer/GIMM-VFI |
| `latent_upscale_models` | 1 | Flow upscaler |
| `llm` | 24 | GGUF-LLM/VLM och multimodala projektorer |
| `rembg` | 1 | BEN2 |
| `sams` | 1 | SAM ViT-B |
| `SEEDVR2` | 6 | 3B/7B GGUF samt FP8 och VAE |
| `ultralytics` | 14 | YOLO bbox/segm, face/eyes/hands/feet/body m.m. |
| `vae_approx` | 7 | TAEF/TAESD-varianter |
| Övriga (13 kataloger) | 0 | `annotator`, `clip_projections`, `facedetection`, `facerestore_models`, `genfocus`, `insightface`, `llama_cpp_runtime`, `luts`, `onnx`, `optical_flow`, `Qwen3-TTS`, `sam3`, `wan` |

Att `models/wan` är tom innebär inte att Wan saknas: Wan-filer finns i `checkpoints`, `unet`, `vae`, `loras` och `text_encoders`.

## Custom nodes (17 installerade kataloger)

| Katalog | Git-commit om rapporterad |
| --- | --- |
| `comfyui-custom-scripts` | Ej rapporterad |
| `comfyui-easy-use` | Ej rapporterad |
| `comfyui-fashn-human-parser` | `3674230adfe24ee2de36a2f649117adbeb95c541` |
| `ComfyUI-GGUF` | `6ea2651e7df66d7585f6ffee804b20e92fb38b8a` |
| `comfyui-kjnodes` | Ej rapporterad |
| `comfyui-krea2-ostris-edit` | `7756566160c4a1b24bb1bd9f0ff3ced1a83d7547` |
| `comfyui-krea2edit` | Ej rapporterad |
| `ComfyUI-PoseClothingBridge` | Ej rapporterad |
| `comfyui-switch-samplers` | `e716e3d8f77e44c04bdfc53c8ff5de6fa3e2dfbe` |
| `comfyui-videohelpersuite` | Ej rapporterad |
| `ComfyUI-WanVideoWrapper` | Ej rapporterad |
| `comfyui_essentials` | Ej rapporterad |
| `comfyui_layerstyle` | Ej rapporterad |
| `persontransfer` | Ej rapporterad |
| `PromptMaker_v48` | Ej rapporterad |
| `rgthree-comfy` | Ej rapporterad |
| `seedvr2_videoupscaler` | Ej rapporterad |

**Ej rapporterad Git-commit** kan bero på att katalogen saknar `.git` eller att Git-kommandot inte kunde läsa den; det innebär inte att noden är inaktiv.

## Prioriterade kunskapsluckor

1. **ComfyUI Python-miljön:** inbyggd Python-plats, version, `torch.__version__`, `torch.version.cuda`, CUDA-enhet, Triton, SageAttention, xFormers, FlashAttention och andra paket. Inventeringens `Environment={}` måste undersökas.
2. **`extra_model_paths.yaml`:** externa modellmappar kan innehålla ytterligare diffusion models, LoRA, checkpoints och text encoders. Inga externa sökvägar traverserades.
3. **Funktion/kompatibilitet:** katalogexistens säger inte att en custom node kan importeras; filnamn säger inte att en modell laddar eller fungerar med viss VAE/textencoder.
4. **Metadata:** exakta filstorlekar i byte, SHA-256 för deduplicering, Safetensors metadata (utan att läsa vikter) och GGUF-metadata behövs för säkrare identifiering.
5. **Prestanda:** faktisk VRAM-förbrukning, CPU-RAM-offloading, latens, upplösning, frames och samplerkonfiguration måste mätas.

## Arbetsregel för framtida projekt

Denna fil är referensen för vilka modellfiler som **fanns** vid inventeringen. Undvik att föreslå ny nedladdning av en modell som redan finns på listan innan versions- och filkompatibilitet kontrollerats. Läs datorprofilen för hårdvaran. Anta inte att en modell fungerar enbart för att filen finns; fråga bara efter ytterligare uppgifter när det påverkar beslutet.
