# GFit Pro, firmware access and custom watch information

Investigation: 2026-10-12. Priority set by owner: inspect the watch's OS/firmware and show custom computer information on its display. Button mapping is secondary. Only a custom host application is sought; installing a generic Linux health app is not a goal.

## Evidence from this specimen

| Item | Evidence | Limit |
| --- | --- | --- |
| Companion app | Owner confirms GFit Pro from Apple's App Store | Android inspection below is a separate platform |
| Firmware displayed by app | Current and latest: **1.0.0.4** | App-reported version, not a firmware-image hash |
| Restoration screen | **pid:76 version:1004 type:0** | Meaning of type 0 has not been decoded |
| App release | Owner reports App Store history lists **1.4.5**, four months earlier | Installed iOS build number not independently retrieved |
| Manual descriptor | `watch_type=ultra2`, title Square watch / 方表 | Vendor tutorial category, not authenticated board identity |
| BLE | AE00 / AE01 / AE02 verified on Linux | Application commands and authentication untested |
| Media control | KEY_PLAYCD / KEY_PAUSECD observed on Linux | Does not establish screen output or OS access |

The firmware values were transcribed from the owner's `photo_2026-10-12_20-57-06.jpg` and `photo_2026-10-12_20-57-07.jpg`. Original photos remain outside this public repository. They supersede the earlier `v1001` report as the latest app-visible observation; the historical marking is retained in the dossier. The owner recalls a previous app firmware update, with uncertainty about that memory.

The restoration screen says the feature is intended for a malfunctioning watch and can leave it unusable. It was inspected as evidence; no Detect/Upgrade/Restore operation was initiated. Its existence establishes an app update feature, not a working recovery guarantee, root access, or permission to load arbitrary code.

## Manual and vendor website inspection

