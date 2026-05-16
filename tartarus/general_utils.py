"""
@title

@description

"""
import base64
import binascii
import json
import logging
import math
import ssl
import threading
import time
from datetime import datetime
from io import BytesIO
from zoneinfo import ZoneInfo

from skill_evolution import TERMINAL_COLUMNS, timezone


def display_progress(category_tag, num_complete, total_jobs, time_elapsed, time_since, initial_bar=False):
    avg_time = time_elapsed / num_complete if num_complete > 0 else math.inf
    time_remaining = avg_time * (total_jobs - num_complete)
    sep = '' if initial_bar else '\r'
    end = '' if num_complete != total_jobs else '\n'
    log_message = (
        f'{sep}\t[{time_tag(timezone)}:{category_tag}] '
        f'Completed: {num_complete}/{total_jobs} ({(num_complete / total_jobs) * 100:0.2f}%) | '
        f'{time_elapsed=:0.2f} | {avg_time=:0.2f} | {time_remaining=:0.2f} | {time_since=:0.2f}        '
    )
    print(log_message, end=end, flush=True)
    return


def batch_iterable(iterable, n=10):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


def filter_dict(data, pass_keys):
    if isinstance(data, str):
        data = json.loads(data)

    filtered_data = {
        field_name: field_val
        for field_name, field_val in data.items()
        if field_name in pass_keys
    }
    return filtered_data


def time_tag(tz_str='GMT'):
    time_zone = ZoneInfo(tz_str)
    curr_time = time.time()
    date_time = datetime.fromtimestamp(curr_time, tz=time_zone)
    time_str = date_time.strftime("%Y-%m-%d-%H-%M-%S")
    return time_str


def run_with_retry(command_func, num_attempts=5, raise_error=False, verbose=False, func_tag=None):
    result_info = None
    failures = []
    for attempt_num in range(num_attempts):
        try:
            result_info = command_func()
            break
        except ssl.SSLEOFError as e:
            failures.append(e)
            delay = 2 ** attempt_num
            if verbose:
                err_message = (
                    f'Attempt {attempt_num + 1} failed with SSL EOF error. Retrying in {delay} seconds:\n'
                    f'\t{e}\n'
                    f'{'=' * TERMINAL_COLUMNS}'
                )
                logging.warning(err_message)
            time.sleep(2 ** delay)
        except Exception as e:
            failures.append(e)
            delay = 2 ** attempt_num
            if verbose:
                err_message = (
                    f'Waiting {delay} seconds before retrying due to error:\n'
                    f'\t{e}\n'
                    f'{'=' * TERMINAL_COLUMNS}'
                )
                logging.warning(err_message)
            time.sleep(delay)
    else:
        if func_tag is None:
            func_tag = command_func.__name__
        failure_message = f'Failed to execute command `{func_tag}` after {num_attempts} attempts: {failures[-1]}'
        if raise_error:
            raise RuntimeError(failure_message)
        elif verbose:
            logging.error(failure_message)
    return {'results': result_info, 'failures': failures}


def get_open_threads(thread_prefix):
    open_threads = [
        each_thread
        for each_thread in threading.enumerate()
        if each_thread.name.startswith(thread_prefix)
    ]
    return open_threads


def wait_for_threads(save_data_thread_prefix):
    open_threads = get_open_threads(save_data_thread_prefix)
    logging.info(f'[{time_tag()}] Open threads: {len(open_threads)=}')
    while len(open_threads) > 0:
        logging.info(f'[{time_tag()}] Open threads: {len(open_threads)=}')
        time.sleep(1)
        open_threads = get_open_threads(save_data_thread_prefix)
    return


def preprocess_pdf_to_str(pdf_content):
    pdf_data = base64.b64encode(pdf_content).decode('utf-8')
    return pdf_data


def encode_image_to_str(image, image_format):
    buffered = BytesIO()
    image.save(buffered, format=image_format)
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str


def base64_image_type(encoded_image) -> str | None:
    """
    Detects the MIME type of a base64 encoded image by inspecting its header bytes (magic numbers).
    Supports PNG, JPEG, GIF, and WebP.

    Args:
        encoded_image: The base64 string (with or without 'data:image/...;base64,' prefix).

    Returns:
        str: MIME type (e.g., 'image/png') or None if unknown/invalid.
    """
    if "base64," in encoded_image[:30]:
        encoded_image = encoded_image.split("base64,")[1]

    # 2. Decode the first 12 bytes (enough for most image signatures)
    try:
        # We only need the beginning of the file to identify it
        header_bytes = base64.b64decode(encoded_image[:24])
    except (binascii.Error, ValueError):
        return None

    # 3. Check for Magic Numbers
    # PNG: 89 50 4E 47 0D 0A 1A 0A
    if header_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'

    # JPEG: FF D8 FF
    if header_bytes.startswith(b'\xff\xd8\xff'):
        return 'jpeg'

    # GIF: "GIF87a" or "GIF89a"
    if header_bytes[:6] in [b'GIF87a', b'GIF89a']:
        return 'gif'

    # WebP: RIFF....WEBP
    # Bytes 0-3 are 'RIFF', bytes 8-11 are 'WEBP'
    if header_bytes.startswith(b'RIFF') and header_bytes[8:12] == b'WEBP':
        return 'webp'

    return None


def is_base64(base64_str):
    try:
        base64.b64decode(base64_str)
        return True
    except Exception:
        return False
