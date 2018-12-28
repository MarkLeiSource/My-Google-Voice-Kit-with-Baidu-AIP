#-*- coding: utf-8 -*-

from aip import AipSpeech
import argparse
import time
import threading
import msgrouter
import os
from aiy.board import Board, Led
from aiy.voice.audio import AudioFormat, play_wav, record_file, Recorder

""" 你的 APPID AK SK """
APP_ID = 'your Baidu APP ID'
API_KEY = 'your Baidu API Key'
SECRET_KEY = 'your Baidu API secret key'
PATH = os.path.abspath('.')+'/'

def main():
    print(PATH)
    while True:
        try:
            parser = argparse.ArgumentParser()
            parser.add_argument('--filename', '-f', default='recording.wav')
            args = parser.parse_args()

            with Board() as board:
                print('Press button to start recording.')
                board.button.wait_for_press()
                board.led.state = Led.ON
                done = threading.Event()
                board.button.when_released = done.set

                def wait():
                    start = time.monotonic()
                    while not done.is_set():
                        duration = time.monotonic() - start
                        print('Recording: %.02f seconds [Press button to stop]' % duration)
                        time.sleep(0.5)
                    board.led.state = Led.OFF
                wavFmt = AudioFormat(sample_rate_hz=16000, num_channels=1, bytes_per_sample=2)
                record_file(wavFmt, filename=args.filename, wait=wait, filetype='wav')
                #print('Press button to end recording sound.')
                #board.button.wait_for_press()
                board.led.state = Led.PULSE_SLOW
                client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

                def get_file_content(filePath):
                    with open(filePath, 'rb') as fp:
                        return fp.read()

                # 识别本地文件
                r = client.asr(get_file_content(PATH+args.filename), 'wav', 16000, {
                    'dev_pid': 1536,
                })
                print(r)
                msg = r['result'][0]
                answer = msgrouter.getAnswer(msg)
                if answer.strip() == '':
                    raise RuntimeError('no answer')
                result  = client.synthesis(answer, 'zh', 1, {
                    'vol': 1,
                    'aue' : 6,
                    'per': 4
                })

                # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
                if not isinstance(result, dict):
                    with open(PATH+'answer.wav', 'wb') as f:
                        f.write(result)
                print('Playing...')
                board.led.state = Led.BLINK
                play_wav(PATH+'answer.wav')
                board.led.state = Led.OFF
                print('Done.')
        except BaseException as e:
            print(e.message)

if __name__ == '__main__':
    main()