The [owner's manual page](https://awsfile.gssdfit.com/gfitProPhone/index.html#/pages/enVideo/index?language=en&watch_type=ultra2&zhTitle=%E6%96%B9%E8%A1%A8&enTitle=Square%20watch) is a JavaScript tutorial application. Offline inspection of its referenced assets found hardcoded Bilibili video IDs and an `ultra2` tutorial selection. The assets did not provide a firmware catalogue or matching image.

Relevant fetched assets:

- `static/js/index.26091567.js`
- `static/js/pages-enVideo-index.d6c9a1a1.js`
- `static/js/pages-enVideo-index~pages-zhVideo-index.85e2ad5a.js`

The video component embeds Bilibili for its video IDs. An English route does not imply English video content. The platform filter also uses `t.type !== device_model`, which appears to exclude that platform's entries; actual browser behavior was not tested. Labels such as app download and menu replacement describe tutorials, not evidence of a native third-party app loader.

The [vendor's current website](https://gssdfit.com/pc/download) links, through a decoded download QR, to its [GS Fit landing page](https://apppage.gssdfit.com/landingpage/index.html). That page supplies a [vendor-hosted GS Fit APK](https://gshardware.oss-cn-shenzhen.aliyuncs.com/app/gsfit/gsfit.apk). **GS Fit and GFit Pro are different app identities.** No compatibility substitution was made. The older GFit Pro website URL returned 404.

GFit Pro's [published policy](https://apppage.gssdfit.com/gfitPro/xieyi/privacy_policy.html) describes the app as supplying the upgrade path while manufacturers supply device firmware. It also describes message/notification delivery, although that broad description is not a packet specification for this specimen.

## Offline app inspection and provenance

An Android GFit Pro XAPK was retrieved through a link in a fetched [APKPure download page](https://apkpure.net/gfit-pro/com.app.cy.GFit/download). It was inspected, not installed or executed. This mirror is acquisition provenance; it does not independently authenticate the publisher or iOS implementation.

| Artifact | Observed identity / SHA-256 |
| --- | --- |
| Mirrored Android base APK | `com.app.cy.GFit`, version **1.4.5**, code **42**; `37aa539669470c402bd064fd252c7daccb90548be8170c3af63b2be2498192b7` |
| Mirrored XAPK | `e7f6bc32b20bbabcbb7ad174c03c2ebbe893705395c81217ccd83403e2cc7fa3` |
| Vendor GS Fit APK, separate comparison | `ca186f83f6d1441523ffd70789114f3291d748b83723b4c68a7975e3fa119d2f` |

The Android GFit package contains Jieli RCSP and Bluetooth OTA classes, plus ARM64 `libjl_auth.so`, `libjl_ota_auth.so`, FAT filesystem and resource-processing libraries in its architecture split. Its internal application classes use `com/app/cy/GsFit` despite the external GFit package identity. These observations strengthen the Jieli protocol-family lead, together with the specimen's UUIDs and historical framing markers. **They still do not identify the watch's main MCU.** An app may support several hardware families or a separate Bluetooth controller.

No bundled `.ufw` or `.fw` firmware image was found in the inspected packages. App binaries, disassembly, native libraries, raw responses and research dependencies remain local under ignored `captures/gfit-research/` or `.venv/`. They are not redistributed here. No app keys or user tokens are published.

## Firmware lookup: concrete mechanism, unresolved image

Offline disassembly of Android GFit Pro 1.4.5 identifies:

| Code location | Observed behavior |
| --- | --- |
| `NetCfg.domainUrl` | Base `https://awsapp.gssdfit.com/abroad/awsd/` |
| `NetApi.getFirmware` | HTTP POST `ota/pidVersion` |
| `NetApi.getFirmwareForce` | HTTP POST `ota/userPidVersion` |
| `UpgradeViewModel.queryOtaMsgForServer` | Supplies PID, version, MAC and optional logged-in user ID |
| `UpgradeViewModel.otaPrepare` | Removes `V_` and dots from the device version before lookup |
| `FirmwareOTAEntity` | Contains firmware filename and URL fields, accessed by `getFwareName` / `getFwareUrl` |
| `NetApi.downloadFirmware` | HTTP POST `ota/piddownload`; caller supplies `fwareUrl` |
| `RetrofitHelper.packParams` | App-specific AES/RSA request envelope, with app name/version |
| Request interceptor | Adds timestamp-based app header and account authorization when available |

These paths were extracted from code, not guessed from domain names. Metadata lookup and binary retrieval are distinct from Bluetooth transfer to the watch. The update state machine also distinguishes firmware and watch-resource work.

A bounded metadata query for PID 76/version 1004 used no owner account credentials and no real device MAC. The initial minimal wrapper returned empty HTTP 200. A request with the app header returned `flag:false`, `code:422`, `message:"Token error or expired"`, `data:null`; correcting the timestamp to seconds produced the same result. This is a server rejection of these research requests, not proof of an unavailable firmware or of which credential would resolve it. No login token was borrowed or account restriction bypassed.

**Result: the exact PID-76 / 1.0.0.4 firmware image has not been obtained.** No matching public release was identified in the searched vendor, app and source repositories. An authenticated app metadata response or already cached download is the strongest next source. Capture only the relevant response/cache without starting Upgrade/Restoration; redact account/device identifiers before sharing. Restoration should not be used merely to create a download for research.

The [official Jieli health demo](https://github.com/Jieli-Tech/Android-JL_Health) queries OTA using product/vendor identifiers, and its [upgrade view model](https://github.com/Jieli-Tech/Android-JL_Health/blob/main/code/app/HealthAide_V1.1.0_SDK_V1.14.0/app/src/main/java/com/jieli/healthaide/ui/device/upgrade/UpgradeViewModel.java) accepts `.ufw`, `.buf` and OTA ZIP files. This establishes candidate formats in that SDK, not this watch's actual container, signatures or flash layout.

## Routes to custom information on the display

| Route | Concrete source evidence | Next proof needed |
| --- | --- | --- |
| Text notifications | Official SDK `pushMessageInfo(NotificationMsg)`; example constructs title/content | Specimen authentication, supported notification command and a fixed synthetic text display |
| Existing task/reminder UI | GFit's task view model sends RCSP commands | Supported task operation and actual rendering on PID 76 |
| Custom watch-face/background resources | SDK offers `enableWatchCustomBg`, `createWatchFile`, watch-file listing; GFit calls related operations | Compatible format, dimensions, capacity and reversible resource replacement |
| Media metadata | Existing Classic control connection and standard host media interfaces | Whether this watch renders track/title metadata |
| Native dedicated UI | Vendor watch development material and custom firmware work on other Jieli devices | Actual MCU/board, matching original image, memory map, validation rules and proven recovery |

The [official API reference](https://doc.zh-jieli.com/Apps/Android/health/en-us/master/Development/interface_desc.html) and [notification example](https://github.com/Jieli-Tech/Android-JL_Health/blob/main/code/app/HealthAide_V1.1.0_SDK_V1.14.0/app/src/main/java/com/jieli/healthaide/tool/notification/NotificationHelper.java) are concrete starting points for a custom host bridge. The app's task methods and SDK resources are capabilities of that software; none has yet been exercised on this specimen. File/resource access would not by itself expose an OS shell or arbitrary executable loading.

The proposed first display test is a fixed, nonprivate message such as `Mero: agent idle`. It is not yet a validated packet. Derive authentication and message serialization from compatible sources/observed app traffic before a watch write is proposed. Do not replay the unknown historical packet as a command.

## Native access and reverse-engineering tools

- [Jieli's watch development index](https://doc.zh-jieli.com/KDocs/master/%E6%89%8B%E8%A1%A8%E7%A9%BF%E6%88%B4%E6%8A%80%E6%9C%AF%E5%BA%94%E7%94%A8%E6%96%87%E6%A1%A3%E5%85%A5%E5%8F%A3%E6%B1%87%E6%80%BB/) links filesystem, UI editor, upgrade, AC701N/AC707N and display development material. It is platform research, not identification of PID 76.
- [ElectronicCats' Jieli badge research](https://github.com/ElectronicCats/jieli-ble-badge-research) publishes firmware build/recovery work for an **AC707N/BR35 E87 badge**, including UFW tools and a Python authentication implementation. [Its build record](https://github.com/ElectronicCats/jieli-ble-badge-research/blob/main/docs/jieli-sdk-build.md) is evidence that custom firmware is feasible on that different hardware. Its image is not compatible firmware for this watch.
- [The Python authentication implementation](https://github.com/ElectronicCats/jieli-ble-badge-research/blob/main/tools/qix-ble/qix_ble/auth.py) and [upstream E87 client](https://github.com/hybridherbst/web-bluetooth-e87) offer candidates for a Linux client without executing an Android native library. Authentication/framing compatibility must be checked; their hardware-specific commands were not sent here.
- [jl-misctools](https://github.com/kagaimiq/jl-misctools) provides firmware unpacking tools; select a parser only after inspecting the actual image. Do not assume one UFW layout fits every generation.
- [ghidra-jieli](https://github.com/kagaimiq/ghidra-jieli) adds processor support for some Jieli custom CPUs. Choosing the correct architecture remains a prerequisite for useful watch firmware disassembly.
- Owner-suggested [ReverseEngineerAnything](https://github.com/sgunin/ReverseEngineerAnything) connects agents to Hopper/Ghidra and supports app/archive/native-binary investigation. Its README lists Linux/Arch requirements and APK/IPA inspection. It was reviewed as a tooling candidate, not installed. It does not supply this watch's firmware, unlock its OS or eliminate architecture requirements.

**OS access remains unproven.** No shell, root account, boot console, application loader, specific RTOS, signed-image policy or chip identity has been established. The copied A2859 identifier cannot select a firmware target. Firmware availability and OTA support alone do not establish arbitrary code execution.

## Next investigation order

1. Obtain a redacted metadata response or cached image from the owner's authenticated GFit Pro session, without a firmware-transfer operation.
2. Inspect the image offline: hash, container entries, strings, architecture clues, resource partitioning and integrity/signature behavior. Keep original bytes unchanged.
3. Correlate GFit initialization/authentication and a synthetic notification with the specimen's BLE channel. This can establish a custom information path independently of native firmware replacement.
4. Implement the smallest custom Linux status sender after that display test succeeds. Keep the native-access branch active until hardware/image/recovery evidence can support a decision.

Research limitations: upstream repository-import tools returned 504; direct GitHub API/raw retrieval succeeded. Some browser fetches failed while direct HTTPS worked. No full authenticated phone traffic was captured. No speculative GATT write, OTA transfer, restoration, firmware execution, physical opening or flash programming occurred.

## 2026-10-12: owner-session capture and matching firmware acquired

This follow-up supersedes the earlier unresolved retrieval status. The owner configured the iPhone Wi-Fi proxy, installed the temporary capture certificate and enabled trust. HTTPS inspection was restricted to the vendor domains; only firmware-route bodies were retained locally. Raw captures, certificate material, request encryption material and binary artifacts remain in ignored `captures/`, outside the public repository.

**Observed:** GFit Pro's normal `ota/pidVersion` check returned code `1024`, saying there was no latest firmware for this device. This did not mean the restoration package was unavailable. An `ota/userUpgradeOta` response returned code `200` and encrypted metadata. Decoding it using the client response-envelope implementation inspected in the Android app produced:

| Field | Observed value |
| --- | --- |
| PID / version / OTA type | `76` / `1004` / `0` |
| Filename | `update1004.ufw` |
| Vendor file reference | `/opt/gssd/file/ota/square/pid76/update1004.ufw` |
| MD5 | `550f4fcf32916da3a2dbb77c9510ee3e` |
| English description | `Performance optimization, voluntary resource upgrade` |
| Size field | `18320`; units not established by the response |

These identifiers match the owner's firmware screenshots. There was no public download URL. A computer-side POST to the app's documented `ota/piddownload` route, with encrypted `fwareUrl` parameters and the live app session headers held only in memory, retrieved the package. An initial attempt forwarded a selected set of headers and received a 73-byte code `422` token-error response; it was rejected as firmware. A subsequent request using the complete applicable app headers succeeded. No firmware-transfer command was sent to the watch.

**Observed artifact:** `18,760,384` bytes; MD5 exactly matches the metadata above; SHA-256 `5f315a22adada0c7933afa89558b5d1e9be577ede10f9dbc5a53cd82c2c23145`. This is a matching vendor restoration package, not a physical dump of the watch's flash. The checksum establishes consistency with the vendor response; it does not establish a cryptographic signature or an unlocked update policy.

### Offline container and board evidence

The [jl-misctools source at commit 0a5b12d](https://github.com/kagaimiq/jl-misctools/tree/0a5b12db0ef38f3042acffbe2452730a37fd2405/firmware) was inspected before use. A local copy added checks against archive filenames escaping the extraction directory. The original firmware bytes were preserved.

**Observed:** the decoded UFW header labels the chip `JL701N`. Its header and entry-table CRC checks passed. Its image-size field equals the complete downloaded file length. Selected outer entries are:

| Entry | Bytes | Observation |
| --- | ---: | --- |
| `res.bin` | 15,878,720 | Resource container; contains a bounded `new_res.bin` payload of 15,878,656 bytes |
| `ota.bin` | 203,879 | Includes `BR28_EDR_UPDATE` and `BR28_BLE_UPDATE` strings |
| `flash.bin` | 1,339,392 | Successfully unpacked application and boot resources |
| `flash2.bin` | 1,335,808 | Successfully unpacked; extracted component files match those from `flash.bin` byte for byte |

These four payloads passed the entry CRC calculation used by the inspected tool. Several small auxiliary entries did not match that same calculation; their encoding/checksum treatment remains unresolved. Do not claim every entry has been validated.

Each flash image yielded 31 files, including `app.bin` (1,200,992 bytes), `uboot.boot`, `user_api.bin`, `p11_code.bin`, configuration, tones and upgrade UI resources. The application contains a source-path suffix `PID76/sdk/apps/watch/board/br28/board_7012AF_J1/board_7012AF_J1.c`, `br28_draw_image`, and RCSP update strings. The second outer flash image also contains an `ac701_uboot_lcd_ui_0.0.1` source-path fragment.

**Interpretation:** independent package and code evidence strongly supports the Jieli AC701/BR28 family and a firmware build targeting `7012AF_J1`. This is substantially stronger than the earlier AC695X/Realtek theories. It is still evidence from the matching package, not a chip-marking inspection or running CPU identification. An `AC697N_ble_test` string and an older AC695N library version string also occur; these are insufficient to override the board-path and package evidence or identify the physical chip.

**Still unproven:** the exact CPU instruction-set target, RTOS identity, debug-port access, an interactive shell, arbitrary-code loading and firmware signature enforcement. UART/update strings alone do not prove an accessible console. The large resource payload still needs format analysis; its presence does not establish that custom apps can run.

The next offline work is to correlate the AC701/BR28 board evidence with the appropriate SDK and disassembler, map the application/resource layout, and trace the existing text/notification display path. A synthetic computer-status display remains the first practical bridge experiment once its protocol is explained. Flashing and restoration are separate experiments requiring approval and a recovery plan.

### Capture cleanup

**Observed on host:** both capture listeners were stopped; both temporary firewall rules were removed; verification found no listener on either capture port and no capture rule remaining. **Owner-reported:** iPhone Wi-Fi proxy switched off and certificate trust disabled. The owner chose to retain the certificate profile for possible future analysis; removal was not confirmed. Private capture setup and artifacts are retained locally for that purpose. No permanent firewall change was made.
