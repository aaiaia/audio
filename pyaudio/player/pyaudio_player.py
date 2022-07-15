# for system
import sys
import threading
from pathlib import Path
import time
# for data type
import queue
# for audio
import pyaudio
# for Debugging
import getopt

class PyaudioPlayer:
    def __init__(self, byte=2, channel=1, rate=8000):
        _funcName = sys._getframe(0).f_code.co_name
        print(_funcName + ' in ' + __name__ + ' is start')
        self.byte = byte
        self.channel = channel
        self.rate = rate
        self.player = pyaudio.PyAudio()
        self.play_queue = queue.Queue()
        self.stream = self.player.open(format=self.player.get_format_from_width(self.byte), channels=self.channel, rate=self.rate, output=True)

        self._thread_play = threading.Thread(target=self._thread_play, name='self._thread_play')
        print(_funcName + ' in ' + __name__ + ' is end')

    def __del__(self):
        _funcName = sys._getframe(0).f_code.co_name
        print(_funcName + ' in ' + __name__ + ' is start')
        if self._thread_play.is_alive():
            self.play_queue.put(None)
        self.stream.stop_stream()
        self.stream.close()
        self.player.terminate()
        print(_funcName + ' in ' + __name__ + ' is end')

    def get_stream(self):
        return self.stream

    def put_to_stream(self, raw_data):
        self.stream.write(raw_data) # wait until data is writable to stream

    def get_queue(self):
        return self.play_queue

    def put_to_queue(self, raw_data):
        if not self._thread_play.is_alive():
            print('thread is not running')
        else:
            self.play_queue.put(raw_data)

    def _thread_play(self):
        _funcName = sys._getframe(0).f_code.co_name
        print(_funcName + ' in ' + __name__ + ' is start')
        while True:
            _data = self.play_queue.get()
            if _data == None:
                print(_funcName + ' detects \'' + str(_data) + '\', will be closed')
                break
            self.stream.write(_data)    # wait until data is writable to stream
        print(_funcName + ' in ' + __name__ + ' is end')

    def run_thread(self):
        _funcName = sys._getframe(0).f_code.co_name
        print(_funcName + ' in ' + __name__ + ' is start')
        self._thread_play.start()
        print(_funcName + ' in ' + __name__ + ' is end')

    def stop_thread(self):
        _funcName = sys._getframe(0).f_code.co_name
        print(_funcName + ' in ' + __name__ + ' is start')
        if self._thread_play.is_alive():
            self.play_queue.put(None)
            print('wait close thread')
            self._thread_play.join()
            print('thread is closed')
        print(_funcName + ' in ' + __name__ + ' is end')

def main(argv):
    print(argv)
    HELP_MSG = '--file=sample.pcm'

    _funcName = sys._getframe(0).f_code.co_name

    _fileName = 'sample.pcm'
    _data_list = []

    try:
        # opts: getopt 옵션에 따라 파싱 ex) [('-i', 'myinstancce1')]
        # etc_args: getopt 옵션 이외에 입력된 일반 Argument
        # argv 첫번째(index:0)는 파일명, 두번째(index:1)부터 Arguments
        opts, etc_args = getopt.getopt(argv[1:], \
            "hf:", ["help", "file="])
    except getopt.GetoptError: # 옵션지정이 올바르지 않은 경우
        print(HELP_MSG)
        sys.exit(2)

    for opt, arg in opts: # 옵션이 파싱된 경우
        if opt in ("-h", "--help"): # HELP 요청인 경우 사용법 출력
            print(HELP_MSG)
            sys.exit(2)
        elif opt in ("-f", "--file"):
            _fileName = arg
            print('set _fileName: ' + _fileName)

    """
    load raw data from file
    """
    if Path(_fileName).exists:
        if Path(_fileName).is_file():
            with open(_fileName, 'rb') as file:
                for block in iter(lambda: file.read(8000), b''):
                    _data_list.append(block)
            print('loaded length of _data_list: ' + str(len(_data_list)))
        else:
            print('is it file?: \'' + _fileName + '\'')
            sys.exit(2)
    else:
        print('file is not exist: \'' + _fileName + '\'')
        sys.exit(2)

    _player = PyaudioPlayer()

    """
    playing test to stream
    """
    print('play just on stream')
    for _data in _data_list:
        _player.put_to_stream(_data)
        print(time.localtime())

    """
    playing test to thread(queue)
    """
    print('play on thread')
    _player.run_thread()
    for _data in _data_list:
        _player.put_to_queue(_data)
        print(time.localtime())
    _player.stop_thread()

    print(_funcName + ' is end')

if __name__ == '__main__':
    main(sys.argv)
