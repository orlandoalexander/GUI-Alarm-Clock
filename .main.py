import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
import time
import threading
from kivy.clock import Clock
from pydub import AudioSegment
from pydub.playback import play
import osascript

Window.size = (600, 400)

class WindowManager(ScreenManager):  # class used for transitions between windows
    pass

class HomeScreen(Screen):
    def on_press(self):
        self.ids.red_button.source = "RedButton_darker.png"
        timedisplay_current_instance = App.get_running_app().root.get_screen('timedisplay') #stores the instance of the class Display that is currently running on the GUI (so the current screen is updated)
        Clock.schedule_interval(timedisplay_current_instance.display_time, 1) #calls the method 'display_time' in the class 'TimeDisplay' every second using Kivy Clock
    def on_release(self):
        time.sleep(0.1)
        self.ids.red_button.source = "RedButton.png"

class TimeDisplay(Screen):
    def display_time(self, *args):
        self.ids.alarm.source = "AlarmClock.png" #by loading the alarm clock image source here, rather than in the kivy file, it ensures the image loads at the same time as the time text
        self.ids.alarm.opacity = 1
        self.ids.alarm_label.opacity = 1
        self.current_time = time.strftime("%H:%M:%S") #provides local time as a structure format of hours followed by minutes and seconds
        self.ids.time.text = str(self.current_time)
    def on_press(self):
        self.ids.alarm.source = "AlarmClock_darker.png"
    def on_release(self):
        time.sleep(0.1)
        self.ids.alarm.source = "AlarmClock.png"

class AlarmDisplay(Screen):
    try:
        alarmdisplay_previous_instance = App.get_running_app().root.get_screen('alarmring')
        current_alarm_time = alarmdisplay_previous_instance.get_previous_alarm_time()
    except:
        current_alarm_time = [12,0]
    def up_left_button(self):
        self.alarm_time("up", "hour")
    def up_right_button(self):
        self.alarm_time("up", "min")
    def down_right_button(self):
        self.alarm_time("down", "min")
    def down_left_button(self):
        self.alarm_time("down", "hour")
    def alarm_time(self, direction, time):
        try:
            self.alarm_time_change +=1
        except:
            self.alarm_time_change = 0
        if direction == "up" and time == "hour":
            if self.current_alarm_time[0] != 23:
                self.current_alarm_time[0] += 1
            else:
                self.current_alarm_time[0] = 00
        elif direction == "down" and time == "hour":
            if self.current_alarm_time[0] != 0:
                self.current_alarm_time[0] -= 1
            else:
                self.current_alarm_time[0] = 23
        elif direction == "up" and time == "min":
            if self.current_alarm_time[1] != 59:
                self.current_alarm_time[1] += 1
            else:
                self.current_alarm_time[1] = 00
        elif direction == "down" and time == "min":
            if self.current_alarm_time[1] != 0:
                self.current_alarm_time[1] -= 1
            else:
                self.current_alarm_time[1] = 59
        self.display_alarm_time()
    def on_press_set(self):
        self.thread_stop = True
        self.ids.alarm_set.source = "AlarmSetButton_darker.png"
        alarm = App.get_running_app().root.get_screen('alarmring')
        try:
            self.alarm_thread.join()
            self.alarm_thread = threading.Thread(target=alarm.alarm_ring, args=(),daemon=False)  # initialises an instance of Thread. As 'daemon = True', this thread will run in the background until the program terminates (or until it finishes running).
            self.thread_stop = False
            self.alarm_thread.start()
        except:
            self.alarm_thread = threading.Thread(target=alarm.alarm_ring, args=(), daemon=False)  # initialises an instance of Thread. As 'daemon = True', this thread will run in the background until the program terminates (or until it finishes running).
            self.thread_stop = False
            self.alarm_thread.start()
    def on_release_set(self):
        time.sleep(0.1)
        timedisplay_current_instance = App.get_running_app().root.get_screen('timedisplay')
        timedisplay_current_instance.ids.alarm_label.text = "Alarm On"
        self.ids.alarm_set.source = "AlarmSetButton.png"
    def on_press_off(self):
        self.thread_stop = True
        self.ids.alarm_off.source = "BlueButton_darker.png"
        try:
            self.previous_alarm_time = self.current_alarm_time_string
        except:
            self.previous_alarm_time = "12:00"
        self.current_alarm_time_string = "Off"
        alarm = App.get_running_app().root.get_screen('alarmring')
        try:
            self.alarm_thread.join()
            self.alarm_thread = threading.Thread(target=alarm.alarm_ring, args=(), daemon=False)  # initialises an instance of Thread. As 'daemon = True', this thread will run in the background until the program terminates (or until it finishes running).
            self.thread_stop = False
            self.alarm_thread.start()
        except:
            self.alarm_thread = threading.Thread(target=alarm.alarm_ring, args=(), daemon=False)  # initialises an instance of Thread. As 'daemon = True', this thread will run in the background until the program terminates (or until it finishes running).
            self.thread_stop = False
            self.alarm_thread.start()
    def on_release_off(self):
        time.sleep(0.1)
        timedisplay_current_instance = App.get_running_app().root.get_screen('timedisplay')
        timedisplay_current_instance.ids.alarm_label.text = "Alarm Off"
        self.ids.alarm_off.source = "BlueButton.png"
        self.current_alarm_time_string = self.previous_alarm_time

    def display_alarm_time(self):
        self.current_alarm_time_string = ["",""]
        for i in range(0, 2):
            if len(str(self.current_alarm_time[i])) < 2:
                self.current_alarm_time_string[i] = "0"+str(self.current_alarm_time[i])
            else:
                self.current_alarm_time_string[i] = str(self.current_alarm_time[i])
        self.current_alarm_time_string = (":".join(self.current_alarm_time_string))
        self.ids.alarm_time.text = self.current_alarm_time_string
    def get_alarm_time(self):
        try:
            return self.current_alarm_time_string
        except:
            return "12:00"
    def get_thread_stop(self):
        return self.thread_stop



