import os
import time
import json
import shlex
import asyncio
import mimetypes
from decimal import Decimal
from datetime import timedelta

# https://stackoverflow.com/a/49361727
def format_bytes(size):
    size = int(size)
    # 2**10 = 1024
    power = 1024
    n = 0
    power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]+'B'}"

async def get_file_mimetype(filename):
    mimetype = mimetypes.guess_type(filename)[0]
    if not mimetype:
        proc = await asyncio.create_subprocess_exec('file', '--brief', '--mime-type', filename, stdout=asyncio.subprocess.PIPE)
        stdout, _ = await proc.communicate()
        mimetype = stdout.decode().strip()
    return mimetype or ''

async def split_files(filename, destination_dir, no_ffmpeg=False):
    ext = os.path.splitext(filename)[1]
    if not no_ffmpeg and (await get_file_mimetype(filename)).startswith('video/'):
        video_info = (await get_video_info(filename))['format']
        if 'duration' in video_info:
            times = 1
            ss = Decimal('0.0')
            duration = Decimal(video_info['duration'])
            files = []
            while duration - ss > 1:
                filepath = os.path.join(destination_dir, os.path.splitext(os.path.basename(filename))[0][-(248-len(ext)):] + ('-' if ext else '.') + 'part' + str(times) + ext)
                proc = await asyncio.create_subprocess_exec('ffmpeg', '-y', '-i', filename, '-ss', str(ss), '-c', 'copy', '-fs', '1900000000', filepath)
                await proc.communicate()
                video_info = (await get_video_info(filepath)).get('format')
                if not video_info:
                    break
                if 'duration' not in video_info:
                    break
                files.append(filepath)
                times += 1
                ss += Decimal(video_info['duration'])
            return files
    args = ['split', '--verbose', '--numeric-suffixes=1', '--bytes=2097152000', '--suffix-length=2']
    if ext:
        args.append(f'--additional-suffix={ext}')
    args.append(filename)
    args.append(os.path.join(destination_dir, os.path.basename(filename)[-(248-len(ext)):] + ('-' if ext else '.') + 'part'))
    proc = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE)
    stdout, _ = await proc.communicate()
    return shlex.split(' '.join([i[14:] for i in stdout.decode().strip().split('\n')]))

async def get_video_info(filename):
    proc = await asyncio.create_subprocess_exec('ffprobe', '-print_format', 'json', '-show_format', '-show_streams', filename, stdout=asyncio.subprocess.PIPE)
    stdout, _ = await proc.communicate()
    return json.loads(stdout)

async def generate_thumbnail(videopath, photopath):
    video_info = await get_video_info(videopath)
    for duration in (10, 5, 0):
        if duration < float(video_info['format']['duration']):
            proc = await asyncio.create_subprocess_exec('ffmpeg', '-y', '-i', videopath, '-ss', str(duration), '-frames:v', '1', photopath)
            await proc.communicate()
            break

async def convert_to_jpg(original, end):
    proc = await asyncio.create_subprocess_exec('ffmpeg', '-y', '-i', original, end)
    await proc.communicate()

# https://stackoverflow.com/a/34325723
def return_progress_string(current, total):
    if total:
        filled_length = int(30 * current // total)
    else:
        filled_length = 0
    return '[' + '=' * filled_length + ' ' * (30 - filled_length) + ']'

# https://stackoverflow.com/a/852718
# https://stackoverflow.com/a/775095
def calculate_eta(current, total, start_time):
    if not current:
        return '00:00:00'
    end_time = time.time()
    elapsed_time = end_time - start_time
    seconds = (elapsed_time * (total / current)) - elapsed_time
    thing = ''.join(str(timedelta(seconds=seconds)).split('.')[:-1]).split(', ')
    thing[-1] = thing[-1].rjust(8, '0')
    return ', '.join(thing)

# https://stackoverflow.com/a/10920872
async def watermark_photo(main, overlay, out):
    proc = await asyncio.create_subprocess_exec('ffmpeg', '-y', '-i', main, '-i', overlay, '-filter_complex', 'overlay=(main_w-overlay_w)/2:(main_h-overlay_h)', out)
    await proc.communicate()
