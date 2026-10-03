#!/usr/bin/env python
# coding: utf-8

# # EXERCISE 3

# ## This notebook creates a practical video format checking system for the Narbonne Online Film Festival. It automatically scans video files using ffprobe to read their technical details, such as codec type, resolution, frame rate, bitrate, and audio settings. Each video is then compared against the festival’s required specifications (MP4 container, HEVC video, AAC audio, 25 FPS, 640×360 resolution, and specific bitrate limits).
# 
# ## If a file does not meet the standards, the program automatically converts it using ffmpeg. Finally, it generates a clear text report summarising which films are compliant and which required corrections. The results show that half of the submitted videos needed reformatting.

# # Imports

# In[1]:


#Import libraries
import subprocess
import json
import os
from pathlib import Path
from datetime import datetime


# # Required Format Settings

# In[2]:


#Defining required format specifications
REQUIRED_FORMAT = {
    'container': 'mp4',
    'video_codec': 'hevc', 
    'audio_codec': 'aac',
    'frame_rate': 25.0,
    'aspect_ratio': '16:9',
    'width': 640,
    'height': 360,
    'video_bitrate_min': 2000000, 
    'video_bitrate_max': 5000000,  
    'audio_bitrate_max': 256000,   
    'audio_channels': 2  
}

#Setting the directory containing the video files
VIDEO_DIR = 'Exercise3_Files'
#Saving the final format report 
REPORT_FILE = 'format_report.txt'


# # Extract Video Information

# In[3]:


#extracting video information using ffprobe
def get_video_info(video_path):
 
    try:
        #building ffprobe command to get video info in json format
        cmd = [
            'ffprobe',
            '-v', 'quiet',         
            '-print_format', 'json',
            '-show_format',        
            '-show_streams',       
            video_path
        ]
        
        #running command
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        #converting json text to Python dictionary
        return json.loads(result.stdout)
    
    except subprocess.CalledProcessError as e:
        #if ffprobe fails
        print(f"Error probing {video_path}: {e}")
        return None

    except json.JSONDecodeError as e:
        #if json cannot be parsed
        print(f"Error parsing ffprobe output for {video_path}: {e}")
        return None


# # Helper Functions

# In[4]:


#returning aspect ratio in simplified form
def calculate_aspect_ratio(width, height):
    from math import gcd

    #finding common divisor to simplify ratio
    divisor = gcd(width, height)

    #returning simplified ratio as string
    return f"{width // divisor}:{height // divisor}"

#converting frame rate string to float.
def parse_frame_rate(frame_rate_str):
    #if frame rate is in fraction format
    if '/' in str(frame_rate_str):
        num, denom = map(float, frame_rate_str.split('/'))
        return num / denom 

    #convert directly to float
    return float(frame_rate_str)


# # Check Format Compliance

# In[5]:


#checking if a video matches the required format settings.
def check_format_compliance(video_path, video_info):
    #store any problems found
    issues = {}  
    
    #if video info could not be read
    if not video_info:
        return False, {'error': 'Could not read video information'}
    
    #extracting video and audio streams
    video_stream = None
    audio_stream = None
    
    for stream in video_info.get('streams', []):
        if stream.get('codec_type') == 'video' and not video_stream:
            video_stream = stream
        elif stream.get('codec_type') == 'audio' and not audio_stream:
            audio_stream = stream
    
    #checking container format 
    format_name = video_info.get('format', {}).get('format_name', '')
    if REQUIRED_FORMAT['container'] not in format_name:
        issues['container'] = f"Current: {format_name}, Required: {REQUIRED_FORMAT['container']}"
    
    #checking video stream
    if video_stream:

        #checking video codec
        video_codec = video_stream.get('codec_name', '')
        if video_codec != REQUIRED_FORMAT['video_codec']:
            issues['video_codec'] = f"Current: {video_codec}, Required: {REQUIRED_FORMAT['video_codec']}"
        
        #checking resolution
        width = video_stream.get('width', 0)
        height = video_stream.get('height', 0)
        if width != REQUIRED_FORMAT['width'] or height != REQUIRED_FORMAT['height']:
            issues['resolution'] = (
                f"Current: {width}x{height}, "
                f"Required: {REQUIRED_FORMAT['width']}x{REQUIRED_FORMAT['height']}"
            )
        
        #checking aspect ratio
        current_aspect = calculate_aspect_ratio(width, height)
        if current_aspect != REQUIRED_FORMAT['aspect_ratio']:
            issues['aspect_ratio'] = (
                f"Current: {current_aspect}, "
                f"Required: {REQUIRED_FORMAT['aspect_ratio']}"
            )
        
        #checking frame rate
        frame_rate_str = video_stream.get('r_frame_rate', '0/1')
        frame_rate = parse_frame_rate(frame_rate_str)
        if abs(frame_rate - REQUIRED_FORMAT['frame_rate']) > 0.1:
            issues['frame_rate'] = (
                f"Current: {frame_rate:.2f} FPS, "
                f"Required: {REQUIRED_FORMAT['frame_rate']} FPS"
            )
        
        #checking video bitrate
        video_bitrate = int(video_stream.get('bit_rate', 0))

        #if not found in stream then trying to get from format
        if video_bitrate == 0:
            video_bitrate = int(video_info.get('format', {}).get('bit_rate', 0))
        
        if video_bitrate > 0:
            if (video_bitrate < REQUIRED_FORMAT['video_bitrate_min'] or
                video_bitrate > REQUIRED_FORMAT['video_bitrate_max']):
                issues['video_bitrate'] = (
                    f"Current: {video_bitrate/1000000:.2f} Mb/s, "
                    f"Required: 2-5 Mb/s"
                )
    else:
        issues['video_stream'] = "No video stream found"
    
    #checking audio stream
    if audio_stream:

        #checking audio codec
        audio_codec = audio_stream.get('codec_name', '')
        if audio_codec != REQUIRED_FORMAT['audio_codec']:
            issues['audio_codec'] = f"Current: {audio_codec}, Required: {REQUIRED_FORMAT['audio_codec']}"
        
        #checking number of audio channels
        audio_channels = audio_stream.get('channels', 0)
        if audio_channels != REQUIRED_FORMAT['audio_channels']:
            issues['audio_channels'] = (
                f"Current: {audio_channels}, "
                f"Required: {REQUIRED_FORMAT['audio_channels']} (stereo)"
            )
        
        #checking audio bitrate
        audio_bitrate = int(audio_stream.get('bit_rate', 0))
        if audio_bitrate > REQUIRED_FORMAT['audio_bitrate_max']:
            issues['audio_bitrate'] = (
                f"Current: {audio_bitrate/1000:.0f} kb/s, "
                f"Required: up to 256 kb/s"
            )
    else:
        issues['audio_stream'] = "No audio stream found"
    
    #if no issues foundd then video is compliant
    is_compliant = len(issues) == 0

    return is_compliant, issues


# # Convert Non-Compliant Videos

# In[6]:


#converting a video file to the required format using ffmpeg
def convert_video(input_path, output_path):
    try:
        #building ffmpeg command with required settings
        cmd = [
            'ffmpeg',
            '-i', input_path,          
            '-y',                      
            '-c:v', 'libx265',         
            '-preset', 'medium',       
            '-b:v', '3500k',           
            '-s', '640x360',           
            '-r', '25',                
            '-aspect', '16:9',      
            '-c:a', 'aac',             
            '-b:a', '192k',            
            '-ac', '2',                
            '-f', 'mp4',               
            output_path
        ]
        
        #runing the ffmpeg command
        print(f"  Converting {os.path.basename(input_path)}...")
        subprocess.run(cmd, capture_output=True, text=True, check=True)

        print(f"  ✓ Successfully converted to {os.path.basename(output_path)}")
        return True
    
    except subprocess.CalledProcessError as e:
        #if ffmpeg fails
        print(f"  ✗ Error converting {input_path}: {e}")
        return False


# # Generate Report

# In[7]:


#creating a text file report showing which films meet the format requirements
def generate_report(results, report_path):
    #opening file for writing
    with open(report_path, 'w', encoding='utf-8') as f:

        #Report Header
        f.write("="*80 + "\n")
        f.write("NARBONNE ONLINE FILM FESTIVAL - FORMAT COMPLIANCE REPORT\n")
        f.write("="*80 + "\n\n")

        #writing current date and time
        f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        #Required Format Section
        f.write("REQUIRED FORMAT SPECIFICATIONS:\n")
        f.write("-" * 80 + "\n")
        f.write(f"  Container Format: {REQUIRED_FORMAT['container']}\n")
        f.write(f"  Video Codec: {REQUIRED_FORMAT['video_codec']} (h.265)\n")
        f.write(f"  Audio Codec: {REQUIRED_FORMAT['audio_codec']}\n")
        f.write(f"  Frame Rate: {REQUIRED_FORMAT['frame_rate']} FPS\n")
        f.write(f"  Aspect Ratio: {REQUIRED_FORMAT['aspect_ratio']}\n")
        f.write(f"  Resolution: {REQUIRED_FORMAT['width']}x{REQUIRED_FORMAT['height']}\n")
        f.write(f"  Video Bitrate: 2-5 Mb/s\n")
        f.write(f"  Audio Bitrate: up to 256 kb/s\n")
        f.write(f"  Audio Channels: {REQUIRED_FORMAT['audio_channels']} (stereo)\n\n")

        #Summary Section
        compliant_count = sum(1 for _, is_comp, _ in results if is_comp)
        non_compliant_count = len(results) - compliant_count

        f.write("SUMMARY:\n")
        f.write("-" * 80 + "\n")
        f.write(f"  Total Films Analyzed: {len(results)}\n")
        f.write(f"  Compliant Films: {compliant_count}\n")
        f.write(f"  Non-Compliant Films: {non_compliant_count}\n\n")

        #List Compliant Films
        if compliant_count > 0:
            f.write("COMPLIANT FILMS:\n")
            f.write("-" * 80 + "\n")
            for filename, is_compliant, _ in results:
                if is_compliant:
                    f.write(f"  ✓ {filename}\n")
            f.write("\n")

        #Listing Non Compliant Films
        if non_compliant_count > 0:
            f.write("NON-COMPLIANT FILMS AND ISSUES:\n")
            f.write("="*80 + "\n\n")

            for filename, is_compliant, issues in results:
                if not is_compliant:
                    f.write(f"Film: {filename}\n")
                    f.write("-" * 80 + "\n")
                    f.write("Problematic Fields:\n")

                    #writing each issue found
                    for field, description in issues.items():
                        f.write(f"  • {field.upper()}: {description}\n")

                    f.write("\n")

        #End of Report
        f.write("="*80 + "\n")
        f.write("END OF REPORT\n")
        f.write("="*80 + "\n")

    print(f"\nReport saved to: {report_path}")