class Alarm(Screen):
    def alarm_ring(self):
        alarm_current_instance = App.get_running_app().root.get_screen('alarmdisplay')
        self.alarm_time = alarm_current_instance.get_alarm_time()
        while True:
            if alarm_current_instance.get_thread_stop() == True:
                break
            elif self.alarm_time == time.strftime("%H:%M"):
                self.stop_loop = False
                self.alarm_thread = threading.Thread(target=self.alarm_audio, args=(),daemon=False)  # initialises an instance of Thread. As 'daemon = True', this thread will run in the background until the program terminates (or until it finishes running).
                self.alarm_thread.start()
                self.alarm_image()
                break
    def alarm_image(self):
        alarm_ring_current_instance = App.get_running_app().root.get_screen('alarmring')
        counter = 0
        while counter < 300:
            counter += 1
            if self.stop_loop == True:
                App.get_running_app().root.current = "timedisplay"
                break
            App.get_running_app().root.current = "alarmring"
            alarm_ring_current_instance.ids.Baldwin.opacity = 1
            time.sleep(0.5)
            alarm_ring_current_instance.ids.Baldwin.opacity = 0
            time.sleep(0.5)
    def get_previous_alarm_time(self):
        return self.alarm_time
    def on_press(self):
        code, out, err = osascript.run("output volume of (get volume settings)")
        self.previous_volume = out
        osascript.osascript("set volume output volume 0")
        self.stop_loop = True
        timedisplay_current_instance = App.get_running_app().root.get_screen('timedisplay')
        timedisplay_current_instance.ids.alarm_label.text = "Alarm Off"
    def alarm_audio(self):
        counter = 0
        while counter < 25:
            counter +=1
            sound = AudioSegment.from_wav('AlarmAudio.wav')
            if self.stop_loop == True:
                osascript.osascript("set volume output volume "+self.previous_volume)
                break
            play(sound)


class MyApp(App):
    def build(self):
        layout = Builder.load_file("layout.kv")  # loads the kv file
        return layout


if __name__ == "__main__":
    MyApp().run()
