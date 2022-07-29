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

class PyaudioRecorder:
    def __init__(self, byte=2, channel=1, rate=8000, frame_per_sample=8000):
        _funcName = sys._getframe(0).f_code.co_name
        print(_funcName + ' in ' + __name__ + ' is start')
        self.byte = byte
        self.channel = channel
        self.rate = rate
        self.frame_per_sample = frame_per_sample
        self.recorder = pyaudio.PyAudio()
        self.record_queue = queue.Queue()
        self.stream = self.recorder.open(format=self.recorder.get_format_from_width(self.byte), channels=self.channel, rate=self.rate, input=True, frames_per_buffer=self.frame_per_sample)

        self._thread_evt_stop = threading.Event()   # default status is clear() = is_set() = False
        print('self._thread_evt_stop.is_set(): ' + str(self._thread_evt_stop.is_set()))
        self._thread_record = threading.Thread(target=self._thread_record, name='self._thread_record')
        print(_funcName + ' in ' + __name__ + ' is end')

    def __del__(self):
        _funcName = sys._getframe(0).f_code.co_name
        print(_funcName + ' in ' + __name__ + ' is start')
        if self._thread_record.is_alive:
            self._thread_evt_stop.set()
        self.stream.stop_stream()
        self.stream.close()
        self.recorder.terminate()
        print(_funcName + ' in ' + __name__ + ' is end')

    def get_stream(self):
        return self.stream

    def get_from_stream(self):
        return self.stream.read(self.frame_per_sample)   # wait until data is readable from stream

    def get_queue(self):
        return self.record_queue

    def get_from_queue(self):
        _data = []
        if not self._thread_record.is_alive():
            print('thread is not running')
        else:
            _qsize = self.record_queue.qsize()
            if _qsize != 0:
                for i in range(_qsize):
                    _data.append(self.record_queue.get())   # if queue is empty, queue.get() wait until not empty
            else:
                pass
        return _data

    def _thread_record(self):
        _funcName = sys._getframe(0).f_code.co_name
        print(_funcName + ' in ' + __name__ + ' is start')
        while True:
            _data = self.stream.read(self.frame_per_sample)  # wait until data is readable from stream
            self.record_queue.put(_data)
            if self._thread_evt_stop.is_set():
                print('self._thread_evt_stop.is_set(): ' + str(self._thread_evt_stop.is_set()))
                break
        print(_funcName + ' in ' + __name__ + ' is end')

    def run_thread(self):
        _funcName = sys._getframe(0).f_code.co_name
        print(_funcName + ' in ' + __name__ + ' is start')
        self._thread_record.start()
        print(_funcName + ' in ' + __name__ + ' is end')

    def stop_thread(self):
        _funcName = sys._getframe(0).f_code.co_name
        print(_funcName + ' in ' + __name__ + ' is start')
        if self._thread_record.is_alive():
            self._thread_evt_stop.set()
            print('wait close thread')
            self._thread_record.join()
            print('thread is closed')
        print(_funcName + ' in ' + __name__ + ' is end')

def main(argv):
    print(argv)
    HELP_MSG = '--file=record_test.pcm'

    _funcName = sys._getframe(0).f_code.co_name

    _rate = 8000
    _buffer_size = 8000
    _record_second =10

    _fileName = 'record_test.pcm'
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

    _recorder = PyaudioRecorder()

    """
    recording test from stream
    """
    print('record on stream in \'' + str(_record_second) + '\' sec')
    for _unit_time in range(0, int(_rate / _buffer_size * _record_second)):
        _data = _recorder.get_from_stream()
        _data_list.append(_data)
    print('_data_list length: ' + str(len(_data_list)))
    """
    save data, getting from stream, to file
    """
    _fileName_stream = _fileName + 'stream'
    print('write _data_list to \'' + _fileName_stream + '\'')
    with open(_fileName_stream, 'wb') as file:
        for _data in _data_list:
            file.write(_data)

    """
    recording test from thread(queue)
    """
    _recorder.run_thread()
    print('record just on thread in \'' + str(_record_second) + '\' sec')
    time.sleep(_record_second)
    time.sleep(1)

    _data_list = _recorder.get_from_queue()
    print('_data_list length: ' + str(len(_data_list)))

    _recorder.stop_thread()
    """
    save data, getting from thread(queue), to file
    """
    _fileName_thread = _fileName + 'thread'
    print('write _data_list to \'' + _fileName_thread + '\'')
    with open(_fileName_thread , 'wb') as file:
        for _data in _data_list:
            file.write(_data)

    print(_funcName + ' is end')

if __name__ == '__main__':
    main(sys.argv)