# # Process All Videos

# In[8]:


#checking format compliance and converting non compliant files and generating a report
def process_video_files(video_dir, auto_convert=True):
    #supported video extensions
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
    video_files = []
    
    #checking if directory exists
    if os.path.isdir(video_dir):

        #collecting all video files in the folder
        for file in os.listdir(video_dir):
            if any(file.lower().endswith(ext) for ext in video_extensions):
                video_files.append(os.path.join(video_dir, file))
    else:
        print(f"Error: Directory '{video_dir}' not found!")
        return
    
    #if no videos found
    if not video_files:
        print(f"No video files found in '{video_dir}'")
        return
    
    print(f"Found {len(video_files)} video file(s) to process\n")
    print("="*80)
    
    #storing results for report
    results = []  
    
    #Process each video
    for video_path in video_files:
        filename = os.path.basename(video_path)

        print(f"\nAnalyzing: {filename}")
        print("-" * 80)
        
        #getting metadata using ffprobe
        video_info = get_video_info(video_path)
        
        #checking if video matches required format
        is_compliant, issues = check_format_compliance(video_path, video_info)
        
        #save result
        results.append((filename, is_compliant, issues))
        
        if is_compliant:
            print("Status: COMPLIANT - No conversion needed")
        else:
            print("Status: NON-COMPLIANT")
            print("\nIssues found:")

            #print all detected issues
            for field, description in issues.items():
                print(f"  • {field.upper()}: {description}")
            
            #convert automatically if enabled
            if auto_convert:
                name_without_ext = os.path.splitext(filename)[0]
                output_filename = f"{name_without_ext}_formatOK.mp4"
                output_path = os.path.join(video_dir, output_filename)
                
                print("\nStarting conversion...")
                success = convert_video(video_path, output_path)
                
                if success:
                    print("Conversion completed successfully")
    
    print("\n" + "="*80)
    print("PROCESSING COMPLETE")
    print("="*80)
    
    #generating final text report
    generate_report(results, REPORT_FILE)
    
    return results


# # Check FFmpeg Installation

# In[9]:


#checking if ffmpeg and ffprobe are installed
try:
    subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    subprocess.run(['ffprobe', '-version'], capture_output=True, check=True)
    print("ffmpeg and ffprobe are installed\n")
except (subprocess.CalledProcessError, FileNotFoundError):
    print("Error: ffmpeg and/or ffprobe not found!")


# # Run Processing

# In[10]:


#processing all videos in the specified directory
results = process_video_files(VIDEO_DIR, auto_convert=True)


# # Display Report

# In[11]:


#displaying the generated report
if os.path.exists(REPORT_FILE):
    print("\n" + "="*80)
    print("GENERATED REPORT CONTENT:")
    print("="*80 + "\n")
    with open(REPORT_FILE, 'r', encoding='utf-8') as f:
        print(f.read())
else:
    print(f"Report file '{REPORT_FILE}' not found.")


# # Summary Statistics

# In[12]:


#displaying summary statistics
if 'results' in locals():
    print("\n" + "="*80)
    print("DETAILED ANALYSIS SUMMARY")
    print("="*80 + "\n")
    
    #counting issues by type
    issue_counts = {}
    for filename, is_compliant, issues in results:
        for issue_type in issues.keys():
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
    
    if issue_counts:
        print("Most Common Issues:")
        print("-" * 80)
        for issue_type, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {issue_type.upper()}: {count} file(s)")
    else:
        print(" All files are compliant with the required format!")

