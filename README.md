# Film Festival Format Checker

An automated **video format compliance checker and converter** for the (fictional) *Narbonne Online Film Festival*, written in Python with **FFmpeg**. It reads each submitted film's technical details with `ffprobe` and compares them with the festival's required format. Any film that doesn't comply is converted automatically with `ffmpeg`, and a text report is written.

Exercise 3 of the Intelligent Signal Processing final coursework.

## Required format

| Property | Requirement |
|---|---|
| Container | MP4 |
| Video codec | HEVC (H.265) |
| Audio codec | AAC |
| Frame rate | 25 FPS |
| Resolution / aspect ratio | 640×360, 16:9 |
| Video bitrate | 2–5 Mb/s |
| Audio bitrate | up to 256 kb/s |
| Audio channels | 2 (stereo) |

## How it works

1. **Scan** `Exercise3_Files/` for videos (`.mp4`, `.avi`, `.mov`, `.mkv`, `.flv`, `.wmv`).
2. **Probe** each file with `ffprobe` (JSON output) for container, codecs, resolution, frame rate, bitrates and channels.
3. **Check** every property against the required format and list each problem with its current and required value.
4. **Convert** non-compliant films with `ffmpeg`:
   - **Video:** `libx265` at 3.5 Mb/s, 640×360, 25 FPS, 16:9
   - **Audio:** AAC at 192 kb/s, stereo
   - **Output:** saved as `<name>_formatOK.mp4`
5. **Report**: write `format_report.txt` with the required format, a summary, the compliant films and each non-compliant film's issues. A count of the most common issues is printed to the terminal.

## Results

All five submitted films were non-compliant. After conversion, all five `_formatOK.mp4` versions pass every check (see [`format_report.txt`](format_report.txt)).

| Film | Problems found |
|---|---|
| Cosmos_War_of_the_Planets.mp4 | H.264 video, 628×354, 314:177 aspect, 29.97 FPS, 317 kb/s audio |
| Last_man_on_earth_1964.mov | ProRes video, 23.98 FPS, 9.29 Mb/s video, PCM audio at 1536 kb/s |
| The_Gun_and_the_Pulpit.avi | AVI container, raw video, 720×404, 180:101 aspect, 88 Mb/s video, PCM audio at 1536 kb/s |
| The_Hill_Gang_Rides_Again.mp4 | H.264 video, 7.54 Mb/s video |
| Voyage_to_the_Planet_of_Prehistoric_Women.mp4 | 29.97 FPS, 8.04 Mb/s video, MP3 audio at 320 kb/s |

## Running it

### Quick start (one command)

Run this command in the terminal. It downloads the project from GitHub into a temporary folder, downloads the five original films (about 290 MB) from the repository's release, and runs the checker:

```bash
D=$(mktemp -d) && gh repo clone Alizea2/ISP-Film-Format-Checker "$D" && cd "$D" && gh release download original-films -D Exercise3_Files && python3 "Exercise 3.py"
```

It takes about a minute:
- **Terminal:** shows each film's status and issues as it converts them, then the full report and the most common issues.
- **Output:** the report is saved as `format_report.txt`, and the converted films are written to `Exercise3_Files/`.

> This needs Python 3 and **FFmpeg with libx265** (`brew install ffmpeg`), plus the [GitHub CLI](https://cli.github.com/) (`gh`) signed in to an account that can access this repository. No extra Python packages are needed.
>
> The converted `_formatOK.mp4` files are already in the repository, so the checker also analyses them, which gives 10 films with 5 compliant, as in the submitted report. The original films are kept in a release because one of them (`The_Gun_and_the_Pulpit.avi`, 212 MB) is too large to store in a GitHub repository.

### Manual setup

Put the films in `Exercise3_Files/`, then run:

```bash
python3 "Exercise 3.py"
```

`Exercise 3.py` was exported from a Jupyter notebook. The `# In[n]:` markers show the original cells.

## Project Structure

| File / Folder | Purpose |
|---|---|
| `Exercise 3.py` | Probing, compliance checks, conversion, the report and the summary |
| `format_report.txt` | The generated compliance report |
| `Exercise3_Files/*_formatOK.mp4` | The five converted, compliant films |
| Release [`original-films`](https://github.com/Alizea2/ISP-Film-Format-Checker/releases/tag/original-films) | The five original submitted films |

## Built With

- Python 3 (standard library only: `subprocess`, `json`, `pathlib`)
- [FFmpeg / ffprobe](https://ffmpeg.org/) with libx265 (HEVC) and AAC

## Related exercises

- [ISP-Lossless-Audio-Compression](https://github.com/Alizea2/ISP-Lossless-Audio-Compression)
- [ISP-Audio-Effects-App](https://github.com/Alizea2/ISP-Audio-Effects-App)
- [ISP-Audio-Captcha-Voice-Control](https://github.com/Alizea2/ISP-Audio-Captcha-Voice-Control)
- [ISP-Audio-Steganography](https://github.com/Alizea2/ISP-Audio-Steganography)
- [ISP-Airport-Speech-Recognition](https://github.com/Alizea2/ISP-Airport-Speech-Recognition)

## Author

[@Alizea2](https://github.com/Alizea2)
